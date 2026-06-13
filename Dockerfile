# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Set relative API path for the unified deployment
ENV VITE_API_BASE_URL=/api
RUN npm run build

# Stage 2: Build the FastAPI backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# Copy React static assets from Stage 1 builder
COPY --from=frontend-builder /app/frontend/dist ./dist

# Port that Cloud Run routes traffic to
ENV PORT=8080
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
