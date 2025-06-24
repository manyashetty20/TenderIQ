from fastapi import APIRouter

router = APIRouter()

# Optional: Import sub-routers safely
try:
    from .upload import router as upload_router
    router.include_router(upload_router, prefix="/upload", tags=["Upload"])
except ImportError as e:
    print("⚠️ Could not import upload.py:", e)

try:
    from .query import router as query_router
    router.include_router(query_router, prefix="/ask", tags=["Q&A"])
except ImportError as e:
    print("⚠️ Could not import query.py:", e)

try:
    from .tasks import router as tasks_router
    router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
except ImportError as e:
    print("⚠️ Could not import tasks.py:", e)

# Add a base route for testing
@router.get("/")
def root():
    return {"message": "TenderIQ API router is live"}
