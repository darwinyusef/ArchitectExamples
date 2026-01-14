# 🚀 Guía de Deploy a Producción

Guía paso a paso para desplegar el microservicio de transcripción de voz en `transcript.aquicreamos.com`.

---

## 📋 Pre-requisitos

### Servidor
- ✅ Ubuntu 20.04+ / Debian 11+
- ✅ Docker 20.10+
- ✅ Docker Compose 2.0+
- ✅ Mínimo 2 GB RAM
- ✅ Mínimo 20 GB disco
- ✅ Puerto 80 y 443 abiertos

### DNS
- ✅ Registro A: `transcript.aquicreamos.com` → IP del servidor
- ✅ Propagación DNS completada (verificar con `dig transcript.aquicreamos.com`)

### Acceso
- ✅ SSH al servidor
- ✅ Usuario con permisos sudo

---

## 🔧 Instalación en Servidor

### 1. Conectar al Servidor

```bash
ssh user@your-server-ip
```

### 2. Instalar Docker (si no está instalado)

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version

# Re-login para aplicar cambios de grupo
exit
# Volver a conectar
ssh user@your-server-ip
```

### 3. Clonar/Subir Proyecto

**Opción A: Git**
```bash
cd /opt
sudo git clone https://github.com/tu-usuario/grpc-voice.git
cd grpc-voice
```

**Opción B: SCP desde local**
```bash
# Desde tu máquina local
scp -r /path/to/grpc-voice user@your-server-ip:/opt/
```

**Opción C: Crear directorio y subir archivos**
```bash
sudo mkdir -p /opt/grpc-voice
cd /opt/grpc-voice
# Subir archivos vía SFTP o rsync
```

---

## ⚙️ Configuración

### 1. Variables de Entorno

```bash
cd /opt/grpc-voice

# Copiar ejemplo de producción
cp .env.prod.example .env.prod

# Editar con valores reales
nano .env.prod
```

**Configurar:**
```env
DOMAIN=transcript.aquicreamos.com
EMAIL=admin@aquicreamos.com

# Generar password seguro
RABBITMQ_USER=admin
RABBITMQ_PASS=$(openssl rand -base64 32)

# Si conectas a RabbitMQ externo
RABBITMQ_EXTERNAL_HOST=rabbitmq.aquicreamos.com
RABBITMQ_EXTERNAL_USER=transcript_service
RABBITMQ_EXTERNAL_PASS=tu_password_seguro
```

### 2. Configurar Conexión a RabbitMQ Externo (Opcional)

Si tu backend principal ya tiene RabbitMQ, modifica `docker-compose.prod.yml`:

```yaml
# Comentar el servicio rabbitmq local:
# rabbitmq:
#   ...

# Actualizar URL en backend:
backend:
  environment:
    - RABBITMQ_URL=amqp://${RABBITMQ_EXTERNAL_USER}:${RABBITMQ_EXTERNAL_PASS}@${RABBITMQ_EXTERNAL_HOST}:5672/
```

---

## 🔐 Configurar SSL (Let's Encrypt)

### 1. Verificar DNS

```bash
# Verificar que el dominio apunte a este servidor
dig +short transcript.aquicreamos.com

# Debe retornar la IP de tu servidor
# Si no, esperar a que DNS propague (puede tardar hasta 48h)
```

### 2. Ejecutar Script de Inicialización SSL

```bash
cd /opt/grpc-voice

# Hacer ejecutable
chmod +x init-letsencrypt.sh

# Ejecutar (modo staging para testing)
./init-letsencrypt.sh transcript.aquicreamos.com admin@aquicreamos.com 1

# Si funciona, ejecutar en producción
./init-letsencrypt.sh transcript.aquicreamos.com admin@aquicreamos.com 0
```

**El script hará:**
1. ✅ Verificar DNS
2. ✅ Crear directorios necesarios
3. ✅ Descargar parámetros TLS
4. ✅ Crear certificado temporal
5. ✅ Iniciar Nginx
6. ✅ Obtener certificado real de Let's Encrypt

---

## 🚀 Deploy

### 1. Build e Iniciar Servicios

```bash
cd /opt/grpc-voice

# Build de imágenes
docker-compose -f docker-compose.prod.yml --env-file .env.prod build

# Iniciar servicios
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Con consumer de RabbitMQ (opcional)
docker-compose -f docker-compose.prod.yml --env-file .env.prod --profile with-consumer up -d
```

### 2. Verificar Estado

```bash
# Ver contenedores
docker-compose -f docker-compose.prod.yml ps

# Deben estar todos en estado "healthy" o "running"
```

### 3. Ver Logs

```bash
# Todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Solo backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Solo whisper
docker-compose -f docker-compose.prod.yml logs -f whisper
```

---

## ✅ Verificación

### 1. Health Checks

```bash
# Backend API
curl https://transcript.aquicreamos.com/api/health

# Frontend
curl https://transcript.aquicreamos.com/

# Nginx
curl https://transcript.aquicreamos.com/health
```

**Respuesta esperada del backend:**
```json
{
  "status": "healthy",
  "services": {
    "whisper": "ok",
    "rabbitmq": "ok",
    "grpc": "running"
  }
}
```

### 2. Probar Transcripción

```bash
# Subir archivo de audio
curl -X POST https://transcript.aquicreamos.com/api/transcribe \
  -F "file=@test.mp3" \
  -F "language=es"
```

### 3. Abrir en Navegador

```
https://transcript.aquicreamos.com
```

- ✅ Debe cargar el frontend
- ✅ Certificado SSL válido
- ✅ Poder grabar o subir audio
- ✅ Ver transcripciones

---

## 📊 Monitoreo

### Ver Recursos

```bash
# Uso de CPU/RAM en tiempo real
docker stats

# Logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

### Ver RabbitMQ (si está local)

```bash
# Acceder temporalmente al management UI
# Crear túnel SSH
ssh -L 15672:localhost:15672 user@your-server-ip

# Luego en navegador local:
# http://localhost:15672
# Usuario: el de .env.prod
```

### Ver Métricas de Envoy

```bash
curl http://localhost:9901/stats
```

---

## 🔄 Actualizaciones

### Actualizar Código

```bash
cd /opt/grpc-voice

# Pull cambios (si usas git)
git pull

# O subir archivos nuevos vía SCP

# Rebuild y reiniciar
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### Actualizar Solo Backend

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build backend
```

### Actualizar Solo Frontend

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build frontend
```

---

## 🛡️ Seguridad

### 1. Firewall

```bash
# Instalar UFW
sudo apt install ufw

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Ver reglas
sudo ufw status
```

### 2. Fail2ban (Opcional)

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Iniciar
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Actualizar Regularmente

```bash
# Sistema
sudo apt update && sudo apt upgrade -y

# Docker
sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart
```

---

## 🔧 Troubleshooting

### Certificado SSL no se crea

```bash
# Verificar DNS
dig +short transcript.aquicreamos.com

# Ver logs de certbot
docker-compose -f docker-compose.prod.yml logs certbot

# Intentar manual
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --dry-run -d transcript.aquicreamos.com
```

### Servicios no inician

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs

# Verificar puertos
sudo netstat -tulpn | grep -E '80|443|8001|50051'

# Reiniciar todo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Whisper muy lento

```bash
# Verificar recursos
docker stats

# Aumentar workers en .env.prod
WHISPER_WORKERS=4

# Usar modelo más pequeño si es necesario
WHISPER_MODEL=tiny

# Reiniciar whisper
docker-compose -f docker-compose.prod.yml restart whisper
```

### No conecta a RabbitMQ externo

```bash
# Verificar conectividad
docker-compose -f docker-compose.prod.yml exec backend ping rabbitmq.aquicreamos.com

# Verificar credenciales
docker-compose -f docker-compose.prod.yml exec backend env | grep RABBIT

# Ver logs
docker-compose -f docker-compose.prod.yml logs backend | grep -i rabbit
```

---

## 📁 Backup

### Backup de Certificados SSL

```bash
# Crear backup
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz certbot/conf/live certbot/conf/archive

# Restaurar
tar -xzf ssl-backup-YYYYMMDD.tar.gz
```

### Backup de Logs

```bash
docker-compose -f docker-compose.prod.yml exec backend tar -czf - /app/logs > logs-backup-$(date +%Y%m%d).tar.gz
```

---

## 🔄 Rollback

Si algo sale mal:

```bash
# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Restaurar versión anterior
git checkout previous-version
# O restaurar archivos

# Reiniciar
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

---

## 📝 Checklist de Deploy

- [ ] Servidor preparado con Docker
- [ ] DNS configurado y propagado
- [ ] Proyecto subido al servidor
- [ ] `.env.prod` configurado
- [ ] Firewall configurado
- [ ] SSL certificados obtenidos
- [ ] Servicios iniciados
- [ ] Health checks OK
- [ ] Prueba de transcripción exitosa
- [ ] Frontend accesible en HTTPS
- [ ] Logs sin errores
- [ ] RabbitMQ conectado (local o externo)
- [ ] Monitoreo configurado

---

## 🆘 Soporte

Si encuentras problemas:

1. Ver logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verificar configuración: `cat .env.prod`
3. Revisar estado: `docker-compose -f docker-compose.prod.yml ps`
4. Contactar al equipo de DevOps

---

**¡Tu microservicio de transcripción está listo para producción!** 🎉
