# ✅ Checklist de Verificación - Docsify v5 Site

Este documento te ayuda a verificar que todo esté configurado correctamente antes del deployment.

---

## 📋 Pre-Deployment Checklist

### Archivos Principales

- [x] `index.html` — Configuración de Docsify v5 con tema oscuro
- [x] `_sidebar.md` — Navegación principal global
- [x] `_404.md` — Página de error personalizada
- [x] `.nojekyll` — Archivo vacío (necesario para Vercel/GitHub Pages)
- [x] `vercel.json` — Configuración de deployment
- [x] `.vercelignore` — Archivos a excluir del deployment

### Contenido

- [x] `study/README.md` — Página de inicio del sitio
- [x] `study/domain-1/README.md` — Resumen del Domain 1
- [x] `study/domain-1/_sidebar.md` — Navegación del Domain 1
- [x] `study/domain-2/README.md` — Resumen del Domain 2
- [x] `study/domain-2/_sidebar.md` — Navegación del Domain 2
- [x] `study/domain-3/README.md` — Resumen del Domain 3
- [x] `study/domain-3/_sidebar.md` — Navegación del Domain 3
- [x] `study/domain-4/README.md` — Resumen del Domain 4
- [x] `study/domain-4/_sidebar.md` — Navegación del Domain 4
- [x] `study/domain-5/README.md` — Resumen del Domain 5
- [x] `study/domain-5/_sidebar.md` — Navegación del Domain 5
- [x] `study/informes/_sidebar.md` — Navegación de informes

### Documentación

- [x] `DEPLOYMENT.md` — Guía de deployment en Vercel
- [x] `DOCSIFY_SITE.md` — Documentación técnica del sitio
- [x] `SITE_README.md` — README del sitio para usuarios
- [x] `CHECKLIST.md` — Este archivo

---

## 🧪 Testing Local

Antes de deployar, prueba el sitio localmente:

### 1. Servidor HTTP Simple

```powershell
# Opción 1: Python
python -m http.server 3000

# Opción 2: PHP
php -S localhost:3000

# Opción 3: Node.js (con npx)
npx http-server -p 3000
```

### 2. Verificaciones Manuales

Abre http://localhost:3000 y verifica:

#### ✅ Página de Inicio
- [ ] La página de inicio carga correctamente
- [ ] El título "AWS AIP-C01 Study Guide" aparece
- [ ] El sidebar principal se muestra a la izquierda
- [ ] El contenido de `study/README.md` se renderiza correctamente

#### ✅ Navegación
- [ ] Puedes navegar a Domain 1 desde el sidebar
- [ ] El sidebar cambia al de Domain 1 al entrar
- [ ] Puedes navegar entre tasks del Domain 1
- [ ] El botón "Inicio" te regresa a la página principal
- [ ] Puedes navegar a cada uno de los 5 dominios
- [ ] Puedes navegar a la sección de informes
- [ ] El sidebar de informes se muestra correctamente

#### ✅ Tema Oscuro
- [ ] El fondo es oscuro (#0d1117)
- [ ] El sidebar es gris oscuro (#161b22)
- [ ] El texto es legible (blanco grisáceo)
- [ ] Los links son azules (#58a6ff)
- [ ] Los code blocks tienen fondo oscuro
- [ ] Las tablas tienen borders visibles

#### ✅ Responsive Design
- [ ] Abre DevTools (F12) y prueba en modo móvil
- [ ] El sidebar se colapsa en móvil
- [ ] El contenido se ajusta correctamente
- [ ] Las tablas tienen scroll horizontal si son anchas
- [ ] Los botones y links son clickeables en táctil

#### ✅ Accesibilidad
- [ ] Puedes navegar con Tab (navegación con teclado)
- [ ] El skip link aparece al presionar Tab
- [ ] Los links tienen indicador de foco visible
- [ ] Los headings siguen jerarquía (H1 > H2 > H3)

#### ✅ Contenido
- [ ] Los emojis se muestran correctamente 📚 🏠 📊
- [ ] Los code blocks tienen syntax highlighting
- [ ] Las imágenes cargan correctamente (si hay)
- [ ] Los links internos funcionan
- [ ] Los links externos abren en la página correcta

#### ✅ Página 404
- [ ] Navega a una URL inexistente (ej: `/no-existe`)
- [ ] La página 404 personalizada aparece
- [ ] Los links de la página 404 funcionan

---

## 🚀 Pre-Deployment Checklist (Vercel)

Antes de hacer el primer deploy:

### Git Repository
- [ ] El código está commiteado en Git
- [ ] El código está pusheado a GitHub/GitLab/Bitbucket
- [ ] La rama principal es `main` o `master`

### Configuración
- [ ] `vercel.json` está en la raíz del proyecto
- [ ] `.vercelignore` excluye archivos innecesarios
- [ ] No hay archivos sensibles commiteados (.env, keys, etc.)

### Contenido
- [ ] Todos los archivos markdown están en la carpeta `study/`
- [ ] Todos los sidebars (`_sidebar.md`) están creados
- [ ] No hay links rotos (todos los paths son correctos)

---

## 📦 Post-Deployment Checklist

Después de deployar en Vercel:

### Deployment Exitoso
- [ ] El deployment completó sin errores
- [ ] Vercel asignó una URL (ej: `https://tu-proyecto.vercel.app`)
- [ ] El sitio es accesible en la URL de Vercel

### Funcionalidad
- [ ] La página de inicio carga correctamente
- [ ] Puedes navegar entre dominios
- [ ] Los sidebars cambian correctamente
- [ ] Los links internos funcionan
- [ ] La página 404 aparece para URLs inexistentes

### Performance
- [ ] El sitio carga rápido (< 2 segundos)
- [ ] Los recursos del CDN (jsDelivr) cargan correctamente
- [ ] No hay errores 404 en DevTools Network tab
- [ ] No hay errores en la consola del navegador

### SEO & Metadata
- [ ] El título del sitio aparece en la pestaña del navegador
- [ ] Los meta tags están correctos (view-source)
- [ ] Open Graph funciona (comparte en Facebook/LinkedIn)
- [ ] Twitter Cards funcionan (comparte en Twitter)

### Mobile
- [ ] El sitio se ve bien en móvil
- [ ] El sidebar es accesible (botón de hamburguesa)
- [ ] Las tablas tienen scroll horizontal
- [ ] Los botones son clickeables

### HTTPS & Security
- [ ] El sitio usa HTTPS (candado en la barra de direcciones)
- [ ] No hay advertencias de contenido mixto
- [ ] Los headers de seguridad están presentes (ver DevTools > Network)

---

## 🔄 Continuous Deployment Checklist

Verifica que el deployment automático funciona:

### Configuración
- [ ] Vercel está conectado a tu repositorio Git
- [ ] Los deployments automáticos están activados
- [ ] Las notificaciones están configuradas (opcional)

### Testing
- [ ] Haz un cambio menor en un archivo markdown
- [ ] Commitea y pushea el cambio
- [ ] Vercel detecta el cambio automáticamente
- [ ] El deployment nuevo se inicia
- [ ] El deployment completa exitosamente (~1 minuto)
- [ ] Los cambios se reflejan en el sitio en vivo

---

## 🐛 Common Issues Checklist

Si algo no funciona, revisa:

### Sidebar no aparece
- [ ] `loadSidebar: true` está en `window.$docsify`
- [ ] Los archivos `_sidebar.md` existen
- [ ] Los paths en `alias` son correctos

### 404 en rutas
- [ ] `vercel.json` contiene las rutas correctas
- [ ] El archivo `.nojekyll` existe
- [ ] No estás usando `file://` protocol

### Estilos no cargan
- [ ] El CDN de jsDelivr está accesible
- [ ] La URL del CSS es correcta en `index.html`
- [ ] Limpiaste el caché del navegador

### Contenido no se muestra
- [ ] El path en `homepage` es correcto
- [ ] El archivo `study/README.md` existe
- [ ] No hay errores en la consola del navegador

---

## ✅ Final Verification

Cuando todo esté listo:

- [ ] ✅ Sitio deployado en Vercel
- [ ] ✅ URL pública accesible
- [ ] ✅ Navegación funcional
- [ ] ✅ Tema oscuro aplicado
- [ ] ✅ Responsive en móvil y desktop
- [ ] ✅ Sin errores en consola
- [ ] ✅ Links internos funcionan
- [ ] ✅ Página 404 personalizada
- [ ] ✅ Deployment automático configurado
- [ ] ✅ Documentación completa

---

## 📝 Notas Adicionales

### Agregar Custom Domain
Si quieres usar tu propio dominio:

1. En Vercel Dashboard → Settings → Domains
2. Agrega tu dominio
3. Configura DNS según instrucciones de Vercel
4. Espera propagación DNS (hasta 48 horas)

### Agregar Analytics
Para agregar Google Analytics:

1. Crea propiedad en Google Analytics
2. Obtén el Tracking ID (GA4 Measurement ID)
3. Agrega el plugin en `index.html`:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/ga.min.js"></script>
   ```
4. Configura en `window.$docsify`:
   ```javascript
   ga: 'G-XXXXXXXXXX'
   ```

### Hacer Backup
Antes de cambios grandes:

```powershell
# Crea una copia de seguridad
git checkout -b backup/pre-major-change
git push origin backup/pre-major-change

# Vuelve a main para continuar
git checkout main
```

---

## 🎉 ¡Todo Listo!

Si todos los checks están marcados, tu sitio está listo para ser usado.

**URL del sitio**: ___________________________________

**Fecha de deployment**: ___________________________________

**Versión de Docsify**: v5.0.0

**Platform**: Vercel

---

**¿Necesitas ayuda?**
- Ver [DEPLOYMENT.md](DEPLOYMENT.md) para troubleshooting
- Ver [DOCSIFY_SITE.md](DOCSIFY_SITE.md) para documentación técnica
- Consultar [Docsify Docs](https://docsify.js.org)
