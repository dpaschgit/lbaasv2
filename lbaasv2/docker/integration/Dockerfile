FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Make sure uvicorn is explicitly installed
RUN pip install --no-cache-dir uvicorn

COPY . .

EXPOSE 8002

# Use python -m to run uvicorn instead of calling uvicorn directly
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
