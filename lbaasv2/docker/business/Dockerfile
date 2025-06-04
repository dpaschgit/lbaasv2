FROM python:3.11-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Create main.py directly in the container
RUN echo 'from fastapi import FastAPI\n\napp = FastAPI(title="LBaaS Business Service")\n\n@app.get("/")\ndef read_root():\n    return {"message": "Business service running"}\n\n@app.get("/health")\ndef health_check():\n    return {"status": "healthy"}' > /app/main.py

EXPOSE 8001

# Use a simple command that will definitely work
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

