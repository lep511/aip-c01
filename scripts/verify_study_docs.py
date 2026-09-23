"""Verificador de los materiales de estudio de `study/`.

Comprueba cinco contratos sobre los archivos Markdown de un directorio:

1. **URLs oficiales de AWS.** Toda URL `https://docs.aws.amazon.com/.../pagina.html`
   citada existe. Se consulta la variante `.md` de la pagina, que devuelve 404 real
   cuando la pagina no existe. El HTML, en cambio, responde 200 con un shell generico
   de ~2.257 bytes incluso para paginas inexistentes, asi que no sirve como oraculo.
2. **Enlaces relativos.** Todo enlace `./archivo.md` o `../domain-1/archivo.md#ancla`
   apunta a un archivo que existe, y el fragmento corresponde a un heading real.
3. **Bloques de codigo.** Ningun bloque esta marcado como `powershell` ni `bash`:
   la convencion del repositorio es Python.
4. **Cobertura de skills.** Cada `task-N-M-*.md` contiene como heading todos los
   identificadores de skill que declara en su linea `Skills cubiertos:`.
5. **Inventario completo.** Si el directorio tiene `referencias-oficiales.md`, toda
   URL oficial citada en sus archivos hermanos aparece en el inventario.

Uso:

    uv run python scripts/verify_study_docs.py study
    uv run python scripts/verify_study_docs.py study/domain-3 --no-network
"""

from __future__ import annotations

import argparse
import re
import sys
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# El oraculo fiable es el 404 de la variante .md. El umbral de bytes solo atrapa
# respuestas vacias: hay paginas legitimas muy cortas (por ejemplo las que avisan
# de que su contenido se movio a otra pagina), y un umbral alto las marcaria como
# inexistentes.
MIN_BODY_BYTES = 100

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)
TIMEOUT_SECONDS = 30
# docs.aws.amazon.com corta conexiones con demasiada concurrencia y se
# manifiesta como SSLError, no como 404. Seis hilos con reintentos es el
# equilibrio que aguanta un inventario de varios cientos de URLs.
MAX_WORKERS = 6
MAX_RETRIES = 4

AWS_DOC_URL = re.compile(r"https://docs\.aws\.amazon\.com/[^\s<>\"')\]]+")
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
INLINE_CODE = re.compile(r"`+[^`]*`+")
FENCE = re.compile(r"^\s{0,3}(?:`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)", re.MULTILINE)
ATX_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)
SKILLS_COVERED = re.compile(r"^Skills cubiertos:\s*(.+)$", re.MULTILINE)
SKILL_ID = re.compile(r"\b(\d+\.\d+\.\d+)\b")
FORBIDDEN_LANGS = {"powershell", "posh", "pwsh", "ps1", "bash", "sh", "shell", "zsh"}


@dataclass
class Findings:
    """Problemas acumulados durante la verificacion."""

    errors: list[str] = field(default_factory=list)
    checked_urls: int = 0
    checked_links: int = 0
    checked_files: int = 0

    def fail(self, path: Path, message: str) -> None:
        self.errors.append(f"{path}: {message}")


def slugify_heading(text: str) -> str:
    """Traduce un heading a su ancla de GitHub.

    Se elimina el formato inline, se pasa a minusculas, se descartan los caracteres
    que no sean alfanumericos, guion, subrayado o espacio, y los espacios pasan a
    guiones. Los acentos se conservan, igual que hace GitHub.
    """
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = unicodedata.normalize("NFC", text).strip().lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in {"-", "_", " "})
    # GitHub sustituye cada espacio por un guion, no los grupos de espacios. Un
    # heading como "Skill 2.1.7 — Frameworks" deja dos espacios al caer la raya y
    # produce "skill-217--frameworks".
    return re.sub(r"\s", "-", text.strip())


def strip_code_blocks(text: str) -> str:
    """Devuelve el texto sin el contenido de los bloques de codigo cercados."""
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                continue
            out.append(line)
        elif stripped.startswith(fence):
            fence = None
    return "\n".join(out)


def strip_inline_code(text: str) -> str:
    """Neutraliza los code spans en linea.

    Un patron como `[a-zA-Z0-9](-*[a-zA-Z0-9])` dentro de backticks tiene la
    forma de un enlace Markdown sin serlo, asi que se descarta antes de buscar
    enlaces. Se conserva la longitud aproximada sustituyendo por espacios.
    """
    return INLINE_CODE.sub(lambda match: " " * len(match.group(0)), text)


def headings_of(path: Path) -> set[str]:
    """Anclas disponibles en un archivo Markdown."""
    if not path.is_file():
        return set()
    body = strip_code_blocks(path.read_text(encoding="utf-8"))
    return {slugify_heading(title) for _, title in ATX_HEADING.findall(body)}


def markdown_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def normalize_doc_url(url: str) -> str:
    """Quita el fragmento y la puntuacion final que arrastra el parseo."""
    url = url.split("#", 1)[0].rstrip(".,;:")
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


_local = threading.local()


def session() -> requests.Session:
    """Sesion HTTP por hilo, con reintentos y backoff.

    Reutilizar la conexion y reintentar ante corte es imprescindible: el
    servidor rechaza rafagas y devuelve errores de transporte que no tienen
    nada que ver con que la pagina exista.
    """
    existing = getattr(_local, "session", None)
    if existing is not None:
        return existing

    retry = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        status=MAX_RETRIES,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    created = requests.Session()
    created.headers["User-Agent"] = USER_AGENT
    adapter = HTTPAdapter(max_retries=retry, pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS)
    created.mount("https://", adapter)
    _local.session = created
    return created


def probe_url(url: str) -> str | None:
    """Devuelve un mensaje de error si la pagina no existe, o None si esta bien."""
    target = f"{url[: -len('.html')]}.md" if url.endswith(".html") else url
    last_error: Exception | None = None

    # Los cortes de transporte se reintentan tambien aqui, porque urllib3 no
    # reintenta un SSLError que ocurre a mitad del handshake.
    for _ in range(MAX_RETRIES):
        try:
            response = session().get(target, timeout=TIMEOUT_SECONDS)
            break
        except requests.RequestException as exc:
            last_error = exc
    else:
        return f"no se pudo comprobar {url} ({type(last_error).__name__})"
    if response.status_code == 404:
        return f"404 en {url} (probado {target})"
    if response.status_code != 200:
        return f"HTTP {response.status_code} en {url} (probado {target})"
    if len(response.content) < MIN_BODY_BYTES:
        return (
            f"cuerpo de {len(response.content)} bytes en {url}: "
            "parece el shell generico de una pagina inexistente"
        )
    return None


def check_aws_urls(files: list[Path], findings: Findings) -> None:
    """Comprueba que toda URL de docs.aws.amazon.com citada existe."""
    by_url: dict[str, set[Path]] = {}
    for path in files:
        body = path.read_text(encoding="utf-8")
        for raw in AWS_DOC_URL.findall(body):
            url = normalize_doc_url(raw)
            if url.endswith(".html") or "/toc-contents.json" in url:
                by_url.setdefault(url, set()).add(path)

    findings.checked_urls = len(by_url)
    if not by_url:
        return

    urls = sorted(by_url)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for url, error in zip(urls, pool.map(probe_url, urls)):
            if error:
                for path in sorted(by_url[url]):
                    findings.fail(path, error)


def check_relative_links(root: Path, files: list[Path], findings: Findings) -> None:
    """Comprueba que los enlaces relativos y sus anclas resuelven."""
    anchor_cache: dict[Path, set[str]] = {}

    for path in files:
        body = strip_inline_code(strip_code_blocks(path.read_text(encoding="utf-8")))
        for target in MARKDOWN_LINK.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            findings.checked_links += 1

            if target.startswith("#"):
                anchor = target[1:].lower()
                anchors = anchor_cache.setdefault(path, headings_of(path))
                if anchor and anchor not in anchors:
                    findings.fail(path, f"ancla interna inexistente: #{anchor}")
                continue

            file_part, _, fragment = target.partition("#")
            resolved = (path.parent / file_part).resolve()
            if not resolved.is_file():
                findings.fail(path, f"enlace roto: {target}")
                continue
            if fragment:
                anchors = anchor_cache.setdefault(resolved, headings_of(resolved))
                if fragment.lower() not in anchors:
                    rel = resolved.relative_to(root.resolve()) if root in resolved.parents else resolved
                    findings.fail(path, f"ancla inexistente en {rel}: #{fragment}")


def check_code_fences(files: list[Path], findings: Findings) -> None:
    """Comprueba que no hay bloques de codigo de shell."""
    for path in files:
        for lang in FENCE.findall(path.read_text(encoding="utf-8")):
            if lang.lower() in FORBIDDEN_LANGS:
                findings.fail(
                    path,
                    f"bloque de codigo `{lang}`: la convencion del repositorio es Python",
                )


def check_reference_inventory(files: list[Path], findings: Findings) -> None:
    """Comprueba que el inventario de referencias no deja fuera ninguna URL.

    Si un directorio tiene `referencias-oficiales.md`, toda URL de
    docs.aws.amazon.com citada en sus archivos hermanos debe aparecer tambien
    en el inventario. De lo contrario, el documento auditable esta incompleto.
    """
    inventories = {p.parent: p for p in files if p.name == "referencias-oficiales.md"}
    if not inventories:
        return

    for directory, inventory in inventories.items():
        listed = {
            normalize_doc_url(raw)
            for raw in AWS_DOC_URL.findall(inventory.read_text(encoding="utf-8"))
        }
        for path in files:
            if path.parent != directory or path == inventory:
                continue
            for raw in AWS_DOC_URL.findall(path.read_text(encoding="utf-8")):
                url = normalize_doc_url(raw)
                if url.endswith(".html") and url not in listed:
                    findings.fail(
                        inventory,
                        f"falta en el inventario: {url} (citada en {path.name})",
                    )


def check_skill_coverage(files: list[Path], findings: Findings) -> None:
    """Comprueba que cada task documenta como heading los skills que declara."""
    for path in files:
        if not re.match(r"task-\d+-\d+-", path.name):
            continue
        body = path.read_text(encoding="utf-8")
        declared = SKILLS_COVERED.search(body)
        if not declared:
            findings.fail(path, "falta la linea 'Skills cubiertos:'")
            continue

        expected = SKILL_ID.findall(declared.group(1))
        if not expected:
            findings.fail(path, "la linea 'Skills cubiertos:' no declara ningun skill")
            continue

        documented = {
            skill
            for _, title in ATX_HEADING.findall(body)
            for skill in SKILL_ID.findall(title)
        }
        for skill in expected:
            if skill not in documented:
                findings.fail(path, f"el skill {skill} no tiene heading propio")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="directorio a verificar, por ejemplo study/domain-3")
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="omite la comprobacion de URLs de docs.aws.amazon.com",
    )
    args = parser.parse_args()

    root = args.path
    if not root.is_dir():
        print(f"error: {root} no es un directorio", file=sys.stderr)
        return 2

    files = markdown_files(root)
    if not files:
        print(f"error: no hay archivos .md en {root}", file=sys.stderr)
        return 2

    findings = Findings(checked_files=len(files))
    check_code_fences(files, findings)
    check_skill_coverage(files, findings)
    check_reference_inventory(files, findings)
    check_relative_links(root, files, findings)
    if args.no_network:
        print("Comprobacion de URLs omitida (--no-network).")
    else:
        check_aws_urls(files, findings)

    print(
        f"Revisados {findings.checked_files} archivos, "
        f"{findings.checked_links} enlaces relativos, "
        f"{findings.checked_urls} URLs de docs.aws.amazon.com."
    )
    if findings.errors:
        print(f"\n{len(findings.errors)} problema(s):\n", file=sys.stderr)
        for error in findings.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Todo correcto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
