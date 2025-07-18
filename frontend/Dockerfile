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

# Create non-root user for security
RUN addgroup -g 1001 -S pmcell && \
    adduser -S pmcell -u 1001

# Set ownership of nginx files
RUN chown -R pmcell:pmcell /var/cache/nginx && \
    chown -R pmcell:pmcell /var/log/nginx && \
    chown -R pmcell:pmcell /etc/nginx/conf.d

# Create nginx PID directory
RUN mkdir -p /var/run/nginx && \
    chown -R pmcell:pmcell /var/run/nginx

# Create executable script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'nginx -g "daemon off;"' >> /start.sh && \
    chmod +x /start.sh

# Switch to non-root user  
USER pmcell

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["/start.sh"]