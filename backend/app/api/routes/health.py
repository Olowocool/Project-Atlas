from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Return the API health status.
    """
    return {
        "status": "ok",
        "service": "atlas-api",
        "version": "0.1.0",
    }