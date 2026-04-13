from fastapi import FastAPI

app = FastAPI()

items = []

@app.post("/items")
def create_item(item: dict):
    items.append(item)
    return item

@app.get("/items")
def get_items():
    return items
