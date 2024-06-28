# Dockerfile para React
FROM node:21 AS build

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
COPY .env ./
RUN npm install

COPY . ./
RUN npm run build

# Exportar los archivos de build a un volumen compartido
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
