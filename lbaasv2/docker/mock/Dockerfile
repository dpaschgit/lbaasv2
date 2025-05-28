FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create placeholder api.py files for the mock services if they don't exist
RUN echo 'from fastapi import FastAPI\nimport uvicorn\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"message": "Mock service running"}\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="0.0.0.0", port=8010)' > api.py

EXPOSE 8010 8011 8012

# Use python directly to run the script
CMD ["python", "api.py"]

