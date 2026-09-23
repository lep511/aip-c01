# AWS AIP-C01 Study Guide - Docsify Site

> **Sitio de documentación** construido con **Docsify v5** para el examen **AWS Certified Generative AI Developer – Professional (AIP-C01)**

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=flat&logo=vercel)](https://vercel.com)
[![Docsify](https://img.shields.io/badge/Docsify-v5.0.0-brightgreen?style=flat)](https://docsify.js.org)
[![License](https://img.shields.io/badge/License-Study%20Material-blue?style=flat)](LICENSE)

---

## 🌐 Sitio en Vivo

**URL del sitio**: [https://aws-aip-c01.vercel.app](https://aws-aip-c01.vercel.app) *(actualizar con tu URL real)*

---

## 📖 Acerca de Este Sitio

Este sitio contiene una **guía de estudio técnica completa** para el examen AWS AIP-C01, organizada en:

- **5 Dominios** del examen (Domain 1 a Domain 5)
- **75+ Skills** específicos evaluados
- **Informes técnicos completos** por dominio
- **Arquitecturas de referencia** y patrones de diseño
- **Ejemplos prácticos** y snippets de código
- **Patrones de pregunta** del examen y trampas comunes

---

## ✨ Características

### 🎨 Diseño Moderno
- ✅ Tema oscuro estilo GitHub
- ✅ Responsive design (desktop y móvil)
- ✅ Navegación intuitiva con sidebars contextuales
- ✅ Syntax highlighting para múltiples lenguajes

### ♿ Accesibilidad
- ✅ Navegación completa con teclado
- ✅ Skip link para screen readers
- ✅ ARIA labels y roles semánticos
- ✅ Soporte para `prefers-reduced-motion`

### 🚀 Performance
- ✅ Sin proceso de build (renderizado en runtime)
- ✅ CDN global con jsDelivr
- ✅ Caching optimizado
- ✅ Lazy loading de contenido

### 🔍 SEO & Compartir
- ✅ Meta tags optimizados
- ✅ Open Graph para redes sociales
- ✅ Twitter Cards
- ✅ URLs limpias (sin .html)

---

## 🏗️ Arquitectura

### Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Docsify** | v5.0.0 | Generador de sitios de documentación |
| **Prism.js** | v1.x | Syntax highlighting |
| **jsDelivr** | CDN | Entrega de assets estáticos |
| **Vercel** | Platform | Hosting y deployment |

### Estructura del Sitio

```
/
├── index.html              # Punto de entrada (Docsify config)
├── _sidebar.md            # Navegación principal
├── _404.md               # Página de error personalizada
│
└── study/                 # Contenido de estudio
    ├── README.md         # Página de inicio
    ├── domain-1/         # Domain 1 + sidebar específico
    ├── domain-2/         # Domain 2 + sidebar específico
    ├── domain-3/         # Domain 3 + sidebar específico
    ├── domain-4/         # Domain 4 + sidebar específico
    ├── domain-5/         # Domain 5 + sidebar específico
    ├── informes/         # Informes completos + sidebar
    └── official-page/    # Recursos oficiales de AWS
```

---

## 🚀 Quick Start

### Ver el Sitio Localmente

#### Opción 1: Servidor HTTP Simple (Python)

```powershell
# Desde la raíz del proyecto
python -m http.server 3000
```

Luego abre: http://localhost:3000

#### Opción 2: Live Server (VS Code)

1. Instala la extensión [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
2. Click derecho en `index.html` → **Open with Live Server**

#### Opción 3: Vercel CLI

```powershell
# Instala Vercel CLI
npm install -g vercel

# Inicia servidor de desarrollo
vercel dev
```

---

## 📦 Deployment en Vercel

### Deployment Automático (Recomendado)

1. **Push a GitHub**
   ```powershell
   git add .
   git commit -m "Add Docsify site"
   git push origin main
   ```

2. **Importa en Vercel**
   - Ve a [vercel.com/new](https://vercel.com/new)
   - Conecta tu repositorio
   - Click en **Deploy**
   - ¡Listo! Tu sitio estará en vivo en ~1 minuto

### Deployment Manual

```powershell
# Instala Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

📖 **Guía detallada**: Ver [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📝 Agregar Contenido

### Agregar una Nueva Task

1. Crea el archivo markdown:
   ```powershell
   New-Item "study\domain-1\task-1-7-nueva-task.md"
   ```

2. Actualiza el sidebar del dominio (`study/domain-1/_sidebar.md`):
   ```markdown
   - [Task 1.7 — Nueva Task](study/domain-1/task-1-7-nueva-task.md)
   ```

3. Los cambios son automáticos (no hay build)

### Agregar un Nuevo Dominio

1. Crea la estructura:
   ```powershell
   New-Item -ItemType Directory "study\domain-6"
   New-Item "study\domain-6\README.md"
   New-Item "study\domain-6\_sidebar.md"
   ```

2. Actualiza `_sidebar.md` principal

3. Agrega alias en `index.html`:
   ```javascript
   alias: {
     '/study/domain-6/.*': '/study/domain-6/_sidebar.md',
   }
   ```

---

## 🎨 Personalización

### Cambiar Colores del Tema

Edita las variables CSS en `index.html`:

```css
:root {
  --base-background-color: #0d1117;  /* Background principal */
  --link-color: #58a6ff;             /* Color de links */
  --sidebar-background: #161b22;     /* Background del sidebar */
  /* ... más variables ... */
}
```

### Agregar Plugins

Agrega el script antes de `</body>` en `index.html`:

```html
<!-- Plugin de búsqueda -->
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/search.min.js"></script>
```

**Plugins disponibles:**
- Search (búsqueda full-text)
- Zoom Image (zoom en imágenes)
- Pagination (navegación prev/next)
- External Script
- Tabs

---

## 📚 Documentación

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Guía completa de deployment en Vercel
- **[DOCSIFY_SITE.md](DOCSIFY_SITE.md)** — Documentación técnica del sitio
- **[Docsify Docs](https://docsify.js.org)** — Documentación oficial de Docsify
- **[Vercel Docs](https://vercel.com/docs)** — Documentación de Vercel

---

## 🔧 Configuración

### Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `index.html` | Configuración principal de Docsify + estilos |
| `vercel.json` | Configuración de deployment en Vercel |
| `.vercelignore` | Archivos a excluir del deployment |
| `.nojekyll` | Indica que no use Jekyll (necesario para GitHub Pages/Vercel) |
| `_sidebar.md` | Navegación global del sitio |
| `_404.md` | Página de error personalizada |

### Variables de Entorno

No se requieren variables de entorno para este sitio. Todo es estático.

---

## 🐛 Troubleshooting

### Sidebar no aparece

**Problema**: El sidebar no se muestra al navegar.

**Solución**: 
1. Verifica que `loadSidebar: true` esté en `window.$docsify`
2. Confirma que el archivo `_sidebar.md` existe en la ubicación correcta
3. Revisa los alias en la configuración

### 404 en rutas internas

**Problema**: Al recargar una página interna aparece 404.

**Solución**: 
- En Vercel: Asegúrate de que `vercel.json` contenga las rutas correctas
- En local: Usa un servidor que soporte SPA routing (no file://)

### Estilos no se aplican

**Problema**: El tema oscuro no aparece.

**Solución**:
1. Abre DevTools (F12) y verifica errores en Console
2. Confirma que el CDN de Docsify esté accesible
3. Limpia caché del navegador (Ctrl+Shift+R)

---

## 📊 Estadísticas del Contenido

| Métrica | Valor |
|---------|-------|
| **Dominios** | 5 |
| **Tasks totales** | 24 |
| **Skills evaluados** | 75+ |
| **Informes técnicos** | 5 |
| **Páginas de contenido** | 50+ |
| **Peso del examen cubierto** | 100% |

---

## 🤝 Contribuir

Este es un proyecto de estudio personal. Si encuentras errores o quieres sugerir mejoras:

1. **Fork** el repositorio
2. **Crea una rama** para tu feature (`git checkout -b feature/mejora`)
3. **Commit** tus cambios (`git commit -m 'Add: nueva sección'`)
4. **Push** a la rama (`git push origin feature/mejora`)
5. **Abre un Pull Request**

---

## 📄 Licencia

Este contenido es material de estudio personal construido a partir de documentación oficial de AWS. Las fuentes originales están sujetas a sus propias licencias.

> ⚠️ **Disclaimer**: El contenido de las fuentes AWS fue parafraseado y resumido para cumplir con restricciones de licencia. Consulta siempre la [documentación oficial de AWS](https://docs.aws.amazon.com/) para información autorizada.

---

## 🔗 Links Útiles

- **[AWS Certification](https://aws.amazon.com/certification/)** — Página oficial de certificaciones
- **[Exam Guide AIP-C01](https://d1.awsstatic.com/training-and-certification/docs-ai-professional/AWS-Certified-Generative-AI-Developer-Professional_Exam-Guide.pdf)** — Guía oficial del examen
- **[AWS Skill Builder](https://explore.skillbuilder.aws/)** — Cursos oficiales de AWS
- **[AWS Whitepapers](https://aws.amazon.com/whitepapers/)** — Arquitecturas de referencia

---

## 🎓 Acerca del Examen AIP-C01

**AWS Certified Generative AI Developer – Professional (AIP-C01)**

- **Duración**: 180 minutos
- **Preguntas**: 75 (65 puntuadas + 10 no puntuadas)
- **Puntuación mínima**: 750/1000
- **Costo**: USD 300
- **Formato**: Opción múltiple y respuesta múltiple
- **Modalidad**: En línea o en centro de testing

**Dominios evaluados:**
1. Foundation Model Integration (31%)
2. Implementation and Integration (26%)
3. AI Safety, Security & Governance (20%)
4. Operational Efficiency & Optimization (12%)
5. Testing, Validation & Troubleshooting (11%)

---

**¡Buena suerte en tu preparación! 🚀**

---

<div align="center">

**Construido con** ❤️ **usando** [Docsify](https://docsify.js.org)

**Deployed en** [Vercel](https://vercel.com)

</div>
