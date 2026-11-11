from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def root():
    return {
        "message": "Welcome to OpsBridge",
        "application": "OpsBridge",
        "version": "1.0.0"
    }

@router.get("/health")
def health_check():
    return {"status": "healthy"}
