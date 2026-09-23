# Deployment Guide - AWS AIP-C01 Study Site

Esta guía explica cómo desplegar el sitio de documentación Docsify v5 en Vercel.

## 📋 Pre-requisitos

- Cuenta en [Vercel](https://vercel.com) (gratuita)
- Repositorio Git (GitHub, GitLab, o Bitbucket)
- [Vercel CLI](https://vercel.com/docs/cli) (opcional, para deploy local)

---

## 🚀 Deployment en Vercel (Método Recomendado)

### Opción 1: Desde la Web UI de Vercel

1. **Push tu código a un repositorio Git**
   ```powershell
   git add .
   git commit -m "Add Docsify v5 documentation site"
   git push origin main
   ```

2. **Importa el proyecto en Vercel**
   - Ve a [vercel.com/new](https://vercel.com/new)
   - Conecta tu cuenta de Git (GitHub/GitLab/Bitbucket)
   - Selecciona el repositorio `aip-c01`
   - Click en **Import**

3. **Configura el proyecto**
   - **Project Name**: `aws-aip-c01-study-guide` (o el nombre que prefieras)
   - **Framework Preset**: Selecciona **Other** o déjalo en Auto-detect
   - **Root Directory**: `.` (raíz del proyecto)
   - **Build Command**: Déjalo vacío (Docsify no necesita build)
   - **Output Directory**: `.` (raíz del proyecto)
   - **Install Command**: Déjalo vacío

4. **Deploy**
   - Click en **Deploy**
   - Espera 1-2 minutos mientras Vercel procesa el deployment
   - ¡Listo! Tu sitio estará disponible en `https://tu-proyecto.vercel.app`

### Opción 2: Desde Vercel CLI

1. **Instala Vercel CLI** (si no lo tienes)
   ```powershell
   npm install -g vercel
   ```

2. **Login en Vercel**
   ```powershell
   vercel login
   ```

3. **Deploy desde la raíz del proyecto**
   ```powershell
   cd c:\GitHub\aip-c01
   vercel
   ```

4. **Sigue las prompts**
   - Set up and deploy? → **Y**
   - Which scope? → Selecciona tu cuenta
   - Link to existing project? → **N** (primera vez)
   - What's your project's name? → `aws-aip-c01-study-guide`
   - In which directory is your code located? → `.` (presiona Enter)
   - Want to override the settings? → **N**

5. **Deploy a producción**
   ```powershell
   vercel --prod
   ```

---

## ⚙️ Configuración

El archivo `vercel.json` en la raíz del proyecto ya está configurado con:

### Rewrites (SPA Routing)
```json
"routes": [
  {
    "src": "/(.*)",
    "dest": "/index.html"
  }
]
```
Esto asegura que todas las rutas sirvan el `index.html` para que Docsify maneje la navegación.

### Headers de Seguridad
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### Cache Headers
- **Archivos estáticos** (JS, CSS, imágenes): `max-age=31536000, immutable`
- **Contenido Markdown**: `max-age=0, must-revalidate`

---

## 🔄 Actualizaciones Automáticas

Una vez configurado, Vercel automáticamente:
- ✅ Detecta nuevos commits en tu repositorio
- ✅ Despliega automáticamente los cambios
- ✅ Crea previews para pull requests
- ✅ Rollback instantáneo si hay problemas

Para actualizar el sitio:
```powershell
git add .
git commit -m "Update content"
git push origin main
```

Vercel desplegará los cambios automáticamente en ~1 minuto.

---

## 🌐 Custom Domain (Opcional)

### Agregar un dominio personalizado:

1. **En Vercel Dashboard**
   - Ve a tu proyecto → **Settings** → **Domains**
   - Click en **Add**
   - Ingresa tu dominio (ej: `aip-c01.tudominio.com`)

2. **Configura DNS**
   - Vercel te dará instrucciones específicas
   - Generalmente necesitas agregar un registro CNAME:
     ```
     CNAME  aip-c01  cname.vercel-dns.com
     ```

3. **Espera propagación DNS** (puede tomar hasta 48 horas)

4. **Vercel automáticamente proveerá SSL/TLS** con Let's Encrypt

---

## 🧪 Testing Local con Vercel Dev

Para probar localmente con el entorno de Vercel:

```powershell
# Instala Vercel CLI si no lo tienes
npm install -g vercel

# Inicia el servidor de desarrollo
cd c:\GitHub\aip-c01
vercel dev
```

Esto iniciará un servidor local en `http://localhost:3000` que simula el entorno de producción de Vercel.

---

## 🐛 Troubleshooting

### Problema: 404 en rutas internas
**Causa**: Los rewrites no están funcionando
**Solución**: Verifica que `vercel.json` esté en la raíz y contenga las rutas correctas

### Problema: Estilos no se cargan
**Causa**: Posible problema de CORS o CDN
**Solución**: Revisa la consola del navegador. Los CDN de Docsify deberían ser accesibles públicamente

### Problema: Sidebar no aparece
**Causa**: Paths incorrectos en la configuración
**Solución**: Verifica los alias en `index.html` y que los archivos `_sidebar.md` existan

### Problema: Contenido markdown no se renderiza
**Causa**: Path incorrecto al contenido
**Solución**: Verifica que `homepage: 'study/README.md'` apunte al archivo correcto

---

## 📊 Analytics (Opcional)

Para agregar analytics de Vercel:

1. Ve a **Project Settings** → **Analytics**
2. Enable **Web Analytics**
3. Los datos estarán disponibles en el dashboard

Para Google Analytics, agrega a `index.html`:
```html
<script src="https://cdn.jsdelivr.net/npm/docsify@5/dist/plugins/ga.min.js"></script>
<script>
  window.$docsify = {
    // ... otras configs
    ga: 'UA-XXXXXXXXX-X' // Tu tracking ID
  }
</script>
```

---

## 🔒 Variables de Entorno

Si necesitas variables de entorno (por ejemplo, para APIs):

1. En Vercel Dashboard → **Settings** → **Environment Variables**
2. Agrega las variables necesarias
3. Accede desde JavaScript:
   ```javascript
   const apiKey = process.env.API_KEY
   ```

---

## 📈 Límites del Plan Gratuito de Vercel

El plan gratuito (Hobby) incluye:
- ✅ Bandwidth ilimitado
- ✅ 100 GB-Hours de ejecución
- ✅ Despliegues ilimitados
- ✅ SSL automático
- ✅ CDN global
- ✅ 1 proyecto concurrente en build

Para un sitio estático como este (Docsify), el plan gratuito es más que suficiente.

---

## 🔗 URLs útiles

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Documentación Vercel**: https://vercel.com/docs
- **Vercel CLI Docs**: https://vercel.com/docs/cli
- **Status de Vercel**: https://www.vercel-status.com/

---

## ✅ Checklist de Deployment

- [ ] Código pushed a repositorio Git
- [ ] Proyecto importado en Vercel
- [ ] Configuración revisada (no build command necesario)
- [ ] Primer deployment exitoso
- [ ] URL funcional y sitio accesible
- [ ] Navegación entre páginas funciona correctamente
- [ ] Sidebar se muestra correctamente
- [ ] Tema oscuro aplicado
- [ ] Links internos funcionan
- [ ] Configuración de auto-deploy activada
- [ ] (Opcional) Custom domain configurado
- [ ] (Opcional) Analytics configurado

---

**¡Tu sitio de documentación AWS AIP-C01 está listo para producción! 🎉**
