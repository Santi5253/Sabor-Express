"""Algoritmos implementados en SaborExpress (adaptados del curso).

1. Hash (bcrypt)            -> app/utils/security.py (hash_password / verify_password)
2. Búsqueda binaria         -> binary_search
3. Ordenamiento (Merge Sort)-> merge_sort
4. Voraz (Greedy)           -> greedy_change (vuelto óptimo)
5. Backtracking             -> backtrack_assign (asignación de mesas a meseros)
"""
from decimal import Decimal


DENOMINATIONS = [200, 100, 50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.01]


def binary_search(items, key, target):
    """Búsqueda binaria sobre una lista ordenada por `key`. O(log n)."""
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = key(items[mid])
        if val == target:
            return items[mid]
        if val < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def _merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr, key):
    """Merge Sort estable. O(n log n) tiempo, O(n) espacio."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return _merge(left, right, key)


def greedy_change(amount):
    """Devuelve el vuelto con el mínimo número de billetes/monedas (voraz).

    Retorna un dict {denominacion: cantidad} o None si no es exacto.
    """
    result = {}
    restante = round(float(amount), 2)
    for d in sorted(DENOMINATIONS, reverse=True):
        if restante >= d - 1e-9:
            q = int(round(restante / d))
            if q > 0:
                result[d] = q
                restante = round(restante - q * d, 2)
    if abs(restante) < 1e-6:
        return result
    return None


def is_safe_table(mesa, mesero, asignaciones):
    """Mesa libre y mesero sin otra mesa en el mismo turno."""
    status = getattr(mesa, "status", None)
    try:
        from app.models.table import TableStatus

        if status != TableStatus.FREE:
            return False
    except Exception:
        if str(status) != "Free":
            return False
    for m, ms in asignaciones:
        if getattr(ms, "id", None) == getattr(mesero, "id", None):
            return False
    return True


def backtrack_assign(mesas, meseros):
    """Asigna mesas a meseros sin conflictos usando backtracking.

    Retorna lista de tuplas (mesa, mesero) o None si no hay solución.
    """
    asignaciones = []

    def rec(idx):
        if idx == len(mesas):
            return [a for a in asignaciones]
        for ms in meseros:
            if is_safe_table(mesas[idx], ms, asignaciones):
                asignaciones.append((mesas[idx], ms))
                res = rec(idx + 1)
                if res is not None:
                    return res
                asignaciones.pop()
        return None

    return rec(0)
