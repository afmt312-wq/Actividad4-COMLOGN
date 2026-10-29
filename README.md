# README

## Propósito

Implementar el núcleo de negocio de una tienda en línea con entidades y Value Objects que protegen sus invariantes, reglas de descuento con el patrón Specification (AND/OR/NOT), una máquina de estados con Domain Events y una API REST con FastAPI.

## Problema que resuelve

Evita que se confirmen pedidos inválidos (vacíos, de clientes inactivos o con más de 20 unidades), aplica descuentos de forma consistente y rechaza transiciones de estado prohibidas, de modo que las reglas viven en el dominio y no en la interfaz. Los datos se cargan desde CSV y se manejan en memoria; al cerrar el programa, los cambios se pierden.

## Reglas principales

- Límite de 20 unidades por pedido (suma de cantidades, no de renglones).
- Descuento de 10 %: total > 500, cliente VIP, al menos 4 unidades y sin promoción activa.
- Descuento de 5 %: total > 5000 y sin promoción activa.
- Si se cumplen ambos, se aplica el 10 %.
- Estados: DRAFT → CONFIRMED → SHIPPED → DELIVERED; CONFIRMED → CANCELLED; SHIPPED → RETURNED.
- Una operación inválida no cambia el estado ni agrega eventos.

## Requisitos

- Python 3.11 o superior.
- Dependencias: fastapi, uvicorn, pytest y httpx.
- No requiere base de datos ni permisos de administrador.

## Instrucciones de uso

```bash
# 1. Entorno virtual
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD:        .venv\Scripts\activate.bat
# macOS / Linux:      source .venv/bin/activate

# 2. Dependencias
python -m pip install fastapi uvicorn pytest httpx

# 3. Verificar la carga de datos (16 pedidos en DRAFT)
python cargar_csv.py

# 4. Ejecutar los 15 escenarios
python ejecutar_escenarios.py

# 5. Pruebas automáticas
python -m pytest -q

# 6. Levantar la API
uvicorn app.api:app --reload
```

Documentación: http://127.0.0.1:8000/docs

## Endpoints

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | /orders/{id} | Consulta un pedido | 200, 404 |
| POST | /orders/{id}/confirm | Confirma el pedido | 200, 404, 409, 422 |
| POST | /orders/{id}/ship | Envía (body: tracking_number) | 200, 404, 409, 422 |
| POST | /orders/{id}/cancel | Cancela (body: reason) | 200, 404, 409, 422 |

## Estructura del proyecto

```
techstore-u4/
  datos/            # CSV de clientes, productos, pedidos, detalle y escenarios
  cargar_csv.py
  ejecutar_escenarios.py
  app/
    __init__.py
    domain.py
    specifications.py
    api.py
```
