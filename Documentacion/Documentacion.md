# Fase 1 de 3 — Tienda de Autos ("Tienda Most Wanted", nombre provisional)

> **Fase actual: 1 de 3.** Este documento describe el alcance de la Fase 1.
> Las Fases 2 y 3 se definirán más adelante.
>
> Última actualización: 21 de noviembre de 2026
>
> Este documento describe la visión del proyecto **y** el estado real del código en este repositorio. Cuando algo está planificado pero aún no existe, se indica explícitamente.

## Descripción General

Aplicación web dedicada a la venta y cotización de automóviles. El proyecto funciona como un catálogo interactivo donde los usuarios pueden explorar distintos modelos de autos y, si encuentran uno de su interés, iniciar un proceso de compra o solicitud de información mediante un formulario.

El nombre visible en la maqueta actual es **"Tienda Most Wanted"**, aunque sigue siendo un nombre provisional y puede cambiar.

## Objetivo del Proyecto

Ofrecer una plataforma intuitiva y segura que facilite la conexión entre compradores y el concesionario. El usuario final debe poder conocer las características de los vehículos y completar una solicitud de compra o reserva de forma digital, agilizando el proceso tradicional.

## Público Objetivo

Cualquier persona interesada en adquirir un vehículo de manera digital, con una experiencia de navegación sencilla, clara y accesible desde cualquier navegador web.

## Funcionalidades

### Implementadas actualmente

1. **CRUD de tareas (prueba técnica de MongoDB)**
   - Ruta `/` (`gestionar_tareas`): lista tareas y permite crear una nueva.
   - Ruta `/completar/<id>`: cambia el estado completada/pendiente.
   - Ruta `/eliminar/<id>`: elimina la tarea.
   - Usa el modelo `Tarea` sobre MongoDB mediante MongoEngine.
   - Nota: es un módulo de prueba heredado del arranque del proyecto; no forma parte del flujo de la tienda.

2. **Página de inicio provisional (maqueta)**
   - Ruta `/index_prov/` (`index_prov`).
   - Plantilla estática `index_prov.html` con header, hero, tres autos de ejemplo escritos a mano y footer.
   - No consume datos de la base de datos.

3. **Catálogo de vehículos (primera versión)**
   - Ruta `/producto/` (`Producto`).
   - Plantilla `producto.html` que recorre los documentos del modelo `Autos`.
   - Muestra imagen, nombre y precio; el botón "Agregar al carrito" todavía no tiene lógica.

4. **Panel de administración de Django**
   - Ruta `/admin/`, habilitada, pero sin modelos registrados (`admin.py` está vacío).

### Planificadas / pendientes

1. **Gestión de usuarios (login y registro)**
   - Identificar usuarios, personalizar la experiencia y vincular los datos de compra a su perfil.
   - Estado: no implementado.

2. **Catálogo completo con ficha de producto**
   - Información ampliada por vehículo (año, características, fotografías múltiples).
   - Estado: el catálogo existe, la ficha individual no.

3. **Carrito de compras**
   - Los botones "Agregar al carrito" son visuales, sin comportamiento.
   - Estado: no implementado.

4. **Proceso de compra / cotización**
   - Formulario con datos personales y de contacto para confirmar intención de compra o solicitar información.
   - Estado: no implementado.

## Tecnologías Utilizadas

| Tecnología | Versión | Uso en el proyecto |
|---|---|---|
| Python | 3.12 | Lenguaje principal |
| Django | 6.1.3 | Framework web, enrutamiento, plantillas, mensajes |
| MongoEngine | 0.29.3 | ODM para modelar documentos sobre MongoDB |
| PyMongo | 4.19.0 | Driver de MongoDB usado por MongoEngine |
| MongoDB | Local en `127.0.0.1:27017` | Base de datos NoSQL `proyecto_clase` |
| HTML + CSS | — | Plantillas Django y estilos en `styles.css` |

Django se organiza en "apps". La única app de negocio actual es `inicio`; en el futuro se prevé separar usuarios, autos y compras en apps independientes.

## Arquitectura del Sistema (MVC)

El proyecto sigue el patrón MVC adaptado al ecosistema Django:

- **Modelo (Model):** representación de los datos. En este proyecto se define con MongoEngine en `inicio/models.py` (`Tarea` y `Autos`), no con el ORM relacional de Django.
- **Vista (View):** lo que el usuario ve en el navegador. Corresponde a las plantillas HTML (`inicio/templates/inicio/`) y al diseño visual (`inicio/static/inicio/styles.css`).
- **Controlador (Controller):** lógica que conecta vista y modelo. En Django son las funciones de `inicio/views.py` junto con el enrutamiento de `Miproyecto/urls.py`.

> Nota: Django denomina "views" a lo que en MVC estricto es el controlador, y "templates" a la vista. La documentación usa la equivalencia anterior para mantener el lenguaje del proyecto.

## Estructura del Proyecto

```text
proyecto-mvc-django/
├── manage.py
├── .gitignore
├── Documentacion/
│   ├── Documentacion.md          # este documento
│   └── Documentacion_IA.md       # guía técnica para agentes/IA
├── Miproyecto/                   # configuración del proyecto Django
│   ├── settings.py               # apps, plantillas, conexión a MongoDB
│   ├── urls.py                   # rutas raíz
│   ├── wsgi.py
│   └── asgi.py
└── inicio/                       # app principal
    ├── models.py                 # modelos MongoEngine
    ├── views.py                  # controladores
    ├── admin.py                  # vacío
    ├── tests.py                  # vacío
    ├── apps.py
    ├── migrations/
    │   └── 0001_initial.py       # migración relacional heredada
    ├── templates/inicio/
    │   ├── index.html            # CRUD de tareas
    │   ├── index_prov.html       # maqueta de la tienda
    │   └── producto.html         # catálogo dinámico
    └── static/inicio/
        ├── styles.css
        └── images/               # 39 imágenes PNG de vehículos
```

## Modelos de Datos

Definidos con MongoEngine en `inicio/models.py`:

### `Tarea`

| Campo | Tipo | Notas |
|---|---|---|
| `titulo` | `StringField(max_length=100)` | Obligatorio |
| `descipcion` | `StringField` | Opcional; el nombre tiene un typo (debería ser `descripcion`) |
| `completada` | `BooleanField` | Por defecto `False` |

### `Autos`

| Campo | Tipo | Notas |
|---|---|---|
| `nombre` | `StringField(max_length=100)` | Obligatorio |
| `precio` | `IntField` | Opcional |
| `imagen` | `StringField` | Opcional; se espera el nombre de archivo dentro de `static/inicio/images/` |

## Rutas y Vistas

| Ruta | Vista | Nombre | Descripción |
|---|---|---|---|
| `/` | `gestionar_tareas` | `inicio` | Lista y crea tareas (MongoDB) |
| `/completar/<str:tarea_id>` | `completar_tarea` | `completar` | Alterna el estado de una tarea |
| `/eliminar/<str:tarea_id>` | `eliminar_tarea` | `eliminar` | Elimina una tarea |
| `/index_prov/` | `index_prov` | `vista_prov` | Maqueta estática de la tienda |
| `/producto/` | `Producto` | `producto` | Catálogo desde el modelo `Autos` |
| `/admin/` | — | — | Admin de Django (sin modelos registrados) |

## Manejo de Errores

### Estado actual

- Las vistas de tareas (`gestionar_tareas`, `completar_tarea`, `eliminar_tarea`) usan `try/except` y reportan el resultado con `django.contrib.messages` (`success`, `error`, `warning`).
- `index.html` muestra los mensajes con clases CSS `.alerta-<tag>` (`.alerta-success`, `.alerta-error`, `.alerta-warning`).
- `gestionar_tareas` captura fallos de conexión a MongoDB con el mensaje "Error crítico: No se pudo conectar a MongoDB".
- Limitaciones actuales:
  - Uso de `except Exception` genérico.
  - En `gestionar_tareas` un error de guardado se reporta con `messages.success` en lugar de `messages.error`.
  - La vista `Producto` no tiene `try/except`.
  - No hay configuración de `LOGGING`.
  - No hay páginas personalizadas `404`/`500` (`handler404`, `handler500`).
  - `DEBUG = True` en desarrollo.

### Estándar definido para el proyecto

1. **Acceso a datos:** toda operación contra MongoDB (`objects`, `save`, `delete`) debe ir dentro de `try/except`.
2. **Excepciones específicas:** capturar excepciones de MongoEngine/PyMongo cuando sea posible; `except Exception` solo como red de seguridad final.
3. **Mensaje al usuario:** usar `messages.error` o `messages.warning` para fallos y `messages.success` únicamente para operaciones exitosas.
4. **Registro técnico:** registrar el error con `logging.getLogger(__name__)` y `logger.exception(...)`; no exponer `str(e)` ni trazas al usuario final.
5. **Validación:** validar los datos en el servidor antes de guardar; el atributo HTML `required` no sustituye la validación.
6. **Producción:** `DEBUG = False`, `ALLOWED_HOSTS` configurado y manejadores `handler404`/`handler500` con plantillas propias.
7. **Consistencia visual:** todo mensaje debe renderizarse con el bloque `{% if messages %}` y las clases `.alerta-<tag>` ya existentes.

### Pendientes

- Configurar `LOGGING` en `Miproyecto/settings.py`.
- Corregir el uso de `messages.success` para errores.
- Envolver la vista `Producto` en manejo de errores.
- Crear plantillas `404.html` y `500.html` y registrar los handlers.

## Configuración Relevante

- **Base de datos:** la conexión se realiza al importar `settings.py` con `mongoengine.connect('proyecto_clase', host='127.0.0.1', port=27017)`. El proyecto requiere un MongoDB local en ejecución.
- **Plantillas:** `APP_DIRS = True`, por lo que Django busca en `inicio/templates/`.
- **Estáticos:** `STATIC_URL = 'static/'`, archivos en `inicio/static/inicio/`.
- **Idioma/zona:** `LANGUAGE_CODE = 'en-us'`, `TIME_ZONE = 'UTC'`.
- **Correo:** backend de consola (`django.core.mail.backends.console.EmailBackend`).
- **Modo desarrollo:** `DEBUG = True` y `SECRET_KEY` embebida; no apto para producción tal cual.

## Estado de la Fase 1 y Deudas Técnicas

Elementos detectados en el código que conviene resolver en fases posteriores:

1. **Migración relacional obsoleta:** `inicio/migrations/0001_initial.py` crea una tabla `Tarea` para el ORM de Django, pero los modelos reales son MongoEngine. La migración no representa el estado actual.
2. **`DATABASES` sin configurar:** Django no define una base relacional, por lo que `admin`, `auth`, `sessions` y `migrate` no están operativos sin configuración adicional.
3. **Error en `completar_tarea` y `eliminar_tarea`:** usan `Tarea.object(...)` en lugar de `Tarea.objects(...)`; la excepción se captura y se muestra un mensaje de error, por lo que esas acciones no funcionan.
4. **Plantillas incompletas:**
   - `index.html` abre `<ul>` pero no genera `<li>` por tarea y no cierra la lista.
   - `producto.html` no carga `styles.css` y no cierra `</div>`, `</body>` ni `</html>`.
5. **CSS:**
   - El selector `.footer a:hover` no coincide con el `<footer>` (no tiene clase `footer`).
   - El hero usa rutas absolutas `/static/inicio/images/...` en lugar de `{% static %}`.
6. **Modelo `Tarea`:** método `str` en lugar de `__str__` y campo `descipcion` con typo.
7. **Sin `requirements.txt`:** las versiones dependen del entorno virtual local.
8. **`admin.py` y `tests.py` vacíos:** no hay modelos registrados ni pruebas automatizadas.
9. **Código de tareas heredado:** `/` muestra el CRUD de tareas en lugar de la tienda; la maqueta vive en `/index_prov/`.
10. **Manejo de errores incompleto:** `except Exception` genérico, sin `LOGGING`, `/producto/` sin `try/except` y sin `handler404`/`handler500`.

## Nota sobre el Alcance y Evolución del Proyecto

Este documento representa la visión del proyecto y su estado en un momento dado; no es definitivo. Funcionalidades, tecnologías, flujos y estructura están sujetos a cambios. A medida que el proyecto avance se podrán añadir características nuevas o descartar las que no resulten viables. Debe entenderse como una guía flexible y en constante evolución.
