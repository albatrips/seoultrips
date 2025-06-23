import csv
from fastapi import APIRouter, HTTPException, Path
from server.services.korea_tour_api import get_location_based_list

router = APIRouter(prefix="/location", tags=["location"])

SEOUL_AREA_CODE = 1

def get_sigungu_code(district_name: str) -> int | None:
    """
    seoul_sigungu_codes.csv 파일에서 지역구 이름에 해당하는 코드를 찾아 반환합니다.
    """
    try:
        with open("seoul_sigungu_codes.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Header skip
            for code, name in reader:
                if name == district_name:
                    return int(code)
    except FileNotFoundError:
        return None
    return None


@router.get("/attractions/{district_name}")
async def get_attractions_by_district(
    district_name: str = Path(..., title="District Name", description="Name of the district in Seoul")
):
    """
    특정 지역구의 관광지 정보를 조회합니다.
    """
    sigungu_code = get_sigungu_code(district_name)
    if sigungu_code is None:
        raise HTTPException(status_code=404, detail=f"District '{district_name}' not found.")

    try:
        data = get_location_based_list(area_code=SEOUL_AREA_CODE, sigungu_code=sigungu_code)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    

@router.get("/attractions/recommend")
async def get_recommend_attractions(
    
):
    """
    특정 지역구의 관광지 정보를 조회합니다.
    """
    sigungu_code = get_sigungu_code(district_name)
    if sigungu_code is None:
        raise HTTPException(status_code=404, detail=f"District '{district_name}' not found.")

    try:
        data = get_location_based_list(area_code=SEOUL_AREA_CODE, sigungu_code=sigungu_code)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 