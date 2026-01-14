# Dockerfile para grpc-basico
FROM node:18-alpine

# Instalar dependencias del sistema
RUN apk add --no-cache bash

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY tsconfig.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY proto/ ./proto/
COPY server/ ./server/
COPY client/ ./client/

# Compilar TypeScript
RUN npm run build

# Exponer puerto gRPC
EXPOSE 50051

# Comando por defecto (servidor)
CMD ["npm", "run", "server"]
