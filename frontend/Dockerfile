# Build React app
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
# Fix rollup issue by removing lock file
RUN rm -rf node_modules package-lock.json && \
    npm install && \
    npm run build

# Serve with simple http server
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist .
EXPOSE 3000
CMD ["serve", "-s", ".", "-l", "3000"]