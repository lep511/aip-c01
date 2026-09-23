# 🚀 Quick Start — AWS AIP-C01 Docsify Site

Guía rápida para poner en marcha el sitio de documentación en **5 minutos**.

---

## ⚡ En 3 Comandos

```powershell
# 1. Abre el proyecto
cd c:\GitHub\aip-c01

# 2. Inicia un servidor local
python -m http.server 3000

# 3. Abre en tu navegador
# http://localhost:3000
```

✅ **¡Listo!** Tu sitio de documentación está corriendo localmente.

---

## 🌐 Deploy a Vercel (5 minutos)

### Opción A: Desde la Web (más fácil)

1. **Push tu código a GitHub** (si no lo has hecho)
   ```powershell
   git add .
   git commit -m "Add Docsify v5 documentation site"
   git push origin main
   ```

2. **Importa en Vercel**
   - Ve a: https://vercel.com/new
   - Conecta tu cuenta de GitHub
   - Selecciona el repo `aip-c01`
   - Click **Deploy**

3. **¡Listo!**
   - Tu sitio estará en vivo en ~60 segundos
   - URL: `https://tu-proyecto.vercel.app`

### Opción B: Desde CLI (más rápido)

```powershell
# 1. Instala Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel --prod
```

✅ **¡Deploy completado!** Tu URL aparecerá en la terminal.

---

## 📂 Estructura del Sitio

```
c:\GitHub\aip-c01\
│
├── index.html              # ← Configuración de Docsify
├── _sidebar.md            # ← Navegación principal
├── study/
│   ├── README.md          # ← Página de inicio
│   ├── domain-1/          # ← Domain 1 + tareas
│   ├── domain-2/          # ← Domain 2 + tareas
│   ├── domain-3/          # ← Domain 3 + tareas
│   ├── domain-4/          # ← Domain 4 + tareas
│   ├── domain-5/          # ← Domain 5 + tareas
│   └── informes/          # ← Informes completos
│
└── vercel.json            # ← Config de deployment
```

---

## ✏️ Editar Contenido

### Agregar una nueva tarea

1. **Crea el archivo markdown**
   ```powershell
   New-Item "study\domain-1\task-1-7-mi-nueva-tarea.md"
   ```

2. **Edita el sidebar del dominio**
   Abre `study/domain-1/_sidebar.md` y agrega:
   ```markdown
   - [Task 1.7 — Mi Nueva Tarea](study/domain-1/task-1-7-mi-nueva-tarea.md)
   ```

3. **Recarga el navegador** — ¡Los cambios aparecen inmediatamente!

### Cambiar el tema

Edita `index.html` y modifica las variables CSS:

```css
:root {
  --base-background-color: #0d1117;  /* Fondo principal */
  --link-color: #58a6ff;             /* Color de links */
  --sidebar-background: #161b22;     /* Fondo del sidebar */
}
```

---

## 🔧 Configuración Básica

Todo está en `index.html` bajo `window.$docsify`:

```javascript
window.$docsify = {
  name: 'AWS AIP-C01',           // Título del sitio
  loadSidebar: true,             // Habilita sidebars
  subMaxLevel: 3,                // Muestra H1-H3 en sidebar
  auto2top: true,                // Scroll al top al cambiar página
  homepage: 'study/README.md',   // Página de inicio
}
```

---

## 📚 Documentación Completa

| Documento | Contenido |
|-----------|-----------|
| **[SITE_README.md](SITE_README.md)** | Guía general del sitio |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Deployment detallado en Vercel |
| **[DOCSIFY_SITE.md](DOCSIFY_SITE.md)** | Documentación técnica completa |
| **[CHECKLIST.md](CHECKLIST.md)** | Checklist de verificación |

---

## 🐛 Problemas Comunes

### El servidor no inicia
```powershell
# Verifica que Python esté instalado
python --version

# Intenta con PHP
php -S localhost:3000

# O usa Node.js
npx http-server -p 3000
```

### El sidebar no aparece
- ✅ Verifica que `_sidebar.md` exista en la carpeta correcta
- ✅ Confirma que `loadSidebar: true` esté en `index.html`

### Cambios no se reflejan
- 🔄 Recarga con Ctrl+F5 (hard reload)
- 🧹 Limpia el caché del navegador

---

## 🎯 Próximos Pasos

1. ✅ **Ver el sitio local** → `python -m http.server 3000`
2. ✅ **Deploy a Vercel** → Sigue "Deploy a Vercel" arriba
3. ✅ **Personaliza el contenido** → Edita los markdown en `study/`
4. ✅ **Comparte tu URL** → Envia a colegas o compañeros de estudio

---

## 💡 Tips Rápidos

- **No hay build**: Los cambios en markdown son inmediatos
- **Git-friendly**: Todo es texto plano, fácil de versionar
- **Zero config en Vercel**: Solo push y deploy
- **Mobile-friendly**: Responsive design out-of-the-box

---

## 🔗 Links Útiles

- 🌐 **Docsify Docs**: https://docsify.js.org
- 🚀 **Vercel**: https://vercel.com
- 📖 **AWS Certification**: https://aws.amazon.com/certification

---

**¿Listo para empezar?** 🚀

```powershell
cd c:\GitHub\aip-c01
python -m http.server 3000
```

Abre http://localhost:3000 y comienza a estudiar! 📚
