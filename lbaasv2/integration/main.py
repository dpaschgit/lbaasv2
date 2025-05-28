from fastapi import FastAPI
import uvicorn

app = FastAPI(title="LBaaS Integration Service")

@app.get("/")
def read_root():
    return {"message": "Integration service running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

