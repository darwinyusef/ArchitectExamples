#!/bin/bash

# Script para inicializar certificados SSL con Let's Encrypt
# Uso: ./init-letsencrypt.sh [dominio] [email]

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
DOMAIN=${1:-transcript.aquicreamos.com}
EMAIL=${2:-admin@aquicreamos.com}
STAGING=${3:-0} # 0 = producción, 1 = staging (para testing)

DATA_PATH="./certbot"
RSA_KEY_SIZE=4096

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Inicializando Let's Encrypt SSL${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Dominio: $DOMAIN"
echo "Email: $EMAIL"
echo "Staging: $STAGING (0=prod, 1=test)"
echo ""

# Verificar que el dominio apunte a este servidor
echo -e "${YELLOW}[1/6]${NC} Verificando DNS..."
CURRENT_IP=$(dig +short $DOMAIN | tail -n1)
if [ -z "$CURRENT_IP" ]; then
    echo -e "${RED}ERROR: El dominio $DOMAIN no resuelve a ninguna IP${NC}"
    echo "Asegúrate de configurar el registro DNS A o CNAME apuntando a este servidor"
    exit 1
fi
echo -e "${GREEN}✓${NC} DNS OK: $DOMAIN → $CURRENT_IP"

# Crear directorios necesarios
echo -e "${YELLOW}[2/6]${NC} Creando directorios..."
mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
mkdir -p "$DATA_PATH/www"
echo -e "${GREEN}✓${NC} Directorios creados"

# Descargar recommended TLS parameters
echo -e "${YELLOW}[3/6]${NC} Descargando parámetros TLS recomendados..."
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
fi
if [ ! -e "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
fi
echo -e "${GREEN}✓${NC} Parámetros TLS descargados"

# Crear certificado dummy para iniciar nginx
echo -e "${YELLOW}[4/6]${NC} Creando certificado dummy temporal..."
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
if [ ! -e "$DATA_PATH/conf/live/$DOMAIN/fullchain.pem" ]; then
    mkdir -p "$DATA_PATH/conf/live/$DOMAIN"
    docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
        openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
        -keyout '$CERT_PATH/privkey.pem' \
        -out '$CERT_PATH/fullchain.pem' \
        -subj '/CN=localhost'" certbot
    echo -e "${GREEN}✓${NC} Certificado dummy creado"
else
    echo -e "${GREEN}✓${NC} Certificado ya existe"
fi

# Iniciar nginx
echo -e "${YELLOW}[5/6]${NC} Iniciando nginx..."
docker-compose -f docker-compose.prod.yml up -d nginx
echo -e "${GREEN}✓${NC} Nginx iniciado"

# Esperar a que nginx esté listo
echo "Esperando a que nginx esté listo..."
sleep 5

# Eliminar certificado dummy
echo -e "${YELLOW}[6/6]${NC} Obteniendo certificado SSL real de Let's Encrypt..."
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
    rm -rf /etc/letsencrypt/live/$DOMAIN && \
    rm -rf /etc/letsencrypt/archive/$DOMAIN && \
    rm -rf /etc/letsencrypt/renewal/$DOMAIN.conf" certbot

# Solicitar certificado real
STAGING_ARG=""
if [ $STAGING != "0" ]; then
    STAGING_ARG="--staging"
    echo -e "${YELLOW}USANDO MODO STAGING (testing)${NC}"
fi

docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    $STAGING_ARG \
    --email $EMAIL \
    -d $DOMAIN \
    --rsa-key-size $RSA_KEY_SIZE \
    --agree-tos \
    --force-renewal \
    --non-interactive" certbot

# Recargar nginx
echo "Recargando nginx con certificado real..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ SSL Configurado Exitosamente!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Tu sitio ahora es accesible en:"
echo -e "${GREEN}https://$DOMAIN${NC}"
echo ""
echo "Los certificados se renovarán automáticamente."
echo ""
echo "Verificar renovación manual:"
echo "docker-compose -f docker-compose.prod.yml run --rm certbot renew"
echo ""
