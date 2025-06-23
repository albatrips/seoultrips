from fastapi import APIRouter, HTTPException, Query
from server.services.korea_tour_api import get_related_tour_info

router = APIRouter(prefix="/related", tags=["related"])

@router.get("/attractions")
async def get_related_attractions(
    keyword: str = Query(..., title="Keyword", description="Keyword to search for related attractions"),
    area_code: int = Query(1, title="Area Code", description="Code for the city/province"),
    sigungu_code: int = Query(1, title="Sigungu Code", description="Code for the district"),
    base_ym: str = Query("202503", title="Base YM", description="Base year and month (YYYYMM)")
):
    """
    키워드에 해당하는 연관 관광지 정보를 조회합니다.
    """
    try:
        data = get_related_tour_info(
            keyword=keyword,
            area_code=area_code,
            sigungu_code=sigungu_code,
            base_ym=base_ym
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 