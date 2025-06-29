from fastapi import APIRouter

router = APIRouter()

<<<<<<< HEAD
# ✅ Upload route
=======
# Optional: Import sub-routers safely
>>>>>>> project-a-branch
try:
    from .upload import router as upload_router
    router.include_router(upload_router, prefix="/upload", tags=["Upload"])
except ImportError as e:
    print("⚠️ Could not import upload.py:", e)

<<<<<<< HEAD
# ✅ Q&A route
=======
>>>>>>> project-a-branch
try:
    from .query import router as query_router
    router.include_router(query_router, prefix="/ask", tags=["Q&A"])
except ImportError as e:
    print("⚠️ Could not import query.py:", e)

<<<<<<< HEAD
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
=======
try:
    from .tasks import router as tasks_router
    router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
except ImportError as e:
    print("⚠️ Could not import tasks.py:", e)

# Add a base route for testing
>>>>>>> project-a-branch
@router.get("/")
def root():
    return {"message": "TenderIQ API router is live"}
