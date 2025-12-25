# Inicio Rápido - FastAPI + React Chat

Ejecuta el chat en menos de 5 minutos con Docker.

## Opción 1: Docker Compose (Más Fácil) 🐳

```bash
# 1. Navegar al proyecto
cd examples/fastapi-react-chat

# 2. Iniciar todo
docker-compose up
```

**¡Listo!** 
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Opción 2: Sin Docker 💻

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Probar el Chat

1. Abre http://localhost:3000
2. Ingresa tu nombre y sala
3. Abre otra pestaña con otro nombre
4. ¡Chatea!

## Características

- ✅ Chat en tiempo real
- ✅ Múltiples salas
- ✅ Lista de usuarios
- ✅ Indicador "escribiendo..."
- ✅ Historial de mensajes
- ✅ Reconexión automática

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Reconstruir
docker-compose up --build
```

## Troubleshooting

**¿Backend no conecta?**
```bash
docker-compose logs backend
```

**¿Puerto ocupado?**
Edita `docker-compose.yml` y cambia los puertos.

---

Ver **README.md** para documentación completa.
