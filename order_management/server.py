from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastmcp import FastMCP

# print("Yes")

mcp = FastMCP(
    name="Order management MCP",
    instructions=(
        "Use these tools to search for products, create orders,"
        "check order status, and cancel the orders"
    ),
    
)




PRODUCTS = {
    "P100": {
        "product_id": "P100",
        "name": "Laptop",
        "price": 75000,
        "stock": 10,
    },

    "P101": {
        "product_id": "P101",
        "name": "Wireless Mouse",
        "price": 1200,
        "stock": 25,
    },

    "P102": {
        "product_id": "P102",
        "name": "keyboard",
        "price": 4500,
        "stock": 15,
    },


}


ORDERS: dict[str, dict[str, Any]] = {}

@mcp.tool
def search_products(query: str) -> list[dict[str, Any]]:
    """Search for the available products by product id or name"""
    normalized_query = query.strip().lower()

    return [
        product
        for product in PRODUCTS.values()
        if normalized_query in product["product_id"].lower() 
        or normalized_query in product["name"].lower()
    ]



@mcp.tool
def create_order(product_id: str, quantity: int, customer_name: str) -> dict[str, Any]:
    """Create an order for a product"""
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    product = PRODUCTS.get(product_id.upper())

    if not product:
        raise ValueError(f"Product '{product_id}' is not found")

    if quantity > product["stock"]:
        raise ValueError(f"Only {product['stock']} units are available")

    order_id = f"ORD-{uuid4().hex[:8].upper()}"
    total_amount = round(product["price"] * quantity, 2)

    order = {
        "order_id": order_id,
        "customer_name": customer_name.strip(),
        "product_id": product["product_id"],
        "product_name": product["name"],
        "quantity": quantity,
        "total_amount": total_amount,
        "status": "CONFIRMED",
        "created_at": datetime.now(timezone.utc).isoformat(),

    }
    ORDERS[order_id] = order
    product["stock"] -= quantity
    return order



@mcp.tool
def get_order(order_id: str) -> dict[str, Any]:
    """Return details and current status of the order"""
    order = ORDERS.get(order_id.upper())

    if not order:
        raise ValueError(f"Order '{order_id}' was not found")
    return order



@mcp.tool
def cancel_order(order_id: str) -> dict[str, Any]:
    """Cancel a confirmed order and restore product stock"""
    normalized_order_id = order_id.upper()
    order = ORDERS.get(normalized_order_id)

    if not order:
        raise ValueError(f"Order '{order_id}' was not found")

    if order["status"] == "CANCELLED":
        return order

    order["status"] = "CANCELLED"
    order["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    PRODUCTS[order["product_id"]]["stock"] += order["quantity"]

    return order


if __name__ == "__main__":
    mcp.run()