# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy all source code first
COPY . .

# Fix npm rollup issue by removing and reinstalling
RUN rm -rf node_modules package-lock.json && \
    npm install && \
    npm run build

# Production stage - use nginx
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create start script that Railway expects
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'nginx -g "daemon off;"' >> /start.sh && \
    chmod +x /start.sh

# Expose port
EXPOSE 80

# Use the start script
CMD ["/start.sh"]