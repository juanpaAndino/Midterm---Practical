import os
import bcrypt
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv

load_dotenv()
PEPPER = os.getenv("APP_PEPPER")

if not PEPPER:
    raise RuntimeError("Error: No se encontró la variable APP_PEPPER en el entorno.")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

class UserCreate(SQLModel):
    username: str
    password: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

def get_password_hash(password: str) -> str:
    peppered_password = password + PEPPER
    password_bytes = peppered_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    peppered_password = plain_password + PEPPER
    return bcrypt.checkpw(
        peppered_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

@app.post("/register")
def register_user(user: UserCreate):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == user.username)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")

        hashed_pwd = get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_pwd)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return {"message": "Usuario registrado exitosamente", "user_id": db_user.id}

@app.post("/login")
def login_user(user: UserCreate):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user.username)).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos.")

        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos.")

        return {"message": "Autenticación exitosa. ¡Bienvenido!"}