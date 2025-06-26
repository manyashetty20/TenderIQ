from fastapi import APIRouter

router = APIRouter()

# ✅ Upload route
try:
    from .upload import router as upload_router
    router.include_router(upload_router, prefix="/upload", tags=["Upload"])
except ImportError as e:
    print("⚠️ Could not import upload.py:", e)

# ✅ Q&A route
try:
    from .query import router as query_router
    router.include_router(query_router, prefix="/ask", tags=["Q&A"])
except ImportError as e:
    print("⚠️ Could not import query.py:", e)

# ✅ Tasks route (directly from tasks.py, not tasks/init.py)
try:
    from . import tasks as tasks_router
    router.include_router(tasks_router.router, prefix="/tasks", tags=["Tasks"])
except ImportError as e:
    print("⚠️ Could not import tasks.py:", e)

# ✅ Projects route
try:
    from .project import router as project_router
    router.include_router(project_router, tags=["Projects"])
except ImportError as e:
    print("⚠️ Could not import project.py:", e)

# ✅ Root route (inside router — for testing the routes system)
@router.get("/")
def root():
    return {"message": "TenderIQ API router is live"}
