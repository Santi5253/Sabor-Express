"""Datos de prueba (seed) para SaborExpress.

Crea: 1 sede, mesas, 2 proveedores, productos y 3 usuarios (admin/mesero/cajero).
Uso:  python seed.py
"""
from decimal import Decimal

from app.database import Base, SessionLocal, engine
from app.models import (
    Branch,
    Product,
    Provider,
    RestaurantTable,
    TableStatus,
    User,
    UserRole,
)
from app.utils.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(User).count() > 0:
    print("La base de datos ya tiene datos. Omitiendo seed.")
    db.close()
    raise SystemExit(0)

branch = Branch(name="Sede Principal", address="Cra 45 # 12-30, Bogotá", phone="+57 601 123 4567")
db.add(branch)
db.flush()

tables = [RestaurantTable(number=n, capacity=c, status=TableStatus.FREE, branch_id=branch.id)
          for n, c in [(1, 4), (2, 4), (3, 2), (4, 6), (5, 2), (6, 4), (7, 8), (8, 4)]]
db.add_all(tables)

p1 = Provider(name="Distribuidora Andina", nit="900.123.456-7", phone="+57 601 555 0001",
              email="ventas@andina.com", address="Zona Industrial Bogotá")
p2 = Provider(name="Lácteos del Valle", nit="901.987.654-3", phone="+57 602 555 0002",
              email="contacto@lacteosvalle.com", address="Cali")
db.add_all([p1, p2])
db.flush()

products = [
    Product(code="ENT-001", name="Ceviche de camarón", product_type="Entradas", provider_id=p1.id, price=Decimal("32.00"), branch_id=branch.id),
    Product(code="ENT-002", name="Causa limeña", product_type="Entradas", provider_id=p1.id, price=Decimal("24.00"), branch_id=branch.id),
    Product(code="PLT-001", name="Lomo saltado", product_type="Platos Fuertes", provider_id=p1.id, price=Decimal("35.00"), branch_id=branch.id),
    Product(code="PLT-002", name="Ají de gallina", product_type="Platos Fuertes", provider_id=p1.id, price=Decimal("28.00"), branch_id=branch.id),
    Product(code="PLT-003", name="Trucha a la plancha", product_type="Platos Fuertes", provider_id=p1.id, price=Decimal("38.00"), branch_id=branch.id),
    Product(code="BEB-001", name="Chicha morada", product_type="Bebidas", provider_id=p2.id, price=Decimal("10.00"), branch_id=branch.id),
    Product(code="BEB-002", name="Limonada frozen", product_type="Bebidas", provider_id=p2.id, price=Decimal("12.00"), branch_id=branch.id),
    Product(code="POS-001", name="Torta de chocolate", product_type="Postres", provider_id=p2.id, price=Decimal("15.00"), branch_id=branch.id),
    Product(code="POS-002", name="Helado artesanal", product_type="Postres", provider_id=p2.id, price=Decimal("14.00"), branch_id=branch.id),
]
db.add_all(products)

users = [
    User(full_name="Administrador General", email="admin@saborexpress.com",
         password_hash=hash_password("Admin@123"), role=UserRole.ADMINISTRADOR, branch_id=branch.id),
    User(full_name="Carlos Pérez", email="mesero@saborexpress.com",
         password_hash=hash_password("Mesero@123"), role=UserRole.MESERO, branch_id=branch.id),
    User(full_name="Ana Gómez", email="cajero@saborexpress.com",
         password_hash=hash_password("Cajero@123"), role=UserRole.CAJERO, branch_id=branch.id),
]
db.add_all(users)

db.commit()
db.close()

print("Seed completado.")
print("Usuarios de prueba:")
print("  admin@saborexpress.com  / Admin@123    (Administrador)")
print("  mesero@saborexpress.com / Mesero@123   (Mesero)")
print("  cajero@saborexpress.com / Cajero@123   (Cajero)")
