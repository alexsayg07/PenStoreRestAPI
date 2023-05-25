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
# import inventory information from json file
df = pd.read_json("inventory.json")
products_df = products_df.append(df)

# Initialize shopping cart dataframe
shopping_cart_data = {"name": [],
                "sku": [],
                "price": [],
                "qty": []}
shopping_cart_df = pd.DataFrame(shopping_cart_data)


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

# Define ShoppingCart BaseModel
class ShoppingCart(BaseModel):
    name: str
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
#@app.post("/cart/buy") # POST /cart/buy

# Global Search
#@app.get('/products?q={searchQuery}')