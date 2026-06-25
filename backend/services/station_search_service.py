# 역 검색 서비스
import json

# 역 코드 JSON 경로
STATIONS_JSON_PATH = "data/stations.json"

# 역 코드 데이터 로드
# 서버 실행 시 stations.json 한 번만 읽기
with open(STATIONS_JSON_PATH, "r", encoding="utf-8") as file:
    STATION_DATA = json.load(file)


def normalize_station_name(station_name: str):
    # 역 이름 정리
    # 예: 청량리역 → 청량리
    return station_name.replace("역", "").strip()


def search_station_by_name(station_name: str):
    """
    역 이름으로 후보 역 검색

    흐름:
    1. 사용자 입력값 정리
    2. stations.json에서 역 이름 검색
    3. 후보 없음 / 후보 1개 / 후보 여러 개 구분
    4. 후보 목록 반환
    """

    # 검색어 정리
    keyword = normalize_station_name(station_name)

    # 역 후보 검색
    candidates = STATION_DATA.get(keyword)

    # 검색 결과 없음
    if not candidates:
        return {
            "success": False,
            "need_select_station": False,
            "message": f"{station_name}에 해당하는 역 정보를 찾지 못했어요.",
            "count": 0,
            "candidates": []
        }

    # 후보 1개
    if len(candidates) == 1:
        return {
            "success": True,
            "need_select_station": False,
            "message": f"{keyword}역 정보를 찾았어요.",
            "count": 1,
            "candidates": candidates
        }

    # 후보 여러 개
    return {
        "success": True,
        "need_select_station": True,
        "message": f"{keyword}역은 여러 노선에 있어요. 조회할 노선을 선택해 주세요.",
        "count": len(candidates),
        "candidates": candidates
    }