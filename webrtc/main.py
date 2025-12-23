from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.models.database import init_db
from app.routers import items, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación
    Inicializa la base de datos al inicio
    """
    print("Inicializando base de datos...")
    await init_db()
    print("Base de datos inicializada correctamente")
    yield
    print("Cerrando aplicación...")


# Crear instancia de FastAPI
app = FastAPI(
    title="WebRTC + WebSocket CRUD API",
    description="API REST con WebRTC y WebSockets usando concurrencia y paralelismo",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(items.router)
app.include_router(websocket.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Página principal con interfaz de cliente
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Endpoint de health check
    """
    return {
        "status": "healthy",
        "service": "WebRTC CRUD API"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
