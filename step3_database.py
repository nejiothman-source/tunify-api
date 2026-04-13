from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    db = SessionLocal()
    db_item = ItemDB(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.get("/items")
def get_items():
    db = SessionLocal()
    items = db.query(ItemDB).all()
    db.close()
    return items
