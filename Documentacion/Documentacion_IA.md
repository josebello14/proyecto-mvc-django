# Documentación para IA — Contexto operativo del proyecto

> **Archivo exclusivo para agentes/IA.** No es documentación de usuario final.
> Última actualización: 21 de noviembre de 2026.
>
> Objetivo: que un agente pueda trabajar en este repositorio sin asumir funcionalidades que no existen y sin romper el estado actual.

## 1. Reglas de trabajo

> **Fase actual: 1 de 3.** No asumir ni adelantar funcionalidades de fases
> posteriores (login, carrito, compra/cotización) sin pedido explícito.

1. **No inventar features.** Solo existen las descritas en "Estado real" (sección 5). Login, carrito, ficha de producto y formulario de compra **no están implementados**.
2. **No tocar código si la tarea es solo documental.** Los únicos archivos de documentación son `Documentacion/Documentacion.md` y este archivo.
3. **Respetar el idioma del código existente:** nombres de funciones, variables, rutas y comentarios están en español. Mantener esa convención.
4. **No renombrar campos de modelos existentes** (`titulo`, `descipcion`, `completada`, `nombre`, `precio`, `imagen`) sin autorización: hay documentos potencialmente guardados en MongoDB y migraciones desalineadas.
5. **No añadir dependencias** sin actualizar la tabla de stack en `Documentacion.md`.
6. **No ejecutar `makemigrations`/`migrate` como solución por defecto:** el ORM relacional no es la fuente de verdad; los datos viven en MongoDB vía MongoEngine.
7. **No commitear** `.venv/`, `__pycache__/`, `*.pyc` ni `db.sqlite3` (ya están en `.gitignore`).

## 2. Stack y entorno

| Componente | Versión / valor |
|---|---|
| Python | 3.12 |
| Django | 6.1.3 |
| MongoEngine | 0.29.3 |
| PyMongo | 4.19.0 |
| MongoDB | `127.0.0.1:27017`, base `proyecto_clase` |
| Entorno virtual | `.venv/` en la raíz |

La conexión a MongoDB se ejecuta **al importar** `Miproyecto/settings.py`. Cualquier comando de Django requiere MongoDB disponible o fallará al arrancar.

### Comandos útiles

```bash
source .venv/bin/activate
python manage.py runserver
python manage.py check
python manage.py shell
```

`migrate` solo tiene sentido si antes se configura `DATABASES`; actualmente no lo está. La migración `inicio/migrations/0001_initial.py` está obsoleta respecto a los modelos MongoEngine.

## 3. Mapa de archivos

| Archivo | Rol | Estado |
|---|---|---|
| `manage.py` | Entrada CLI de Django | Estándar |
| `Miproyecto/settings.py` | Configuración + conexión MongoEngine | Funcional |
| `Miproyecto/urls.py` | Rutas raíz | Funcional |
| `Miproyecto/wsgi.py`, `asgi.py` | Puntos de entrada | Estándar |
| `inicio/models.py` | Modelos `Tarea` y `Autos` (MongoEngine) | Funcional con detalles |
| `inicio/views.py` | 6 vistas de función | Parcial (ver bugs) |
| `inicio/admin.py` | Registro en admin | Vacío |
| `inicio/tests.py` | Pruebas | Vacío |
| `inicio/apps.py` | `InicioConfig` | Estándar |
| `inicio/migrations/0001_initial.py` | Migración SQL de `Tarea` | **Obsoleta** |
| `inicio/templates/inicio/index.html` | CRUD de tareas | Con HTML incompleto |
| `inicio/templates/inicio/index_prov.html` | Maqueta estática de la tienda | Funcional |
| `inicio/templates/inicio/producto.html` | Catálogo dinámico | Incompleto (sin CSS ni cierre) |
| `inicio/static/inicio/styles.css` | Estilos de la maqueta | Funcional con detalles |
| `inicio/static/inicio/images/` | 39 PNG de vehículos | Assets |

### Archivos que NO se deben modificar sin pedido explícito

- `Documentacion/Documentacion.md` y `Documentacion/Documentacion_IA.md` (salvo tarea documental).
- `inicio/static/inicio/images/**` (assets binarios).
- `Miproyecto/settings.py` en lo referente a la conexión MongoEngine y `SECRET_KEY`.

## 4. Modelos

```python
# inicio/models.py (resumen)
class Tarea(Document):
    titulo = StringField(max_length=100, required=True)
    descipcion = StringField(blank=True)   # typo real, no corregir sin pedido
    completada = BooleanField(default=False)
    def str(self): ...                     # debería ser __str__

class Autos(Document):
    nombre = StringField(max_length=100, required=True)
    precio = IntField(blank=True)
    imagen = StringField(blank=True)       # nombre de archivo en static/inicio/images/
    def __str__(self): ...
```

- `Tarea` es un módulo de prueba heredado; no pertenece al dominio de la tienda.
- `Autos` alimenta únicamente `/producto/`.

## 5. Estado real vs. pendiente

### Fase actual

**Fase 1 de 3.** Este es el alcance vigente. No asumir ni implementar funcionalidades de las fases 2 y 3 sin pedido explícito.

### Existe y funciona (o debería)

- `/` → listar/crear tareas en MongoDB.
- `/index_prov/` → maqueta estática.
- `/producto/` → listado de `Autos` desde MongoDB.
- `/admin/` → accesible, sin modelos registrados.
- Mensajes de Django (`messages`) en las vistas de tareas.

### No existe (no asumir)

- Login, registro, logout y perfiles de usuario.
- Carrito de compras y su persistencia.
- Formulario de compra/cotización.
- Ficha individual de vehículo (`/producto/<id>/`).
- Búsqueda, filtros, paginación.
- API REST.
- Pruebas automatizadas.
- `requirements.txt`.
- Configuración de `DATABASES` para el ORM de Django.

## 6. Bugs y deudas conocidas

| # | Ubicación | Problema | Impacto |
|---|---|---|---|
| 1 | `inicio/views.py` | `Tarea.object(...)` en `completar_tarea` y `eliminar_tarea` | Las acciones fallan silenciosamente (excepción capturada) |
| 2 | `inicio/templates/inicio/index.html` | Abre `<ul>` sin generar `<li>` y sin cerrar la lista | HTML inválido |
| 3 | `inicio/templates/inicio/producto.html` | No carga `styles.css`; faltan `</div>`, `</body>`, `</html>` | Sin estilos y HTML inválido |
| 4 | `inicio/static/inicio/styles.css` | `.footer a:hover` no coincide con `<footer>` | Hover del footer inactivo |
| 5 | `inicio/static/inicio/styles.css` | Hero con `/static/inicio/images/...` absoluto | Puede fallar si cambia `STATIC_URL` |
| 6 | `inicio/models.py` | `def str` en `Tarea` en lugar de `__str__` | Representación incorrecta |
| 7 | `inicio/models.py` | Campo `descipcion` (typo) | Deuda de nombres |
| 8 | `inicio/migrations/0001_initial.py` | Migración SQL de `Tarea` desalineada con MongoEngine | Confusión al ejecutar `migrate` |
| 9 | `Miproyecto/settings.py` | Sin `DATABASES` | Admin/auth/sessions no operativos |
| 10 | `inicio/views.py` | Errores reportados con `messages.success` | Semántica incorrecta |
| 11 | `Miproyecto/settings.py` | `DEBUG=True`, `SECRET_KEY` embebida, `ALLOWED_HOSTS=[]` | No apto para producción |
| 12 | Raíz `/` | Muestra el CRUD de tareas, no la tienda | La maqueta vive en `/index_prov/` |
| 13 | `inicio/views.py` | `except Exception` genérico y sin `logging` | Errores difíciles de diagnosticar |
| 14 | `inicio/views.py` | La vista `Producto` no tiene `try/except` | La página falla si MongoDB no responde |
| 15 | `Miproyecto/settings.py`, `Miproyecto/urls.py` | Sin `LOGGING` ni `handler404`/`handler500` | Sin trazabilidad ni páginas de error propias |

> Corregir estos puntos requiere una tarea explícita. No los arregles "de paso" si el pedido es otro.

## 7. Rutas (contrato actual)

```text
/admin/                        admin.site.urls
/                              gestionar_tareas   name='inicio'
/completar/<str:tarea_id>      completar_tarea    name='completar'
/eliminar/<str:tarea_id>       eliminar_tarea     name='eliminar'
/index_prov/                   index_prov         name='vista_prov'
/producto/                     Producto           name='producto'
```

Sin slash final en `completar` y `eliminar`; los enlaces usan `{% url %}`.

## 8. Convenciones

- **App única:** `inicio`. Si se añaden apps (usuarios, autos, compras), registrarlas en `INSTALLED_APPS`.
- **Plantillas:** `inicio/templates/inicio/<nombre>.html` (namespace por app).
- **Estáticos:** `inicio/static/inicio/...`; usar `{% load static %}` y `{% static 'inicio/...' %}`.
- **Vistas:** funciones (no CBV) en `inicio/views.py`.
- **Modelos:** MongoEngine `Document`, no `django.db.models.Model`.
- **Mensajes:** `django.contrib.messages` con clases CSS `alerta-<tag>`.
- **Idioma:** español para dominio y UI; identificadores técnicos de Django en inglés.

## 9. Manejo de errores (obligatorio)

1. **Envolver el acceso a datos:** todo uso de MongoEngine (`Modelo.objects`, `.save()`, `.delete()`, `.first()`) debe ir dentro de `try/except`.
2. **Excepciones específicas:** capturar errores de MongoEngine/PyMongo cuando sea posible; `except Exception` solo como red de seguridad final.
3. **Mensajes correctos:** `messages.error` o `messages.warning` para fallos; `messages.success` **solo** para operaciones exitosas. No repetir el bug de `gestionar_tareas`.
4. **No silenciar:** registrar con `logger = logging.getLogger(__name__)` y `logger.exception(...)` antes de devolver el mensaje al usuario.
5. **No filtrar detalles:** nunca mostrar `str(e)`, trazas ni datos internos al usuario final.
6. **Validar en servidor:** comprobar los datos del `request.POST` antes de guardar; `required` en HTML no es validación.
7. **Mantener el patrón visual:** renderizar mensajes con `{% if messages %}` y clases `.alerta-<tag>` (`.alerta-success`, `.alerta-error`, `.alerta-warning`).
8. **Producción:** `DEBUG = False`, `ALLOWED_HOSTS` definido y `handler404`/`handler500` con plantillas `404.html`/`500.html`.

### Pendientes de manejo de errores

- Configurar `LOGGING` en `Miproyecto/settings.py`.
- Corregir `messages.success` usado para errores en `gestionar_tareas`.
- Envolver `Producto` en `try/except`.
- Crear `404.html`, `500.html` y registrar los handlers en `Miproyecto/urls.py`.

## 10. Checklist antes de cambiar código

1. ¿La funcionalidad existe ya? Revisar sección 5.
2. ¿Afecta modelos? Verificar MongoEngine, campos y documentos existentes; no crear migraciones SQL salvo pedido.
3. ¿Afecta rutas? Actualizar `Miproyecto/urls.py` y usar `{% url %}` en plantillas.
4. ¿Afecta plantillas? Mantener `{% load static %}`, `{% csrf_token %}` en formularios y HTML bien cerrado.
5. ¿Afecta estáticos? Respetar `inicio/static/inicio/` y `{% static %}`.
6. ¿Cambia el stack o el estado? Actualizar `Documentacion/Documentacion.md` y este archivo.
7. ¿Se añadió código de prueba? Ubicarlo en `inicio/tests.py`.
8. ¿La nueva vista maneja errores de base de datos, valida la entrada y registra el fallo con `logging`? Revisar sección 9.

## 11. Glosario mínimo

- **Document (MongoEngine):** clase que representa una colección en MongoDB.
- **`objects`:** manager de consultas de MongoEngine (`Modelo.objects`). **No** es `object`.
- **`render(request, template, contexto)`:** devuelve una plantilla renderizada.
- **`{% csrf_token %}`:** token obligatorio en formularios POST.
- **`{% static 'ruta' %}`:** resuelve una URL de archivo estático.
- **`messages`:** sistema de mensajes de una sola petición.
- **MVC en Django:** Modelo = `models.py`; Vista = plantillas; Controlador = `views.py` + `urls.py`.
