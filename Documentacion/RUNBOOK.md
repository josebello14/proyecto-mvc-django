# RUNBOOK — Operación local del proyecto

> **Proyecto:** Tienda de Autos ("Tienda Most Wanted", nombre provisional)
> **Fase:** 1 de 3
> **Ámbito:** entorno local de desarrollo (Linux)
> **Última actualización:** 21 de noviembre de 2026
>
> Documento operativo: cómo instalar, arrancar, verificar y mantener el proyecto.
> Para el contexto técnico ver `Documentacion.md` y `Documentacion_IA.md`.
> Para validar este runbook paso a paso ver `HARNESS.md`.

---

## 1. Propósito y alcance

Este runbook permite levantar el proyecto desde cero en una máquina local y comprobar que funciona.

**Incluye:**
- Instalación de dependencias en un entorno virtual.
- Arranque de MongoDB y de Django.
- Verificación de las rutas existentes.
- Operaciones básicas sobre MongoDB.
- Diagnóstico de fallos frecuentes.
- Copia de seguridad, restauración y despliegue de referencia.

**No incluye (no existe todavía):**
- Login, registro o perfiles de usuario.
- Carrito de compras.
- Formulario de compra/cotización.
- Ficha individual de vehículo.
- Despliegue en producción real.

> **Advertencia:** el proyecto está en fase de desarrollo. `DEBUG = True`, la `SECRET_KEY` está embebida y no hay configuración de producción. No exponerlo a Internet.

---

## 2. Requisitos previos

| Requisito | Versión / valor | Cómo comprobarlo |
|---|---|---|
| Sistema operativo | Linux (probado en Ubuntu) | `uname -a` |
| Python | 3.12.x (probado 3.12.3) | `python3.12 --version` |
| pip | Incluido con Python | `python3.12 -m pip --version` |
| MongoDB | Servidor local | `mongod --version` |
| MongoDB Shell | `mongosh` | `mongosh --version` |
| Git | Cualquiera reciente | `git --version` |
| Puerto 27017 | Libre / ocupado por `mongod` | `ss -ltn \| grep 27017` |
| Puerto 8000 | Libre para Django | `ss -ltn \| grep 8000` |

---

## 3. Instalación desde cero

> El repositorio **no incluye `requirements.txt`**. Las versiones se fijan manualmente aquí para reproducir el entorno actual.

```bash
# 1. Clonar el repositorio
git clone https://github.com/josebello14/proyecto-mvc-django.git
cd proyecto-mvc-django

# 2. Crear y activar el entorno virtual
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Actualizar pip e instalar dependencias con versiones fijadas
python -m pip install --upgrade pip
pip install Django==6.1.3 mongoengine==0.29.3 pymongo==4.19.0

# 4. Verificar versiones instaladas
python -c "import django, mongoengine, pymongo; print(django.get_version(), mongoengine.__version__, pymongo.version)"
```

Salida esperada:

```text
6.1.3 0.29.3 4.19.0
```

Dependencias transitivas que aparecerán instaladas: `asgiref`, `sqlparse`, `dnspython`.

---

## 4. Configuración

La configuración vive en `Miproyecto/settings.py`. No hay archivo `.env` ni variables de entorno.

| Parámetro | Valor actual | Ubicación |
|---|---|---|
| Base de datos | `proyecto_clase` | `settings.py` |
| Host MongoDB | `127.0.0.1` | `settings.py` |
| Puerto MongoDB | `27017` | `settings.py` |
| `DEBUG` | `True` | `settings.py` |
| `ALLOWED_HOSTS` | `[]` | `settings.py` |
| `LANGUAGE_CODE` | `en-us` | `settings.py` |
| `TIME_ZONE` | `UTC` | `settings.py` |
| `STATIC_URL` | `static/` | `settings.py` |
| App de negocio | `inicio` | `INSTALLED_APPS` |

La conexión se ejecuta **al importar** `settings.py`:

```python
mongoengine.connect('proyecto_clase', host='127.0.0.1', port=27017)
```

> **Importante:** no hay `DATABASES` de Django configurada. Por eso `admin`, `auth`, `sessions` y `migrate` no son operativos. Los datos reales viven en MongoDB.

---

## 5. Arranque

### 5.1 Iniciar MongoDB

```bash
# Opción A: servicio del sistema
sudo systemctl status mongod
sudo systemctl start mongod

# Opción B: arranque manual (si no hay servicio)
mkdir -p ~/mongodb-data
mongod --dbpath ~/mongodb-data
```

Verificar que responde:

```bash
mongosh --quiet --eval "db.adminCommand({ping:1})"
```

Salida esperada:

```text
{ ok: 1 }
```

### 5.2 Iniciar Django

```bash
cd /ruta/al/proyecto-mvc-django
source .venv/bin/activate
python manage.py runserver
```

Salida esperada (resumen):

```text
System check identified no issues (0 silenced).
Django version 6.1.3, using settings 'Miproyecto.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Si el puerto 8000 está ocupado:

```bash
python manage.py runserver 127.0.0.1:8001
```

---

## 6. Verificación de rutas

Con el servidor en marcha, comprobar:

| Ruta | Vista | Resultado esperado |
|---|---|---|
| `/` | `gestionar_tareas` | `200` + "Mis Tareas (CRUD NoSQL)" |
| `/index_prov/` | `index_prov` | `200` + "Bienvenido a nuestro sitio web" |
| `/producto/` | `Producto` | `200` + "Producto" y los autos de MongoDB |
| `/admin/` | Admin Django | `302` hacia `/admin/login/`; el login **no** es operativo sin `DATABASES` |
| `/completar/<id>` | `completar_tarea` | `302`, pero **no cambia el estado** (bug conocido) |
| `/eliminar/<id>` | `eliminar_tarea` | `302`, pero **no elimina** (bug conocido) |
| Ruta inexistente | — | `404` |

Comprobación rápida por terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/index_prov/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/producto/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/admin/
```

---

## 7. Operación con MongoDB

### 7.1 Abrir la shell

```bash
mongosh
```

### 7.2 Consultas básicas

```javascript
use proyecto_clase
show collections
db.autos.find().pretty()
db.autos.countDocuments()
db.tarea.find().pretty()
```

Colecciones esperadas:

| Colección | Modelo | Cuándo existe |
|---|---|---|
| `autos` | `Autos` | Desde que se inserta el primer auto |
| `tarea` | `Tarea` | Desde que se crea la primera tarea |

### 7.3 Insertar un auto de ejemplo

El campo `imagen` debe coincidir con un archivo de `inicio/static/inicio/images/`:

```javascript
db.autos.insertOne({
  nombre: "Aston Martin DB9",
  precio: 90000,
  imagen: "1 - CbMZAfn.png"
})
```

### 7.4 Crear una tarea desde la aplicación

1. Abrir `http://127.0.0.1:8000/`.
2. Escribir un título y pulsar "Guardar".
3. Verificar en MongoDB:

```javascript
db.tarea.find({ titulo: "prueba-harness" }).pretty()
```

---

## 8. Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'django'` | Entorno virtual no activado | `source .venv/bin/activate` |
| `ServerSelectionTimeoutError` o consultas que fallan | MongoDB detenido | `sudo systemctl start mongod` y verificar `ping` |
| "Error crítico: No se pudo conectar a MongoDB" | MongoDB detenido o puerto incorrecto | Revisar `mongod` y `settings.py` |
| `That port is already in use.` | Puerto 8000 ocupado | `python manage.py runserver 8001` o detener el proceso |
| `/admin/` da error tras el login | No hay `DATABASES` | No usar el admin en esta fase |
| `/completar/<id>` no cambia el estado | `Tarea.object` en lugar de `Tarea.objects` | Bug conocido; requiere corrección de código |
| `/eliminar/<id>` no elimina | `Tarea.object` en lugar de `Tarea.objects` | Bug conocido; requiere corrección de código |
| Imágenes del catálogo rotas | `imagen` no coincide con el archivo | Revisar `inicio/static/inicio/images/` |
| `DisallowedHost` | `ALLOWED_HOSTS` vacío con `DEBUG=False` | Añadir el host o mantener `DEBUG=True` en local |
| `migrate` falla o no refleja los modelos | Migración SQL obsoleta | No usar `migrate`; los datos están en MongoDB |

---

## 9. Mantenimiento

### 9.1 Copia de seguridad

```bash
mkdir -p ~/backups
mongodump --db proyecto_clase --out ~/backups/$(date +%F)
```

### 9.2 Restauración

```bash
mongorestore --db proyecto_clase --drop ~/backups/2026-11-21/proyecto_clase
```

### 9.3 Exportar una colección

```bash
mongoexport --db proyecto_clase --collection autos --out ~/backups/autos.json
```

### 9.4 Reiniciar la base de datos

> **Destructivo:** elimina todos los datos de `proyecto_clase`.

```bash
mongosh proyecto_clase --eval "db.dropDatabase()"
```

---

## 10. Despliegue de referencia y rollback

El proyecto **no está listo para producción**. Antes de plantearlo, como mínimo:

- [ ] `DEBUG = False`.
- [ ] `ALLOWED_HOSTS` con el dominio real.
- [ ] `SECRET_KEY` desde variable de entorno, no en el código.
- [ ] `python manage.py collectstatic` y servidor de estáticos.
- [ ] Servidor WSGI/ASGI (Gunicorn/Uvicorn **no instalados** actualmente).
- [ ] MongoDB con autenticación, backups y acceso restringido.
- [ ] `requirements.txt` con versiones fijadas.
- [ ] Corregir los bugs conocidos y añadir pruebas.

### Rollback

1. Detener el servidor de aplicación.
2. Volver a la revisión anterior: `git checkout <commit-o-tag>`.
3. Restaurar el backup de MongoDB si hubo cambios de datos:
   ```bash
   mongorestore --db proyecto_clase --drop <ruta-del-backup>/proyecto_clase
   ```
4. Reinstalar dependencias si cambiaron y volver a arrancar.

---

## 11. Referencias

- `Documentacion/Documentacion.md` — visión, estado y deudas técnicas.
- `Documentacion/Documentacion_IA.md` — contexto operativo para agentes/IA.
- `Documentacion/HARNESS.md` — arnés de validación de este runbook.
- Django 6.1: <https://docs.djangoproject.com/en/6.1/>
- MongoEngine: <https://docs.mongoengine.org/>
