from openai import OpenAI
client = OpenAI()
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def home():
    return {"message": "API is running"}
# 🔥 ADD THIS (CORS FIX)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

class Item(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str
    password: str
class Prompt(BaseModel):
    prompt: str
security = HTTPBearer()

def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/signup")
def signup(user: User):
    db = SessionLocal()
    db_user = UserDB(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"message": "User created"}

@app.post("/login")
def login(user: User):
    db = SessionLocal()
    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    
    if not db_user or db_user.password != user.password:
        db.close()
        return {"error": "Invalid credentials"}
    
    token = create_token(user.username)
    db.close()
    return {"access_token": token}

@app.post("/items")
def create_item(item: Item, user: str = Depends(verify_token)):
    db = SessionLocal()
    db_item = ItemDB(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.get("/items")
def get_items(user: str = Depends(verify_token)):
    db = SessionLocal()
    items = db.query(ItemDB).all()
    db.close()
    return items
from openai import OpenAI
client = OpenAI()
@app.post("/agent")
def agent(data: Prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a startup expert."},
                {"role": "user", "content": data.prompt}
            ]
        )

        return {
            "result": response.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)}
