from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.database.mongo import get_database
from app.schemas.dashboard import DashboardOut
from app.services.dashboard_service import DashboardService


router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(current_user: dict = Depends(get_current_user)) -> DashboardOut:
    service = DashboardService(get_database())
    return await service.get_dashboard(user=current_user)
