# Guion de Algoritmos Implementados — SaborExpress

**Proyecto:** Sistema de Gestión de Pedidos — Restaurante "SaborExpress"
**Desarrollado por:** NovaTech Soluciones IT S.A.S
**Repositorio:** https://github.com/Santi5253/Sabor-Express.git

Este documento describe los **5 algoritmos** implementados en el producto SaborExpress, indicando
dónde están implementados, para qué se usan y cómo funcionan.

---

## 1. Hash (bcrypt) — Encriptación de contraseñas

- **Dónde está implementado:** `Producto/backend/app/utils/security.py` — funciones `hash_password()` y `verify_password()`. Usado por `auth_service.py` en el login y por `users.py` al crear/editar usuarios.
- **Para qué:** proteger las credenciales de los usuarios (Mesero, Cajero, Administrador) frente a filtraciones. Cumple OWASP (autenticación rota, datos sensibles). El login valida el hash sin exponer la contraseña.
- **Cómo funciona:**
  1. Al crear un usuario, `hash_password(plain)` genera un hash bcrypt con salt aleatorio y factor de costo (2^12), almacenado en `password_hash` (VARCHAR(255)).
  2. Al iniciar sesión, `verify_password(plain, hashed)` usa `bcrypt.checkpw`, que compara en tiempo constante (resistente a timing attacks).
  3. Nunca se almacena ni se transmite la contraseña en texto plano.

---

## 2. Búsqueda binaria (Binary Search)

- **Dónde está implementado:** `Producto/backend/app/utils/algorithms.py` — función `binary_search()`. Usado en `Producto/backend/app/routers/products.py` — endpoint `GET /api/v1/admin/products/search?code=...`.
- **Para qué:** localizar un producto por código exacto en el catálogo en tiempo O(log n), acelerando la toma de pedidos y la parametrización, incluso con catálogos grandes (respuesta <= 2 s).
- **Cómo funciona:**
  1. Se obtiene la lista de productos y se ordena por `code`.
  2. Se define un rango `[lo, hi]`. En cada iteración se calcula `mid = (lo + hi) // 2`.
  3. Si `products[mid].code == target`, se retorna el producto.
  4. Si `products[mid].code < target`, se busca en la mitad derecha (`lo = mid + 1`).
  5. Si `products[mid].code > target`, se busca en la mitad izquierda (`hi = mid - 1`).
  6. Si el rango se vacía, retorna `None` (no encontrado).

---

## 3. Ordenamiento (Merge Sort)

- **Dónde está implementado:** `Producto/backend/app/utils/algorithms.py` — funciones `merge_sort()` y `_merge()`. Usado en `Producto/backend/app/routers/products.py` — parámetro `sort` (name, price, code) en `GET /api/v1/admin/products`.
- **Para qué:** ordenar listados de productos (por nombre, precio o código) de forma estable y predecible (O(n log n) en el peor caso), mejorando la presentación en la UI y los reportes.
- **Cómo funciona:**
  1. Si la lista tiene 0 o 1 elemento, ya está ordenada.
  2. Se divide la lista en dos mitades.
  3. Se ordena cada mitad recursivamente (merge_sort).
  4. Se fusionan (merge) las dos mitades ordenadas, comparando por la clave indicada y conservando el orden relativo de elementos iguales (estabilidad).
  5. Complejidad: O(n log n) tiempo, O(n) espacio (arreglos auxiliares).

---

## 4. Algoritmo voraz (Greedy) — Cálculo óptimo del vuelto

- **Dónde está implementado:** `Producto/backend/app/utils/algorithms.py` — función `greedy_change()`. Usado en `Producto/backend/app/services/payment_service.py` — `create_payment()`, campo `change_breakdown` de la respuesta de pago.
- **Para qué:** en el pago en efectivo, el cajero debe devolver el cambio con el mínimo número de billetes/monedas, acelerando la caja y reduciendo errores. Mejora la UX del cajero (cálculo instantáneo del vuelto).
- **Cómo funciona:**
  1. Denominaciones ordenadas de mayor a menor: [200, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.01].
  2. Para cada denominación, se calcula cuántas caben en el monto restante (`q = restante // d`).
  3. Se registra `result[d] = q` y se resta `q * d` del restante.
  4. Si el restante llega a 0, se retorna el diccionario {denominación: cantidad}; si no, retorna `None` (no exacto).
  5. Funciona de forma óptima con sistemas monetarios canónicos (cada denominación divide a la mayor).

---

## 5. Backtracking — Asignación válida de mesas a meseros

- **Dónde está implementado:** `Producto/backend/app/utils/algorithms.py` — funciones `is_safe_table()` y `backtrack_assign()`. Usado en `Producto/backend/app/routers/tables.py` — endpoint `POST /api/v1/tables/assign`.
- **Para qué:** asignar mesas a meseros/turnos sin conflictos (mesa ocupada, mesero ya asignado a otra mesa en el mismo turno). Análogo a colocar reinas sin que se amenacen. Mejora la operación del salón y evita asignaciones inválidas.
- **Cómo funciona:**
  1. `is_safe(mesa, mesero, asignaciones)` verifica que la mesa esté Libre y que el mesero no tenga ya otra mesa asignada en el mismo turno.
  2. `backtrack(mesas, meseros, idx, asignaciones)` recorre las mesas una a una (índice `idx`).
  3. Para cada mesa, prueba cada mesero; si es seguro, lo asigna y avanza al siguiente índice (recursión).
  4. Si se llega al final (`idx == len(mesas)`), se retorna la asignación válida.
  5. Si una rama no lleva a solución, se deshace la última asignación (`pop`) y se prueba la siguiente opción (retroceso).
  6. Complejidad: en el peor caso exponencial O(k^n), pero la poda (`is_safe`) reduce drásticamente el espacio de búsqueda.

---

## Resumen de endpoints nuevos

| Algoritmo | Endpoint | Método |
|---|---|---|
| Búsqueda binaria | `/api/v1/admin/products/search?code=...` | GET |
| Merge Sort | `/api/v1/admin/products?sort=name\|price\|code` | GET |
| Greedy (vuelto) | `/api/v1/payments` (campo `change_breakdown` en la respuesta) | POST |
| Backtracking | `/api/v1/tables/assign` | POST |

## Preguntas de sustentación (referencia)

- **Hash:** ¿Por qué bcrypt y no MD5/SHA-1? → bcrypt incorpora salt y factor de costo, resistiendo fuerza bruta; MD5/SHA-1 son rápidos y vulnerables.
- **Búsqueda binaria:** ¿Precondición? → La lista debe estar ordenada por la clave de búsqueda. Complejidad O(log n).
- **Merge Sort:** ¿Por qué sobre Quick Sort? → Estable y garantiza O(n log n) en el peor caso.
- **Greedy:** ¿Cuándo falla? → Con denominaciones no canónicas; haría falta programación dinámica.
- **Backtracking:** ¿Qué es la poda? → Descartar ramas que no pueden llevar a una solución válida.
path: C:/Users/sf467/Documents/Sabor Express/5. Cierre/Guion_Algoritmos_SaborExpress.md