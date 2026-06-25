# 수유실 API 호출
import os
import json
import requests
from dotenv import load_dotenv


# 환경변수 로드
load_dotenv()


# 서비스키 가져오기
DAIRYROOM_SERVICE_KEY = os.getenv("DAIRYROOM_SERVICE_KEY")


# 수유실 API 주소
DAIRY_ROOM_API_URL = "https://openapi.kric.go.kr/openapi/convenientInfo/stationDairyRoom"


# 역 코드 JSON 경로
STATIONS_JSON_PATH = "backend/data/stations.json"


# 역 코드 데이터 로드
# 서버 실행 시 한 번만 읽기
with open(STATIONS_JSON_PATH, "r", encoding="utf-8") as file:
    STATION_DATA = json.load(file)


def get_dairy_room_summary_by_station_name(station_name: str):
    """
    역 이름으로 수유실 요약 조회

    흐름:
    1. 역 이름 검색
    2. 같은 이름의 역 후보 전체 조회
    3. 후보별 수유실 API 호출
    4. 요약 + 상세정보 반환
    """

    # 검색어 정리
    keyword = normalize_station_name(station_name)

    # 역 후보 검색
    candidates = STATION_DATA.get(keyword)

    # 역 검색 실패
    if not candidates:
        return {
            "success": False,
            "station_name": keyword,
            "message": f"{station_name}에 해당하는 역 정보를 찾지 못했어요.",
            "candidate_count": 0,
            "dairy_room_count": 0,
            "summary": []
        }

    # 요약 결과 저장
    summary = []

    # 수유실 있는 후보 개수
    dairy_room_count = 0

    # 후보별 수유실 조회
    for station in candidates:
        # 후보 1개 수유실 조회
        dairy_room_result = request_dairy_room_api(station)

        # 수유실 있음 여부
        has_dairy_room = dairy_room_result["has_dairy_room"]

        # 수유실 있음 카운트
        if has_dairy_room:
            dairy_room_count += 1

        # 요약 카드 데이터 저장
        summary.append({
            "title": f"{station['LN_NM']} {station['STIN_NM']}역",
            "has_dairy_room": has_dairy_room,
            "message": dairy_room_result["message"],
            "station": station,

            # 3단계 상세보기용 데이터
            # 프론트에서 클릭 시 이 rooms를 펼치면 됨
            "rooms": dairy_room_result["rooms"]
        })

    # 최종 결과 반환
    return {
        "success": True,
        "station_name": keyword,
        "step": "summary",
        "message": make_summary_message(
            station_name=keyword,
            candidate_count=len(candidates),
            dairy_room_count=dairy_room_count
        ),
        "candidate_count": len(candidates),
        "dairy_room_count": dairy_room_count,
        "summary": summary
    }


def request_dairy_room_api(station: dict):
    """
    후보 역 하나에 대해 수유실 API 호출
    """

    # 서비스키 확인
    if not DAIRYROOM_SERVICE_KEY:
        return {
            "has_dairy_room": False,
            "message": "DAIRYROOM_SERVICE_KEY가 설정되지 않았어요.",
            "rooms": []
        }

    # 요청값 설정
    params = {
        "serviceKey": DAIRYROOM_SERVICE_KEY,
        "format": "json",
        "railOprIsttCd": station["RAIL_OPR_ISTT_CD"],
        "lnCd": station["LN_CD"],
        "stinCd": station["STIN_CD"],
    }

        # ✅ 추가: API 요청 시작 로그
    print(f"[수유실 API] 요청 시작 → 역코드: {station['STIN_CD']}, 노선: {station['LN_CD']}")

    # API 요청
    try:
        response = requests.get(
            DAIRY_ROOM_API_URL,
            params=params,
            timeout=10
        )
        # ✅ 추가: 응답 상태코드 로그
        print(f"[수유실 API] 응답 상태코드: {response.status_code}")

    # ✅ 추가: 연결 오류 잡기
    except requests.exceptions.ConnectionError as e:
        print(f"[수유실 API] 연결 오류 (서버 다운 or 네트워크 문제): {e}")
        return {
            "has_dairy_room": False,
            "message": "수유실 API 서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.",
            "rooms": []
        }

    # ✅ 추가: 타임아웃 오류 잡기
    except requests.exceptions.Timeout:
        print(f"[수유실 API] 타임아웃 오류 → 역코드: {station['STIN_CD']}")
        return {
            "has_dairy_room": False,
            "message": "수유실 API 응답 시간이 초과됐어요.",
            "rooms": []
        }

    # 요청 실패 처리
    if response.status_code != 200:
        return {
            "has_dairy_room": False,
            "message": "수유실 API 요청 실패",
            "rooms": []
        }

    # JSON 변환
    try:
        api_data = response.json()

    # 변환 실패 처리
    except ValueError:
        return {
            "has_dairy_room": False,
            "message": "JSON 변환 실패",
            "rooms": []
        }

    # 응답 헤더 확인
    header = api_data.get("header", {})

    # 조회 개수 확인
    result_count = header.get("resultCnt", 0)

    # 데이터 없음 처리
    if result_count == 0:
        return {
            "has_dairy_room": False,
            "message": "현재 공공데이터 기준 수유실 정보 없음",
            "rooms": []
        }

    # 수유실 목록 꺼내기
    dairy_room_list = api_data.get("body", [])

    # 수유실 상세정보 정리
    rooms = []

    for index, room in enumerate(dairy_room_list, start=1):
        rooms.append({
            "title": f"{index}번째 수유실 정보",
            "운영시간": room.get("utlPsbHr", "운영시간 정보 없음"),
            "위치": room.get("dtlLoc", "위치 정보 없음"),
            "층수": make_floor_text(
                room.get("grndDvNm"),
                room.get("stinFlor")
            ),
            "출구": make_exit_text(room.get("exitNo")),
            "전화번호": room.get("telNo", "전화번호 정보 없음"),
            "시설": {
                "유아용 침대": make_count_text(room.get("larmBabyBedNum")),
                "소파": make_count_text(room.get("larmSofaNum")),
                "전자레인지": make_count_text(room.get("larmOvenNum")),
                "간이세면대": make_count_text(room.get("larmSmpSinkNum")),
            }
        })

    # 수유실 있음 반환
    return {
        "has_dairy_room": True,
        "message": f"수유실 정보 {len(rooms)}개 확인",
        "rooms": rooms
    }


def normalize_station_name(station_name: str):
    # 역 이름 정리
    # 예: 청량리역 → 청량리
    return station_name.replace("역", "").strip()


def make_summary_message(station_name: str, candidate_count: int, dairy_room_count: int):
    # 수유실 정보 없음
    if dairy_room_count == 0:
        return f"현재 공공데이터 기준으로 {station_name}역 수유실 정보가 없어요."

    # 수유실 정보 있음
    return f"{station_name}역 관련 노선 {candidate_count}개 중 {dairy_room_count}개 노선에서 수유실 정보가 확인됐어요."


def make_floor_text(ground_type, floor):
    # 층수 정보 없음
    if ground_type is None and floor is None:
        return "층수 정보 없음"

    # 층수만 없음
    if floor is None:
        return str(ground_type)

    # 층수 변환
    return f"{ground_type} {floor}층"


def make_exit_text(exit_no):
    # 출구 정보 없음
    if exit_no is None:
        return "출구 정보 없음"

    # 출구 변환
    return f"{exit_no}번 출구"


def make_count_text(count):
    # 시설 정보 없음
    if count is None:
        return "정보 없음"

    # 시설 개수 변환
    return f"{count}개"