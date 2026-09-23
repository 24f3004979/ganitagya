from fastapi import APIRouter
from server.api.controllers import Registration

router = APIRouter()

@router.get("/health")
def  health():
    return {"status":"ok", "version":"0.01"}
