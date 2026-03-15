from flask import Flask, send_from_directory
from datetime import datetime
import os
import html
from store import get_order


def create_app():
    app = Flask(__name__, static_folder=None)

    public_dir = os.path.join(os.path.dirname(__file__), "public")

    @app.get("/")
    def index():
        return "<html><head><title>Order Tracking</title></head><body><h1>Order Tracking</h1><p>Use /track/&lt;orderId&gt;</p></body></html>"

    @app.get("/public/<path:filename>")
    def public_files(filename):
        return send_from_directory(public_dir, filename)

    @app.get("/track/<order_id>")
    def track(order_id):
        order = get_order(order_id)
        if not order:
            return (
                "<!doctype html><html><head><title>Not Found</title>"
                "<link rel=\"stylesheet\" href=\"/public/styles.css\" /></head>"
                "<body><main class=\"page\"><section class=\"card\">"
                f"<h1>Order Not Found</h1><p>No order with ID <strong>{html.escape(order_id)}</strong>.</p>"
                "</section></main></body></html>",
                404,
            )

        created_at = order.get("createdAt", "")
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            created_text = created_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            created_text = created_at

        return (
            "<!doctype html><html><head>"
            f"<title>Order {html.escape(order.get('orderId', ''))}</title>"
            "<link rel=\"stylesheet\" href=\"/public/styles.css\" /></head>"
            "<body><main class=\"page\"><section class=\"card\">"
            "<div class=\"badge\">Order Tracking</div>"
            f"<h1>Order #{html.escape(order.get('orderId', ''))}</h1>"
            "<div class=\"grid\">"
            f"<div class=\"label\">Product</div><div class=\"value\">{html.escape(order.get('productName', ''))}</div>"
            f"<div class=\"label\">Status</div><div class=\"value status\">{html.escape(order.get('status', ''))}</div>"
            f"<div class=\"label\">Price</div><div class=\"value\">৳ {html.escape(str(order.get('price', '')))}</div>"
            f"<div class=\"label\">Created</div><div class=\"value\">{html.escape(created_text)}</div>"
            "</div><div class=\"footer\">Thank you for your purchase.</div>"
            "</section></main></body></html>"
        )

    return app
