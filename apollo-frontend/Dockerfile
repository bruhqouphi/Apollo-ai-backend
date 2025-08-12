# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Write nginx configuration
RUN printf 'user  nginx;\nworker_processes  auto;\nerror_log  /var/log/nginx/error.log warn;\npid        /var/run/nginx.pid;\n\nEvents { worker_connections 1024; }\n\nhttp {\n  include       /etc/nginx/mime.types;\n  default_type  application/octet-stream;\n  sendfile        on;\n  keepalive_timeout  65;\n  server {\n    listen 80;\n    server_name _;\n    root   /usr/share/nginx/html;\n    index  index.html;\n\n    location /api/ {\n      proxy_pass http://backend:8000;\n      proxy_set_header Host $host;\n      proxy_set_header X-Real-IP $remote_addr;\n      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n      proxy_set_header X-Forwarded-Proto $scheme;\n    }\n\n    location / {\n      try_files $uri /index.html;\n    }\n  }\n}\n' > /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 