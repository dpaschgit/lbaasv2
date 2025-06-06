from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Mock service running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8012))
    uvicorn.run(app, host="0.0.0.0", port=port)
