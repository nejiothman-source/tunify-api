from openai import OpenAI
client = OpenAI()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

class Prompt(BaseModel):
    prompt: str
@app.post("/agent")
def agent(data: Prompt):
    db = SessionLocal()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a startup idea generator."},
            {"role": "user", "content": data.prompt}
        ]
    )

    result = response.choices[0].message.content

    new_item = Item(name=data.prompt, price=0)
    db.add(new_item)
    db.commit()

    return {"result": result}
@app.get("/ideas")
def get_ideas():
    db = SessionLocal()
    items = db.query(Item).all()

    return {
        "ideas": [{"id": item.id, "idea": item.name} for item in items]
    }
