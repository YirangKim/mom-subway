# 원본 JSON을 역명 기준 JSON으로 변환
import os
import json


# 현재 파일이 있는 폴더 경로
CURRENT_DIR = os.path.dirname(__file__)


# 1단계에서 만든 원본 JSON 경로
RAW_JSON_PATH = os.path.join(CURRENT_DIR, "station_code_raw.json")


# 2단계에서 저장할 검색용 JSON 경로
STATIONS_JSON_PATH = os.path.join(CURRENT_DIR, "stations.json")


def normalize_station_name(station_name):
    # 역 이름 정리
    # 예: 소요산역 → 소요산
    return str(station_name).replace("역", "").strip()


def get_value(row, key):
    # 값 가져오기
    value = row.get(key)

    # 빈 값 처리
    if value is None:
        return ""

    # 문자열 변환
    return str(value).strip()


def print_progress(step, total_step, message):
    # 진행률 계산
    percent = int((step / total_step) * 100)

    # 진행률 출력
    print(f"[{percent}%] {message}")


def convert_raw_json_to_stations_json():
    # 전체 단계 수
    total_step = 5

    # 시작 로그
    print_progress(0, total_step, "역명 기준 JSON 변환 시작")

    # 원본 JSON 읽기
    print_progress(1, total_step, "station_code_raw.json 읽는 중")
    with open(RAW_JSON_PATH, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    # 변환 결과 저장
    print_progress(2, total_step, "역명 기준으로 데이터 정리 중")
    station_dict = {}

    # 원본 데이터 반복
    for row in raw_data:
        # 역 이름 정리
        station_name = normalize_station_name(
            get_value(row, "STIN_NM")
        )

        # 빈 역명 제외
        if not station_name:
            continue

        # 원본 파라미터 그대로 정리
        station_info = {
            "RAIL_OPR_ISTT_CD": get_value(row, "RAIL_OPR_ISTT_CD"),
            "RAIL_OPR_ISTT_NM": get_value(row, "RAIL_OPR_ISTT_NM"),
            "LN_CD": get_value(row, "LN_CD"),
            "LN_NM": get_value(row, "LN_NM"),
            "STIN_CD": get_value(row, "STIN_CD"),
            "STIN_NM": get_value(row, "STIN_NM"),
        }

        # 같은 역명이 처음 나온 경우
        if station_name not in station_dict:
            station_dict[station_name] = []

        # 같은 역명 목록에 추가
        station_dict[station_name].append(station_info)

    # 역명 가나다순 정렬
    print_progress(3, total_step, "역명 가나다순 정렬 중")
    sorted_station_dict = dict(
        sorted(station_dict.items(), key=lambda item: item[0])
    )

    # JSON 저장
    print_progress(4, total_step, "stations.json 저장 중")
    with open(STATIONS_JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(
            sorted_station_dict,
            file,
            ensure_ascii=False,
            indent=2
        )

    # 완료 로그
    print_progress(5, total_step, "역명 기준 JSON 변환 완료")
    print("====================================")
    print("stations.json 생성 완료")
    print(f"저장 위치: {STATIONS_JSON_PATH}")
    print(f"원본 행 개수: {len(raw_data)}개")
    print(f"역 이름 개수: {len(sorted_station_dict)}개")
    print("====================================")


# 직접 실행
if __name__ == "__main__":
    convert_raw_json_to_stations_json()