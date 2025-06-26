from fastapi import FastAPI
from src.api.routes import router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is working"}

app.include_router(router)
