import os
import requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
load_dotenv()

BASE_URL = "http://apis.data.go.kr/B551011"
SERVICE_KEY = os.getenv("TOUR_API_SERVICE_KEY")

def get_location_based_list(area_code: int, sigungu_code: int, page_no: int = 1, num_of_rows: int = 1000):
    """지역 기반 관광정보 조회"""
    url = f"{BASE_URL}/KorService2/areaBasedList2"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "MobileOS": "ETC",
        "MobileApp": "alba",
        "areaCode": area_code,
        "sigunguCode": sigungu_code,
        # "_type": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    results = []
    items = root.findall(".//body/items/item")
    for item in items:
        # findtext() 메소드를 사용하여 항목이 없을 경우 None을 반환하도록 합니다.
        title = item.findtext("title")
        addr1 = item.findtext("addr1")
        ldong_regn_cd = item.findtext("lDongRegnCd")
        ldong_signgu_cd = item.findtext("lDongSignguCd")

        results.append(
            {
                "title": title,
                "addr1": addr1,
                "lDongRegnCd": ldong_regn_cd,
                "lDongSignguCd": ldong_signgu_cd,
                "nsigungu_code": ldong_regn_cd + ldong_signgu_cd
            }
        )
    return results

    return response.json()

def get_visitor_stats(area_code: int, sigungu_code: int, page_no: int = 1, num_of_rows: int = 1000):
    """관광지 방문자 수 조회"""
    url = f"{BASE_URL}/TatsCnctrRateService/tatsCnctrRatedList"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "MobileOS": "ETC",
        "MobileApp": "alba",
        "areaCd": area_code,
        "signguCd": sigungu_code,
        "_type": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_related_tour_info(keyword: str, area_code: int, sigungu_code: int, base_ym: str, page_no: int = 1, num_of_rows: int = 10):
    """연관 관광지 정보 조회"""
    url = f"{BASE_URL}/TarRlteTarService1/searchKeyword1"
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "MobileOS": "ETC",
        "MobileApp": "alba",
        "keyword": keyword,
        "areaCd": area_code,
        "signguCd": sigungu_code,
        "baseYm": base_ym,
        "_type": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json() 