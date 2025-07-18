# Build React app
FROM node:18 AS builder
WORKDIR /app
COPY . .
RUN npm ci && npm run build

# Serve with simple http server
FROM node:18-slim
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist .
EXPOSE 3000
CMD ["serve", "-s", ".", "-l", "3000"]