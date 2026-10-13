# SaborExpress — Sistema de Gestión de Pedidos

Producto de software (MVC) para el restaurante **SaborExpress**, desarrollado por
**NovaTech Soluciones IT S.A.S**. Implementa las Historias de Usuario 1.1 y el
Backlog por Sprint 1.1: toma de pedidos (mesero), mapa de mesas, cierre y pago
(cajero: efectivo / débito / crédito), reportes con exportación a Excel
(administrador) y parametrización del sistema.

- **Repositorio:** https://github.com/Santi5253/Sabor-Express.git

## Stack

| Capa | Tecnología |
|------|------------|
| Back-end | Python 3.11 · FastAPI · SQLAlchemy 2.0 · PyJWT · bcrypt |
| Base de datos | PostgreSQL 16 (producción) · SQLite (desarrollo) |
| Front-end | HTML5 · CSS3 · JavaScript (Vanilla) |
| Reportes | OpenPyXL (Excel .xlsx) |
| Despliegue | Docker / docker-compose |

## Estructura

```
Producto/
├── backend/
│   ├── app/
│   │   ├── models/       # Modelos ORM (9 tablas)
│   │   ├── schemas/      # Validación Pydantic
│   │   ├── routers/      # Endpoints REST (/api/v1)
│   │   ├── services/     # Lógica de negocio
│   │   ├── middleware/   # Autenticación (JWT) y auditoría
│   │   ├── utils/        # Seguridad y exportación Excel
│   │   ├── config.py     # Configuración (.env)
│   │   ├── database.py   # Conexión SQLAlchemy
│   │   └── main.py       # Punto de entrada FastAPI
│   ├── seed.py           # Datos de prueba
│   ├── smoke_test.py     # Prueba end-to-end del flujo crítico
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
└── frontend/             # Vistas (HTML/CSS/JS)
    ├── login.html
    ├── take-order.html       # HU008-HU013 (mesero)
    ├── my-orders.html        # HU014
    ├── tables.html           # HU013 (mapa de mesas)
    ├── close-and-pay.html    # HU015-HU021 (cajero)
    ├── admin.html            # HU022-HU027 (administrador)
    ├── reports.html          # HU028-HU030 (reportes)
    └── assets/{css,js}
```

## Puesta en marcha (desarrollo, SQLite)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python seed.py                    # carga datos de prueba
python run.py                     # http://localhost:8000
```

Abrir el navegador en <http://localhost:8000> (el back-end sirve también el
front-end estático). Documentación interactiva: <http://localhost:8000/docs>.

### Cuentas de demostración

| Rol | Email | Contraseña |
|-----|-------|------------|
| Administrador | admin@saborexpress.com | Admin@123 |
| Mesero | mesero@saborexpress.com | Mesero@123 |
| Cajero | cajero@saborexpress.com | Cajero@123 |

## Pruebas

```bash
pip install -r requirements-dev.txt
python smoke_test.py
```

Cubre: autenticación y bloqueo, RBAC, creación de pedido con IGV 18%, pago en
efectivo (con cálculo de vuelto), cierre de pedido y liberación de mesa,
generación de reporte y exportación a Excel.

## Producción (Docker + PostgreSQL)

```bash
cd backend
docker compose up --build
```

Levanta PostgreSQL 16 y la API en el puerto 8000, aplicando el `seed` inicial.
Ajuste `SECRET_KEY` y las credenciales de base de datos antes de desplegar.

## Reglas de negocio implementadas

IGV 18% · cantidad por ítem 1–99 · observaciones ≤ 200 caracteres · precio > 0 ·
pago con un único método por pedido · efectivo entregado ≥ total (con vuelto) ·
tarjeta con últimos 4 dígitos + N° de autorización ≤ 20 · pedido Open/Closed ·
mesa Free/Occupied · sin eliminación de registros (solo edición) · bloqueo tras
5 intentos fallidos (15 min) · sesión inactiva 3 min (aviso a los 2) · "recordar
sesión" 7 días · trazabilidad en `audit_logs`.
