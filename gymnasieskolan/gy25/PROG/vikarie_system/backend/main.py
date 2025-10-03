from fastapi import FastAPI
from app.routers import substitutes, assignments, attendance

app = FastAPI(title="Vikarie Management System", version="0.1.0")

app.include_router(substitutes.router, prefix="/substitutes", tags=["substitutes"])
app.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])

@app.get("/")
async def root():
    return {"message": "Vikarie Management System API"}
