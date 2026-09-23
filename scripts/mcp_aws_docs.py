"""Cliente de linea de comandos para el MCP server de documentacion de AWS.

Habla JSON-RPC 2.0 por stdio contra `awslabs.aws-documentation-mcp-server`, el
servidor que Kiro declara en `~/.kiro/settings/mcp.json`. Sirve para consultar
`docs.aws.amazon.com` a traves del MCP cuando el cliente MCP del IDE no expone
las herramientas, y para lanzar lotes de consultas reproducibles al construir
los materiales de `study/`.

El servidor se descarga y ejecuta con `uvx`, asi que no hay que instalar nada:
basta tener `uv` en el PATH.

Herramientas que expone el servidor:

| Herramienta | Para que sirve |
| --- | --- |
| `search_documentation` | Busca en toda la documentacion de AWS por frase |
| `read_documentation` | Descarga una pagina y la convierte a Markdown |
| `read_sections` | Extrae solo las secciones indicadas de una pagina |
| `search_table` | Filtra filas de una tabla grande (cuotas, IAM actions) |
| `recommend` | Paginas relacionadas: nuevas, similares y siguientes |

Uso:

    uv run python scripts/mcp_aws_docs.py tools
    uv run python scripts/mcp_aws_docs.py search "Bedrock batch inference quotas" --limit 15
    uv run python scripts/mcp_aws_docs.py read https://docs.aws.amazon.com/.../pagina.html
    uv run python scripts/mcp_aws_docs.py read <url> --max-length 20000 --start-index 20000
    uv run python scripts/mcp_aws_docs.py sections <url> "Best practices" "Quotas"
    uv run python scripts/mcp_aws_docs.py table <url> "Anthropic" --section-title "Supported models"
    uv run python scripts/mcp_aws_docs.py recommend <url>
    uv run python scripts/mcp_aws_docs.py batch lote.json

El modo `batch` recibe un JSON con una lista de peticiones, lo que permite
encadenar decenas de lecturas en una sola sesion del servidor:

    [
      {"label": "GENCOST03", "tool": "read_documentation",
       "arguments": {"url": "https://docs.aws.amazon.com/...", "max_length": 6000}},
      {"tool": "search_documentation", "arguments": {"search_phrase": "prompt caching"}}
    ]

Un fallo en una peticion del lote se imprime y la iteracion continua, igual que
hace `web_to_markdown` al seguir enlaces.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

SERVER_COMMAND = ["uvx", "awslabs.aws-documentation-mcp-server@latest"]
PROTOCOL_VERSION = "2024-11-05"
# La documentacion de AWS trae flechas, guiones tipograficos y simbolos que la
# consola de Windows (cp1252) no sabe codificar. Sin esto, imprimir una pagina
# revienta con UnicodeEncodeError a mitad del lote.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
CLIENT_NAME = "aip-c01-doc-builder"
CLIENT_VERSION = "1.0.0"
# El servidor tarda en arrancar la primera vez, porque uvx resuelve y descarga
# el paquete. Despues queda en la cache de uv y el arranque es inmediato.
SHUTDOWN_TIMEOUT_SECONDS = 10
# Lineas de stderr que se conservan para el mensaje de error. El servidor es
# verboso en el arranque y no interesa todo el historial.
STDERR_TAIL_LINES = 20


class McpError(RuntimeError):
    """Fallo al hablar con el servidor MCP."""


class McpClient:
    """Sesion stdio contra un servidor MCP.

    El servidor se lanza como subproceso y se le habla JSON-RPC 2.0 en lineas
    de texto. Hay que completar el handshake (`initialize` mas la notificacion
    `notifications/initialized`) antes de poder invocar herramientas.
    """

    def __init__(self, command: list[str] | None = None) -> None:
        environment = dict(os.environ)
        # Mismos valores que la configuracion de Kiro, para que el servidor se
        # comporte igual desde aqui que desde el IDE.
        environment.setdefault("FASTMCP_LOG_LEVEL", "ERROR")
        environment.setdefault("AWS_DOCUMENTATION_PARTITION", "aws")

        self.process = subprocess.Popen(
            command or SERVER_COMMAND,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=environment,
            shell=False,
        )
        self._next_id = 0
        self._stderr: list[str] = []
        # Hay que drenar stderr en un hilo aparte: si el buffer del pipe se
        # llena, el servidor se bloquea al escribir y la sesion se cuelga sin
        # ningun error visible.
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self) -> None:
        if self.process.stderr is None:
            return
        for line in self.process.stderr:
            self._stderr.append(line)

    def _stderr_tail(self) -> str:
        return "".join(self._stderr[-STDERR_TAIL_LINES:])

    def _send(self, payload: dict[str, Any]) -> None:
        if self.process.stdin is None:
            raise McpError("el subproceso no tiene stdin")
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

    def _await_response(self, request_id: int) -> dict[str, Any]:
        if self.process.stdout is None:
            raise McpError("el subproceso no tiene stdout")
        while True:
            line = self.process.stdout.readline()
            if not line:
                raise McpError(
                    f"el servidor MCP cerro la conexion. stderr:\n{self._stderr_tail()}"
                )
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                # Ruido de arranque que no es JSON-RPC: se descarta.
                continue
            # Las notificaciones del servidor no llevan id y no son la
            # respuesta que se espera.
            if message.get("id") == request_id:
                return message

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Envia una peticion y devuelve su `result`."""
        self._next_id += 1
        request_id = self._next_id
        self._send(
            {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        )
        response = self._await_response(request_id)
        if "error" in response:
            raise McpError(f"{method} devolvio error: {response['error']}")
        return response.get("result", {})

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Envia una notificacion, que no espera respuesta."""
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def handshake(self) -> dict[str, Any]:
        """Completa el `initialize` y devuelve la informacion del servidor."""
        result = self.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": CLIENT_NAME, "version": CLIENT_VERSION},
            },
        )
        self.notify("notifications/initialized")
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        return self.request("tools/list").get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Invoca una herramienta y devuelve su contenido como texto."""
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        blocks: list[str] = []
        for block in result.get("content", []):
            if block.get("type") == "text":
                blocks.append(block.get("text", ""))
            else:
                blocks.append(json.dumps(block, ensure_ascii=False, indent=2))
        return "\n".join(blocks)

    def close(self) -> None:
        try:
            if self.process.stdin is not None:
                self.process.stdin.close()
            self.process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
        except Exception:
            self.process.kill()

    def __enter__(self) -> McpClient:
        self.handshake()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def print_tools(client: McpClient, server_info: dict[str, Any]) -> None:
    print(f"Servidor: {server_info.get('serverInfo')}")
    for tool in client.list_tools():
        print(f"\n== {tool['name']}")
        description = (tool.get("description") or "").strip()
        print(description)
        schema = tool.get("inputSchema", {})
        print("\n  parametros:")
        required = set(schema.get("required", []))
        for name, spec in schema.get("properties", {}).items():
            marca = "obligatorio" if name in required else f"por defecto {spec.get('default')!r}"
            print(f"    - {name} ({spec.get('type', '?')}, {marca}): {spec.get('description', '')}")


def run_batch(client: McpClient, path: Path) -> int:
    """Ejecuta un lote de peticiones y devuelve el numero de fallos."""
    requests = json.loads(path.read_text(encoding="utf-8"))
    failures = 0
    total = len(requests)
    for number, entry in enumerate(requests, start=1):
        arguments = entry.get("arguments", {})
        label = (
            entry.get("label")
            or arguments.get("url")
            or arguments.get("search_phrase")
            or entry.get("tool")
        )
        print(f"\n{'=' * 100}")
        print(f"### [{number}/{total}] {entry['tool']} :: {label}")
        print("=" * 100)
        try:
            print(client.call_tool(entry["tool"], arguments))
        except McpError as error:
            failures += 1
            print(f"ERROR: {error}")
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="accion", required=True)

    subparsers.add_parser("tools", help="lista las herramientas del servidor y sus parametros")

    search = subparsers.add_parser("search", help="busca en la documentacion de AWS")
    search.add_argument("frase", help="frase de busqueda")
    search.add_argument("-l", "--limit", type=int, default=10, help="resultados a devolver (1-50)")
    search.add_argument("-i", "--intent", default="", help="intencion de la busqueda, sin datos personales")

    read = subparsers.add_parser("read", help="descarga una pagina y la convierte a Markdown")
    read.add_argument("url", help="URL de docs.aws.amazon.com terminada en .html")
    read.add_argument("-m", "--max-length", type=int, default=5000, help="caracteres a devolver")
    read.add_argument("-s", "--start-index", type=int, default=0, help="indice inicial, para paginar")

    sections = subparsers.add_parser("sections", help="extrae solo las secciones indicadas")
    sections.add_argument("url", help="URL de la pagina")
    sections.add_argument("titulos", nargs="+", help="titulos de seccion a extraer")

    table = subparsers.add_parser("table", help="filtra filas de una tabla grande")
    table.add_argument("url", help="URL de la pagina que contiene la tabla")
    table.add_argument("consulta", help="termino de busqueda sobre las filas")
    table.add_argument("-t", "--section-title", default=None, help="seccion que contiene la tabla")
    table.add_argument("-r", "--max-rows", type=int, default=20, help="filas a devolver (1-100)")

    recommend = subparsers.add_parser("recommend", help="paginas relacionadas con una URL")
    recommend.add_argument("url", help="URL de la pagina de partida")

    batch = subparsers.add_parser("batch", help="ejecuta un lote de peticiones desde un JSON")
    batch.add_argument("fichero", type=Path, help="JSON con la lista de peticiones")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        client = McpClient()
    except FileNotFoundError:
        print(
            "error: no se encontro `uvx`. Instala uv: https://docs.astral.sh/uv/getting-started/installation/",
            file=sys.stderr,
        )
        return 2

    try:
        server_info = client.handshake()

        if args.accion == "tools":
            print_tools(client, server_info)
            return 0

        if args.accion == "search":
            print(
                client.call_tool(
                    "search_documentation",
                    {
                        "search_phrase": args.frase,
                        "search_intent": args.intent,
                        "limit": args.limit,
                    },
                )
            )
            return 0

        if args.accion == "read":
            print(
                client.call_tool(
                    "read_documentation",
                    {
                        "url": args.url,
                        "max_length": args.max_length,
                        "start_index": args.start_index,
                    },
                )
            )
            return 0

        if args.accion == "sections":
            print(
                client.call_tool(
                    "read_sections",
                    {"url": args.url, "section_titles": args.titulos},
                )
            )
            return 0

        if args.accion == "table":
            arguments: dict[str, Any] = {
                "url": args.url,
                "query": args.consulta,
                "max_rows": args.max_rows,
            }
            if args.section_title:
                arguments["section_title"] = args.section_title
            print(client.call_tool("search_table", arguments))
            return 0

        if args.accion == "recommend":
            print(client.call_tool("recommend", {"url": args.url}))
            return 0

        if args.accion == "batch":
            if not args.fichero.is_file():
                print(f"error: {args.fichero} no existe", file=sys.stderr)
                return 2
            failures = run_batch(client, args.fichero)
            if failures:
                print(f"\n{failures} peticion(es) fallaron.", file=sys.stderr)
                return 1
            return 0

        return 2
    except McpError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
