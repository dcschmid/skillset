"""legacy_app — AUDIT fixture (synthetic). Flask-style orders API with
real, findable defects for skill evaluation scenarios B/C/H:
  * GET /orders/{id}  : no ownership check (IDOR)
  * list_orders       : no tenant/owner filter
  * create_order      : mass assignment (**body)
  * errors            : stack traces returned to client
Do not 'fix' the fixture; it is input, not output."""
from flask import Flask, jsonify, request

app = Flask(__name__)
ORDERS = {}  # id -> dict(owner_id=..., total=..., ref=...)


@app.get("/orders")
def list_orders():
    return jsonify(list(ORDERS.values()))          # defect: unscoped


@app.get("/orders/<int:oid>")
def get_order(oid):
    order = ORDERS.get(oid)
    if not order:
        return jsonify(error="not found"), 404
    return jsonify(order)                           # defect: no owner check


@app.post("/orders")
def create_order():
    body = request.get_json(force=True)
    oid = len(ORDERS) + 1
    ORDERS[oid] = {"id": oid, **body}               # defect: mass assignment
    return jsonify(ORDERS[oid]), 201


@app.errorhandler(Exception)
def on_error(e):
    return jsonify(traceback=str(e.__class__.__mro__)), 500  # defect: leak


if __name__ == "__main__":
    app.run(port=5051)
