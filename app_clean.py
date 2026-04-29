import os
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
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

class Prompt(BaseModel):
    prompt: str
class UserCreate(BaseModel):
    username: str
    password: str
@app.post("/agent")
def agent(data: Prompt):
    db = SessionLocal()

    try:
        import os
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise Exception("Missing API key")

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a startup builder AI. Generate a structured startup plan."},
                {"role": "user", "content": data.prompt}
            ]
        )

        result = response.choices[0].message.content

    except Exception as e:
        result = "AI error: " + str(e)

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
@app.post("/signup")
def signup(user: UserCreate):
    db = SessionLocal()

    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()

    return {"message": "User created"}
@app.post("/login")
def login(user: UserCreate):
    db = SessionLocal()

    existing = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()

    if not existing:
        return {"error": "Invalid credentials"}

    return {"message": "Login success"}
