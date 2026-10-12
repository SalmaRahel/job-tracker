FROM node:22-alpine AS build
WORKDIR /app
ARG VITE_API_URL
RUN case "$VITE_API_URL" in http*) ;; *) echo "VITE_API_URL must be set and start with http" >&2; exit 1 ;; esac
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=nginxconf default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
