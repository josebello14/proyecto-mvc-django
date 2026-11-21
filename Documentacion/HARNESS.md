# HARNESS — Arnés de validación del RUNBOOK

> **Proyecto:** Tienda de Autos ("Tienda Most Wanted", nombre provisional)
> **Fase:** 1 de 3
> **Ámbito:** validación manual/asistida del runbook en local
> **Última actualización:** 21 de noviembre de 2026
>
> Este documento **no es un conjunto de pruebas automatizadas**. Es un protocolo que verifica que cada paso de `RUNBOOK.md` se ejecuta y produce el resultado esperado.
> No modifica código. Algunos checks escriben datos temporales en MongoDB; se limpian en la sección 7.

---

## 1. Propósito

Comprobar, de forma repetible, que:

1. El entorno se instala y arranca según `RUNBOOK.md`.
2. Las rutas existentes responden con el comportamiento documentado.
3. MongoDB contiene las colecciones esperadas.
4. Los fallos conocidos siguen identificados y no se confunden con regresiones nuevas.

Cada check devuelve uno de estos estados:

| Estado | Significado |
|---|---|
| **PASS** | El resultado coincide con lo esperado. |
| **FAIL** | El resultado no coincide y no estaba documentado como fallo conocido. |
| **FAIL CONOCIDO** | Falla tal como se documentó en `Documentacion.md`; no es una regresión nueva. |
| **SKIP** | No se ejecutó (opcional, destructivo o requiere intervención manual). |

---

## 2. Convenciones

- Ejecutar desde la raíz del repositorio, salvo que se indique otra cosa.
- Usar `bash` en Linux.
- Registrar cada resultado en la tabla de evidencia (sección 6).
- No ejecutar los checks destructivos (H-17, H-18) en un entorno con datos reales.
- Si un check falla, detenerse, corregir y repetir desde el check anterior.

Preparación de la sesión:

```bash
cd /ruta/al/proyecto-mvc-django
source .venv/bin/activate
export BASE_URL="http://127.0.0.1:8000"
```

---

## 3. Matriz de verificación

| ID | Check | Resultado esperado | Tipo |
|---|---|---|---|
| H-01 | Versión de Python | `Python 3.12.3` | PASS/FAIL |
| H-02 | Entorno virtual activo | `python` apunta a `.venv/bin/python` | PASS/FAIL |
| H-03 | Versiones de paquetes | `6.1.3 0.29.3 4.19.0` | PASS/FAIL |
| H-04 | MongoDB responde | `{ ok: 1 }` | PASS/FAIL |
| H-05 | Archivos clave presentes | `OK` | PASS/FAIL |
| H-06 | `manage.py check` | `System check identified no issues` | PASS/FAIL |
| H-07 | Servidor arranca | HTTP `200` en `/` | PASS/FAIL |
| H-08 | Ruta `/` | Contiene "Mis Tareas" | PASS/FAIL |
| H-09 | Ruta `/index_prov/` | Contiene "Bienvenido a nuestro sitio web" | PASS/FAIL |
| H-10 | Ruta `/producto/` | HTTP `200` + "Producto" | PASS/FAIL |
| H-11 | Ruta `/admin/` | HTTP `302` | PASS/FAIL |
| H-12 | Crear tarea | Documento en `db.tarea` | PASS/FAIL |
| H-13 | `/completar/<id>` | Estado sin cambios | FAIL CONOCIDO |
| H-14 | `/eliminar/<id>` | Documento sigue existiendo | FAIL CONOCIDO |
| H-15 | Ruta inexistente | HTTP `404` | PASS/FAIL |
| H-16 | Backup/restore en seco | Conteos coinciden | PASS/FAIL |
| H-17 | MongoDB detenido | `/producto/` falla | SKIP (opcional) |
| H-18 | Puerto ocupado | Error de puerto en uso | SKIP (opcional) |

---

## 4. Procedimientos

### H-01 — Versión de Python

```bash
python --version
```

Esperado: `Python 3.12.3` (o 3.12.x).

---

### H-02 — Entorno virtual activo

```bash
which python
```

Esperado: una ruta que contenga `/proyecto-mvc-django/.venv/bin/python`.

---

### H-03 — Versiones de paquetes

```bash
python -c "import django, mongoengine, pymongo; print(django.get_version(), mongoengine.__version__, pymongo.version)"
```

Esperado:

```text
6.1.3 0.29.3 4.19.0
```

---

### H-04 — MongoDB responde

```bash
mongosh --quiet --eval "db.adminCommand({ping:1})"
```

Esperado:

```text
{ ok: 1 }
```

Si falla: iniciar MongoDB según `RUNBOOK.md` §5.1.

---

### H-05 — Archivos clave presentes

```bash
test -f manage.py \
  && test -f Miproyecto/settings.py \
  && test -f Miproyecto/urls.py \
  && test -f inicio/models.py \
  && test -f inicio/views.py \
  && test -f inicio/templates/inicio/index.html \
  && test -f inicio/templates/inicio/index_prov.html \
  && test -f inicio/templates/inicio/producto.html \
  && test -f inicio/static/inicio/styles.css \
  && echo OK
```

Esperado: `OK`.

---

### H-06 — `manage.py check`

```bash
python manage.py check
```

Esperado:

```text
System check identified no issues (0 silenced).
```

Código de salida esperado: `0`.

---

### H-07 — Servidor arranca

En una terminal:

```bash
python manage.py runserver 127.0.0.1:8000
```

En otra terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/"
```

Esperado: `200`.

> Mantener el servidor en marcha para H-08 a H-15.

---

### H-08 — Ruta `/`

```bash
curl -s "$BASE_URL/" | grep -q "Mis Tareas" && echo PASS || echo FAIL
```

Esperado: `PASS`.

---

### H-09 — Ruta `/index_prov/`

```bash
curl -s "$BASE_URL/index_prov/" | grep -q "Bienvenido a nuestro sitio web" && echo PASS || echo FAIL
```

Esperado: `PASS`.

---

### H-10 — Ruta `/producto/`

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/producto/"
curl -s "$BASE_URL/producto/" | grep -q "Producto" && echo PASS || echo FAIL
```

Esperado: `200` y `PASS`.

Si la base tiene autos, además debe aparecer su nombre. Estado actual de referencia: 1 documento en `autos` (`Aston Martin DB9`).

---

### H-11 — Ruta `/admin/`

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/admin/"
```

Esperado: `302` (redirección a `/admin/login/`).

> El login del admin **no es operativo** porque no hay `DATABASES` configurada. Un error tras seguir la redirección es el comportamiento conocido, no una regresión.

---

### H-12 — Crear tarea

Procedimiento manual:

1. Abrir `http://127.0.0.1:8000/`.
2. Escribir el título `prueba-harness` y pulsar "Guardar".
3. Verificar en MongoDB:

```bash
mongosh proyecto_clase --quiet --eval "print(db.tarea.countDocuments({titulo:'prueba-harness'}))"
```

Esperado: `1`.

> Este check escribe en la base. La limpieza está en la sección 7.

---

### H-13 — `/completar/<id>` (FAIL CONOCIDO)

Obtener el id de la tarea de prueba:

```bash
ID=$(mongosh proyecto_clase --quiet --eval "print(db.tarea.findOne({titulo:'prueba-harness'})._id.toString())")
echo "$ID"
```

Estado antes:

```bash
mongosh proyecto_clase --quiet --eval "print(db.tarea.findOne({titulo:'prueba-harness'}).completada)"
```

Ejecutar la ruta:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/completar/$ID"
```

Esperado: `302`.

Estado después:

```bash
mongosh proyecto_clase --quiet --eval "print(db.tarea.findOne({titulo:'prueba-harness'}).completada)"
```

Resultado esperado según el estado actual del código: **el valor no cambia** (`false` → `false`).
Motivo: `completar_tarea` usa `Tarea.object(...)` en lugar de `Tarea.objects(...)`.

Clasificación: **FAIL CONOCIDO**.

---

### H-14 — `/eliminar/<id>` (FAIL CONOCIDO)

Con el mismo `ID` de H-13:

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/eliminar/$ID"
```

Esperado: `302`.

Comprobar que el documento sigue existiendo:

```bash
mongosh proyecto_clase --quiet --eval "print(db.tarea.countDocuments({titulo:'prueba-harness'}))"
```

Resultado esperado según el estado actual del código: **`1`** (no se elimina).
Motivo: `eliminar_tarea` usa `Tarea.object(...)`.

Clasificación: **FAIL CONOCIDO**.

---

### H-15 — Ruta inexistente

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/ruta-que-no-existe/"
```

Esperado: `404`.

---

### H-16 — Backup/restore en seco

```bash
rm -rf /tmp/harness-backup
mkdir -p /tmp/harness-backup

# 1. Backup
mongodump --db proyecto_clase --out /tmp/harness-backup

# 2. Restaurar en una base temporal
mongorestore \
  --nsFrom 'proyecto_clase.*' \
  --nsTo 'proyecto_clase_harness.*' \
  /tmp/harness-backup/proyecto_clase

# 3. Comparar conteos
mongosh proyecto_clase --quiet --eval "print('origen:', db.autos.countDocuments())"
mongosh proyecto_clase_harness --quiet --eval "print('temporal:', db.autos.countDocuments())"

# 4. Limpiar la base temporal
mongosh --quiet --eval "db.getSiblingDB('proyecto_clase_harness').dropDatabase()"
```

Esperado: ambos conteos coinciden y la base temporal se elimina sin error.

---

### H-17 — MongoDB detenido (opcional, destructivo)

> Solo en un entorno de pruebas. Afecta a todo el sistema que use ese MongoDB.

1. Detener MongoDB:
   ```bash
   sudo systemctl stop mongod
   ```
2. Pedir `/producto/`:
   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" "$BASE_URL/producto/"
   ```
   Esperado: error `500` (la vista `Producto` no captura la excepción).
3. Reiniciar MongoDB:
   ```bash
   sudo systemctl start mongod
   ```
4. Repetir H-04 y H-10 para confirmar recuperación.

Clasificación por defecto: **SKIP** (no ejecutar en la validación estándar).

---

### H-18 — Puerto ocupado (opcional)

Con el servidor de H-07 en marcha, intentar un segundo arranque:

```bash
python manage.py runserver 127.0.0.1:8000
```

Esperado: mensaje `That port is already in use.` y salida distinta de `0`.

Clasificación por defecto: **SKIP**.

---

## 5. Criterios de aprobación

La validación se considera **APROBADA** si:

- H-01 a H-12, H-15 y H-16 están en **PASS**.
- H-13 y H-14 están en **FAIL CONOCIDO**.
- H-17 y H-18 pueden quedar en **SKIP**.
- No hay ningún **FAIL** sin justificar.

Cualquier **FAIL** nuevo debe registrarse como incidencia y actualizar `Documentacion.md` y `Documentacion_IA.md` si cambia el estado del proyecto.

---

## 6. Registro de evidencia

Completar una fila por check:

| ID | Fecha | Ejecutor | Resultado | Evidencia / observaciones |
|---|---|---|---|---|
| H-01 | | | | |
| H-02 | | | | |
| H-03 | | | | |
| H-04 | | | | |
| H-05 | | | | |
| H-06 | | | | |
| H-07 | | | | |
| H-08 | | | | |
| H-09 | | | | |
| H-10 | | | | |
| H-11 | | | | |
| H-12 | | | | |
| H-13 | | | | |
| H-14 | | | | |
| H-15 | | | | |
| H-16 | | | | |
| H-17 | | | | |
| H-18 | | | | |

---

## 7. Limpieza

Ejecutar al terminar, incluso si la validación falla:

```bash
# 1. Eliminar la tarea de prueba
mongosh proyecto_clase --quiet --eval "db.tarea.deleteMany({titulo:'prueba-harness'})"

# 2. Eliminar backups temporales
rm -rf /tmp/harness-backup

# 3. Eliminar base temporal si quedó creada
mongosh --quiet --eval "db.getSiblingDB('proyecto_clase_harness').dropDatabase()"
```

Detener el servidor de Django con `Ctrl+C` en su terminal.

---

## 8. Certificación

| Campo | Valor |
|---|---|
| Fecha de ejecución | |
| Ejecutor | |
| Versión / commit | `git rev-parse --short HEAD` |
| Checks PASS | |
| Checks FAIL CONOCIDO | |
| Checks FAIL | |
| Veredicto | APROBADO / RECHAZADO |
| Observaciones | |

---

## 9. Limitaciones conocidas del arnés

- No hay suite de pruebas automatizadas en el repositorio (`inicio/tests.py` está vacío).
- H-12, H-13 y H-14 requieren pasos manuales o extracción previa del `id`.
- El admin de Django no se puede validar de extremo a extremo sin `DATABASES`.
- Los checks asumen una instalación local limpia; datos previos en `proyecto_clase` pueden cambiar los conteos.
- H-17 y H-18 son opcionales y potencialmente disruptivos.
