from fastapi import APIRouter, HTTPException, Query
from server.services.korea_tour_api import get_visitor_stats

router = APIRouter(prefix="/visitors", tags=["visitors"])

@router.get("/concentration")
async def get_visitor_concentration(
    area_code: int = Query(1, title="Area Code", description="Code for the city/province"),
    sigungu_code: int = Query(1, title="Sigungu Code", description="Code for the district")
):
    """
    관광지 방문자 집중률을 조회합니다.
    기간은 API에서 제공하는 최신 데이터를 기준으로 합니다. (현재 하드코딩)
    """
    try:
        data = get_visitor_stats(area_code=area_code, sigungu_code=sigungu_code)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 