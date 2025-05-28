FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Use absolute paths and verify installation
RUN /usr/local/bin/pip install --no-cache-dir -r requirements.txt && \
    /usr/local/bin/pip install --no-cache-dir uvicorn && \
    /usr/local/bin/pip list | grep uvicorn

COPY . .

EXPOSE 8000

# Use the full path to uvicorn or use python -m
CMD ["/usr/local/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
