# Frontend Dockerfile for React/Vite app

FROM node:20-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Development server
CMD ["npm", "run", "dev", "--", "--host"]

