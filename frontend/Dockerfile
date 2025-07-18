# Multi-stage build for production optimization
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy all source code first
COPY . .

# Clean install with build fix
RUN rm -rf node_modules package-lock.json && \
    npm install && \
    npm run build

# Production stage with Nginx
FROM nginx:alpine as production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx PID directory
RUN mkdir -p /var/run/nginx

# Create executable script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'nginx -g "daemon off;"' >> /start.sh && \
    chmod +x /start.sh

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["/start.sh"]