# Build the FastAPI backend and serve prebuilt React static files
FROM python:3.11-slim
WORKDIR /app

# Install python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files, prebuilt frontend, and database
COPY backend/ ./
COPY frontend/dist ./dist
COPY data/ ./data

# Port that Cloud Run routes traffic to
ENV PORT=8080
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
