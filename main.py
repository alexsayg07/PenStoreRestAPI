from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from odmantic import Field, Model
import uvicorn
import pandas as pd

# Initialize inventory dataframe and import inventory from json
products_data = {"name": [],
                "variant": [],
                "sku": [],
                "price": [],
                "qty": [],
                "description": []}
products_df = pd.DataFrame(products_data)
df = pd.read_json("inventory.json")
products_df = products_df.append(df)

print(products_df)
total_items = products_df["qty"].sum()
print(total_items)

# Initialize shopping cart dataframe
cart_data = {"sku": [],
             "qty": [],
             "price": []}
cart_df = pd.DataFrame(cart_data)


# Initialize application
app = FastAPI()

# Define data model using pydantic library
# Define Product BaseModel
# Serializer
class Product(BaseModel):
    name: str
    variant: str
    sku: str
    price: float
    qty: int
    description: str

# Define Cart BaseModel for future implementation for multiple users
class Cart(BaseModel):
    sku: str
    qty: int
    price: float

@app.get("/")
async def root():
    return {"Hello": "World!!"}

# return all inventory
@app.get("/products")
def get_inventory():
    global products_df
    return products_df

# return all shopping cart
@app.get("/cart")
def get_inventory():
    global cart_df
    return cart_df

# Add a new product
# send product details in request body
@app.post("/products") # POST /products
def add_product(product: Product):
    # save product to database
    global products_df
    new_product = pd.DataFrame({
        "name": [product.name],
        "variant": [product.variant],
        "sku": [product.sku],
        "price": [product.price],
        "qty": [product.qty],
        "description": [product.description]
    })
    products_df = products_df.append(new_product, ignore_index=True)
    # return a response
    return {"message": "Product added."}

# Add/Remove from inventory
# Send quantity to add/remove in request body
# quantity values negative or positive to remove/add
@app.put("/products/{product_id}/inventory") #PUT /products/{product_id}/inventory
def update_qty(product_id: str, quantity: int):
    global products_df

    # Find the product index by sku str in the DataFrame
    product_index = products_df.index[products_df['sku'] == product_id].tolist()
    if not product_index:
        return {"message": "Product not found"}

    # Check if the requested quantity is available in the inventory
    current_inventory = products_df.loc[product_index[0], "qty"]
    if quantity < 0:
        if abs(quantity) > current_inventory:
            return {"message": "Insufficient inventory"}

    # Otherwise, update the inventory value
    products_df.loc[product_index[0], "qty"] += quantity

# Update Product
# Send updated product details in request body
@app.put("/products/{product_id}") # PUT /products/{product_id}
def update_details(product_id: str, description: str):
    global products_df
    # Find the product index by sku str in the DataFrame
    product_index = products_df.index[products_df['sku'] == product_id].tolist()
    if not product_index:
        return {"message": "Product not found"}

    # Update description
    products_df.loc[product_index[0], "description"] = description

    return {"message": "Updated product description"}

# Remove Product
@app.delete("/products/{product_id}") # DELETE
def delete_product(product_id: str):
    global products_df
    # Find the product index by sku str in the DataFrame
    product_index = products_df.index[products_df['sku'] == product_id].tolist()
    if not product_index:
        return {"message": "Product not found"}
    products_df = products_df.drop(product_index)
    return {"message": str(product_id, "has been deleted")}

# Buy Product (Shopping Cart)
# Send product IDs and quantities in the request body
# return cart summary and total cost
# TODO: Update input to only be product_id (sku) and quantity
@app.post("/cart/buy")
def add_to_cart(product: Product):
    global cart_df
    # check if sku already in cart and add to quantity
    # if not create new cart_product
    cart_index = cart_df.index[cart_df['sku'] == product.sku].tolist()
    if not cart_index:
        cart_product = {"sku": product.sku,
                        "qty": product.qty,
                        "price": product.price}
        cart_df = cart_df.append(cart_product, ignore_index=True)
    else:
        cart_df.loc[cart_index[0], "qty"] += product.qty

    # summarize cart total and number of items
    num_items = cart_df["qty"].sum()
    total = (cart_df["qty"] * cart_df["price"]).sum()
    msg = "Cart total: $" + str(total) + " for " + str(num_items) + " items."
    return{"message": msg}


# Global Search
#@app.get('/products?q={searchQuery}')