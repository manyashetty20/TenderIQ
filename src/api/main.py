from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # ✅ ADD THIS
from src.api.routes import router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is working"}

app.include_router(router)

# ✅ ADD THIS LINE TO SERVE FILES FROM data/uploads/
app.mount("/static", StaticFiles(directory="data/uploads"), name="static")
