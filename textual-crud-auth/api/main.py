from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import uvicorn
import os

# Configuración
SECRET_KEY = "tu-clave-secreta-super-segura-cambiala"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="CRUD API con Auth")

# CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Modelos
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Base de datos en memoria
items_db: List[Item] = [
    Item(id=1, name="Laptop", description="Laptop de alto rendimiento", price=1200.0),
    Item(id=2, name="Mouse", description="Mouse inalámbrico", price=25.0),
    Item(id=3, name="Teclado", description="Teclado mecánico", price=80.0),
]
next_id = 4

# Usuario de prueba (en producción usarías una base de datos real)
users_db = {
    "admin": "admin123",
    "user": "user123"
}

# Funciones de autenticación
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

# Endpoints de autenticación
@app.post("/auth/login", response_model=Token)
async def login(user: User):
    if user.username not in users_db or users_db[user.username] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/verify")
async def verify(username: str = Depends(verify_token)):
    return {"username": username, "status": "authenticated"}

@app.get("/auth_page.html")
async def get_auth_page():
    file_path = os.path.join(os.path.dirname(__file__), "auth_page.html")
    return FileResponse(file_path)

# Endpoints CRUD
@app.get("/")
async def root():
    return {"message": "API CRUD con autenticación - Usa /docs para ver la documentación"}

@app.get("/items", response_model=List[Item])
async def get_items(username: str = Depends(verify_token)):
    return items_db

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, username: str = Depends(verify_token)):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, username: str = Depends(verify_token)):
    global next_id
    item.id = next_id
    next_id += 1
    items_db.append(item)
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item, username: str = Depends(verify_token)):
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            item.id = item_id
            items_db[i] = item
            return item
    raise HTTPException(status_code=404, detail="Item no encontrado")

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, username: str = Depends(verify_token)):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return {"message": "Item eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Item no encontrado")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
