import json
import os
import threading
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "orders.json")
_lock = threading.Lock()


def _ensure_file():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"orders": []}, f, indent=2)


def _read():
    _ensure_file()
    with open(DATA_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "orders" not in data or not isinstance(data["orders"], list):
        return {"orders": []}
    return data


def _write(data):
    _ensure_file()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_order(order_id):
    with _lock:
        data = _read()
        for order in data["orders"]:
            if order.get("orderId") == order_id:
                return order
    return None


def upsert_order(order):
    with _lock:
        data = _read()
        orders = data["orders"]
        for i, existing in enumerate(orders):
            if existing.get("orderId") == order.get("orderId"):
                orders[i] = order
                break
        else:
            orders.append(order)
        _write(data)


def list_orders():
    with _lock:
        data = _read()
        return list(data["orders"])


def new_order(order_id, product_name, status, price):
    return {
        "orderId": order_id,
        "productName": product_name,
        "status": status,
        "price": price,
        "createdAt": datetime.utcnow().isoformat() + "Z",
    }
