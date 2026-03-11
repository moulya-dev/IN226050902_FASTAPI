from fastapi import FastAPI, HTTPException, Response, status, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Product Model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# Initial Product Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Helper Function
def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

# GET All Products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

# POST Add Product
@app.post("/products")
def add_product(product: Product, response: Response):

    # check duplicate name
    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED

    return {
        "message": "Product added",
        "product": new_product
    }

# GET Products Audit
@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }

# PUT Category Discount
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    # Validate discount range
    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="discount_percent must be between 1 and 99")

    updated_products = []

    # Apply discount to matching category
    for product in products:
        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated_products.append({
                "name": product["name"],
                "new_price": new_price
            })

    # Handle case where category does not exist
    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }

# PUT Update Product
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    response: Response,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }

# DELETE Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {
        "message": f"Product '{product['name']}' deleted"
    }

# GET Single Product
@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product