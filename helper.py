from fastapi import FastAPI # type: ignore
from pydantic import BaseModel

# Define the FastAPI app
app = FastAPI()

# In-memory storage for the last posted item
last_item = None

# Define a Pydantic model for the incoming JSON payload
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

# Define a POST endpoint that accepts JSON
@app.post("/items/")
async def create_item(item: Item):
    global last_item
    last_item = item
    return {
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "tax": item.tax
    }

# Define a GET endpoint that returns the last posted item
@app.get("/items/")
async def get_last_item():
    if last_item is None:
        return {"message": "No items have been posted yet."}
    return {
        "name": last_item.name,
        "description": last_item.description,
        "price": last_item.price,
        "tax": last_item.tax
    }

# To run the app, use the following command:
# uvicorn main:app --reload
