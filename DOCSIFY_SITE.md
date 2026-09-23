# Docsify v5 Documentation Site - AWS AIP-C01

Este documento describe la estructura y configuración del sitio de documentación construido con Docsify v5.

## 📁 Estructura de Archivos

```
c:\GitHub\aip-c01\
│
├── index.html                 # Punto de entrada principal (Docsify v5)
├── _sidebar.md               # Sidebar principal (navegación global)
├── _404.md                   # Página de error 404 personalizada
├── .nojekyll                 # Indica a GitHub/Vercel que no use Jekyll
├── vercel.json              # Configuración de deployment en Vercel
├── .vercelignore            # Archivos a ignorar en deployment
├── DEPLOYMENT.md            # Guía de deployment
├── DOCSIFY_SITE.md          # Este archivo (documentación del sitio)
│
└── study/                    # Contenido de estudio
    ├── README.md            # Página de inicio del sitio
    │
    ├── domain-1/            # Domain 1: Foundation Model Integration
    │   ├── _sidebar.md      # Sidebar específico del Domain 1
    │   ├── README.md        # Resumen del Domain 1
    │   ├── referencias-oficiales.md
    │   ├── task-1-1-analisis-y-diseno.md
    │   ├── task-1-2-seleccion-y-configuracion-fm.md
    │   ├── task-1-3-datos-para-consumo-fm.md
    │   ├── task-1-4-vector-stores.md
    │   ├── task-1-5-retrieval.md
    │   └── task-1-6-prompt-engineering-governance.md
    │
    ├── domain-2/            # Domain 2: Implementation & Integration
    │   ├── _sidebar.md
    │   ├── README.md
    │   ├── referencias-oficiales.md
    │   ├── task-2-1-agentic-ai-y-herramientas.md
    │   ├── task-2-2-despliegue-de-modelos.md
    │   ├── task-2-3-integracion-empresarial.md
    │   ├── task-2-4-integraciones-api-fm.md
    │   └── task-2-5-patrones-de-aplicacion-y-tooling.md
    │
    ├── domain-3/            # Domain 3: AI Safety & Security
    │   ├── _sidebar.md
    │   ├── README.md
    │   ├── referencias-oficiales.md
    │   ├── task-3-1-controles-de-seguridad-entrada-salida.md
    │   ├── task-3-2-seguridad-y-privacidad-de-datos.md
    │   ├── task-3-3-governance-y-compliance.md
    │   └── task-3-4-ia-responsable.md
    │
    ├── domain-4/            # Domain 4: Operational Efficiency
    │   ├── _sidebar.md
    │   ├── README.md
    │   ├── referencias-oficiales.md
    │   ├── task-4-1-costes-y-eficiencia-de-recursos.md
    │   ├── task-4-2-latencia-y-throughput.md
    │   ├── task-4-2-retrieval-y-parametros.md
    │   ├── task-4-3-observabilidad-y-metricas.md
    │   └── task-4-3-herramientas-vector-stores-y-fallos.md
    │
    ├── domain-5/            # Domain 5: Testing & Validation
    │   ├── _sidebar.md
    │   ├── README.md
    │   ├── referencias-oficiales.md
    │   ├── task-5-1-frameworks-y-herramientas.md
    │   ├── task-5-1-retrieval-y-agentes.md
    │   └── task-5-2-monitoreo-troubleshooting-optimizacion.md
    │
    ├── informes/            # Informes técnicos completos
    │   ├── _sidebar.md
    │   ├── informe_dominio1_implementation_integration.md
    │   ├── informe_dominio2_implementation_integration.md
    │   ├── informe_dominio3_ai_safety_security_governance.md
    │   ├── informe_dominio4_operational_efficiency_optimization.md
    │   └── informe_dominio5_testing_validation_troubleshooting.md
    │
    └── official-page/       # Contenido de la página oficial de AWS
        └── ... (archivos markdown de la documentación oficial)
```

---

## ⚙️ Configuración de Docsify

### Archivo: `index.html`

**Características principales:**

1. **Docsify v5.0.0** - Última versión estable
2. **Tema oscuro moderno** - Personalizado con variables CSS
3. **CDN de jsDelivr** - Para recursos de Docsify
4. **Plugins incluidos:**
   - Emoji support
   - Copy to clipboard para code blocks
   - Syntax highlighting (Prism.js) para múltiples lenguajes

**Configuración principal (`window.$docsify`):**

```javascript
{
  name: 'AWS AIP-C01',           // Nombre del sitio
  nameLink: '/',                 // Link del título
  loadSidebar: true,             // Habilita sidebars personalizados
  subMaxLevel: 3,                // Muestra headings hasta H3 en sidebar
  auto2top: true,                // Scroll automático al top al cambiar página
  relativePath: true,            // Permite paths relativos en links
  notFoundPage: '_404.md',       // Página 404 personalizada
  homepage: 'study/README.md',   // Página de inicio
  
  // Alias para sidebars específicos por carpeta
  alias: {
    '/study/domain-1/.*': '/study/domain-1/_sidebar.md',
    '/study/domain-2/.*': '/study/domain-2/_sidebar.md',
    // ... etc
  }
}
```

---

## 🎨 Tema Oscuro

El tema oscuro está implementado usando **CSS Custom Properties (variables)** siguiendo el estilo de GitHub Dark:

### Colores principales:
- **Background**: `#0d1117` (negro azulado)
- **Sidebar**: `#161b22` (gris oscuro)
- **Text**: `#e6edf3` (blanco grisáceo)
- **Links**: `#58a6ff` (azul brillante)
- **Code blocks**: `#161b22` con border `#30363d`

### Variables CSS clave:
```css
:root {
  color-scheme: dark;
  --base-background-color: #0d1117;
  --base-color: #e6edf3;
  --link-color: #58a6ff;
  --sidebar-background: #161b22;
  --code-block-background: #161b22;
  /* ... más variables ... */
}
```

---

## 🗂️ Sistema de Navegación

### Sidebars Jerárquicos

El sitio usa un sistema de sidebars contextuales:

1. **Sidebar global** (`/_sidebar.md`)
   - Se muestra en la página de inicio
   - Lista los 5 dominios y sección de informes
   - Links a recursos oficiales

2. **Sidebars por dominio** (`/study/domain-X/_sidebar.md`)
   - Se activan al navegar a cualquier página dentro de `domain-X/`
   - Listan todas las tasks del dominio
   - Link de regreso al inicio
   - Link al informe completo del dominio

3. **Sidebar de informes** (`/study/informes/_sidebar.md`)
   - Se activa en la carpeta de informes
   - Lista los 5 informes con links bidireccionales a dominios

### Configuración de Alias

Los alias en `window.$docsify` mapean rutas a sidebars específicos:

```javascript
alias: {
  '/study/domain-1/.*': '/study/domain-1/_sidebar.md',
  '/study/domain-2/.*': '/study/domain-2/_sidebar.md',
  // ...
}
```

Esto hace que:
- Al visitar `/study/domain-1/task-1-1-analisis-y-diseno.md` → se carga `/study/domain-1/_sidebar.md`
- Al visitar `/study/informes/informe_dominio1_*.md` → se carga `/study/informes/_sidebar.md`

---

## 🚀 Características

### Accesibilidad

- ✅ **Skip link** - "Saltar al contenido principal" para navegación con teclado
- ✅ **ARIA labels** - `role="main"` en el contenido principal
- ✅ **Focus visible** - Indicadores claros de foco para navegación con teclado
- ✅ **Reduced motion** - Respeta `prefers-reduced-motion` del usuario
- ✅ **Semantic HTML** - Uso correcto de headings y landmarks

### Responsive Design

- ✅ **Mobile-first** - Optimizado para dispositivos móviles
- ✅ **Sidebar colapsable** - En móvil, el sidebar se oculta por defecto
- ✅ **Tablas scrollables** - Tablas largas tienen scroll horizontal en móvil
- ✅ **Viewport meta tag** - Escala correcta en todos los dispositivos

### Performance

- ✅ **Preconnect** - A cdn.jsdelivr.net para recursos más rápidos
- ✅ **DNS prefetch** - Resolución DNS anticipada
- ✅ **No build process** - Docsify renderiza en runtime (más rápido para deploys)
- ✅ **Cache headers** - Configurados en Vercel para óptimo caching

### SEO

- ✅ **Meta tags** - Title, description, keywords
- ✅ **Open Graph** - Para compartir en redes sociales
- ✅ **Twitter Cards** - Para compartir en Twitter
- ✅ **Semantic HTML** - Mejora la indexación de buscadores
- ✅ **Clean URLs** - Sin extensión .html (configurado en Vercel)

---

## 🔧 Mantenimiento

### Agregar nuevo contenido

**Para agregar una nueva task a un dominio:**

1. Crea el archivo markdown en la carpeta del dominio:
   ```powershell
   New-Item "study\domain-1\task-1-7-nueva-task.md"
   ```

2. Actualiza el `_sidebar.md` del dominio:
   ```markdown
   - [Task 1.7 — Nueva Task](study/domain-1/task-1-7-nueva-task.md)
   ```

3. Los cambios se reflejarán automáticamente (no hay build)

**Para agregar un nuevo dominio:**

1. Crea la carpeta:
   ```powershell
   New-Item -ItemType Directory "study\domain-6"
   ```

2. Crea los archivos necesarios:
   - `README.md` - Resumen del dominio
   - `_sidebar.md` - Navegación del dominio
   - Archivos de tasks

3. Actualiza el `_sidebar.md` principal para incluir el nuevo dominio

### Actualizar estilos

Edita la sección `<style>` en `index.html`. Los cambios serán inmediatos en el siguiente deploy.

### Agregar plugins

Agrega el script del plugin antes del cierre de `</body>` en `index.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/search.min.js"></script>
```

Luego configura el plugin en `window.$docsify`.

---

## 📊 Plugins Disponibles (Opcionales)

Plugins que puedes agregar fácilmente:

### 1. Search (Búsqueda)
```html
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/search.min.js"></script>
```

### 2. Zoom Image
```html
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/zoom-image.min.js"></script>
```

### 3. Pagination (Next/Previous)
```html
<script src="https://cdn.jsdelivr.net/npm/docsify-pagination@2/dist/docsify-pagination.min.js"></script>
```

### 4. External Script
```html
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/external-script.min.js"></script>
```

### 5. Tabs
```html
<script src="https://cdn.jsdelivr.net/npm/docsify-tabs@1"></script>
```

---

## 🐛 Troubleshooting

### Problema: Sidebar no cambia al navegar entre dominios

**Causa**: Los alias no están configurados correctamente.

**Solución**: Verifica que en `window.$docsify.alias` cada patrón de ruta apunte al `_sidebar.md` correcto.

### Problema: 404 en GitHub Pages

**Causa**: Falta el archivo `.nojekyll`.

**Solución**: Asegúrate de que `.nojekyll` exista en la raíz del repositorio.

### Problema: Estilos no se aplican

**Causa**: CDN bloqueado o problema de red.

**Solución**: 
1. Verifica en DevTools (F12) si los recursos del CDN se cargan
2. Prueba con otro CDN (UNPKG o cdnjs)

### Problema: Links internos no funcionan

**Causa**: Paths relativos incorrectos.

**Solución**: Usa paths absolutos desde la raíz: `/study/domain-1/README.md` en lugar de `./README.md`

---

## 📚 Referencias

- [Docsify Documentation](https://docsify.js.org)
- [Docsify v5 Release Notes](https://github.com/docsifyjs/docsify/releases/tag/v5.0.0)
- [Vercel Documentation](https://vercel.com/docs)
- [GitHub Markdown Guide](https://guides.github.com/features/mastering-markdown/)

---

## 📝 Notas

- **No hay proceso de build**: Docsify renderiza el markdown en el navegador
- **Hot reload en dev**: Los cambios en markdown se reflejan al recargar la página
- **Git-friendly**: Solo archivos de texto, fácil de versionar y colaborar
- **Zero config en Vercel**: El `vercel.json` maneja todo automáticamente

---

**Versión del sitio**: Docsify v5.0.0
**Última actualización**: 2026-09-23
