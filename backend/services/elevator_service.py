# 서울 지하철 엘리베이터 정보 
# elevator_service.py

import requests
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# .env 안의 SERVICE_KEY 가져오기
API_KEY = os.getenv("SERVICE_KEY")


def get_elevator_data(start_index=1, end_index=5):
    """
    엘리베이터 원본 데이터를 가져오는 함수
    """

    print("[엘리베이터 API 요청 준비 시작]")

    # 인증키가 없으면 요청 중단
    if not API_KEY:
        print("[인증키 오류]")
        print(".env 파일의 SERVICE_KEY 값을 확인하세요.")
        return None

    # 응답 형식
    # json은 파이썬에서 다루기 쉬움
    file_type = "json"

    # API 서비스명
    # 엘리베이터 위치 정보 서비스
    service_name = "tbTraficElvtr"

    print("[요청 정보 확인]")

    # 인증키 전체 출력 방지
    # 앞 5글자만 확인
    print("API KEY:", API_KEY[:5] + "****")

    print("파일 타입:", file_type)
    print("서비스명:", service_name)
    print("시작 번호:", start_index)
    print("끝 번호:", end_index)

    # 서울 열린데이터광장 API 주소 구조
    # 인증키 / 파일타입 / 서비스명 / 시작번호 / 끝번호
    url = (
        f"http://openapi.seoul.go.kr:8088/"
        f"{API_KEY}/"
        f"{file_type}/"
        f"{service_name}/"
        f"{start_index}/"
        f"{end_index}/"
    )

    print("[요청 URL 생성 완료]")

    # URL에는 인증키가 포함됨
    # 실제 운영에서는 전체 출력하지 않는 것이 좋음
    print(url.replace(API_KEY, API_KEY[:5] + "****"))

    print("[API 요청 시작]")

    try:
        # API에 실제 요청 보내기
        # timeout=10은 10초까지만 기다린다는 뜻
        response = requests.get(url, timeout=10)

    except requests.exceptions.RequestException as error:
        # 인터넷 문제
        # 서버 연결 문제
        # 요청 시간 초과 등
        print("[API 요청 오류]")
        print(error)
        return None

    print("[API 응답 도착]")
    print("상태 코드:", response.status_code)

    # 응답이 너무 길 수 있음
    # 앞부분 500자만 확인
    print("[응답 원문 앞부분]")
    print(response.text[:500])

    # 200이 아니면 요청 실패
    if response.status_code != 200:
        print("[요청 실패]")
        print(response.text)
        return None

    print("[JSON 변환 시작]")

    try:
        # JSON 문자열을 파이썬 dict로 변환
        data = response.json()

    except ValueError:
        # JSON 형식이 아닐 때 발생
        print("[JSON 변환 실패]")
        print(response.text)
        return None

    print("[JSON 변환 완료]")

    # 정상이라면 tbTraficElvtr 키가 보여야 함
    print("[최상위 키 확인]")
    print(data.keys())

    # 원본 데이터 반환
    return data


def split_node_wkt(node_wkt):
    """
    NODE_WKT에서 경도와 위도 분리

    예:
    POINT(126.97312061611817 37.557295350602715)
    """

    print("[좌표 분리 시작]")
    print("원본 NODE_WKT:", node_wkt)

    # 좌표값이 없으면 종료
    if not node_wkt:
        print("[좌표 없음]")
        return None, None

    try:
        # POINT( 제거
        # ) 제거
        point_text = node_wkt.replace("POINT(", "").replace(")", "")

        # 공백 기준으로 나누기
        # 결과 예: ["126.9731", "37.5572"]
        parts = point_text.strip().split()

        # 서울시 데이터는 경도, 위도 순서
        longitude = parts[0]
        latitude = parts[1]

        print("경도:", longitude)
        print("위도:", latitude)
        print("[좌표 분리 완료]")

        return longitude, latitude

    except Exception as error:
        # 좌표 형식이 다를 때 대비
        print("[좌표 분리 오류]")
        print(error)
        return None, None


def make_elevator_message(station_name, longitude, latitude):
    """
    엘리베이터 1개 안내 문구 생성
    """

    print("[개별 안내 문구 생성 시작]")

    # 엘리베이터 1개에 대한 문장
    message = (
        f"{station_name} 주변 엘리베이터 위치 정보가 확인되었습니다. "
        f"이 엘리베이터 위치는 경도 {longitude}, "
        f"위도 {latitude} 지점입니다. "
        f"현재 맘서브웨이 지도 기능은 준비 중입니다."
    )

    print("[개별 안내 문구 생성 완료]")
    print(message)

    return message


def parse_elevator_data(data):
    """
    API 원본 데이터에서 필요한 값만 정리
    """

    print("[엘리베이터 데이터 정리 시작]")

    # 원본 데이터가 없으면 종료
    if data is None:
        print("[정리 실패] 데이터 없음")
        return []

    # 서울 열린데이터광장 응답의 최상위 키
    service_key = "tbTraficElvtr"

    # 응답 안에 tbTraficElvtr이 없으면 실패
    if service_key not in data:
        print("[정리 실패] tbTraficElvtr 키 없음")
        print("현재 응답:", data)
        return []

    # 실제 엘리베이터 데이터 블록
    elevator_block = data[service_key]

    # 전체 데이터 개수
    print("[총 데이터 개수]")
    print(elevator_block.get("list_total_count"))

    # 요청 결과 정보
    result_info = elevator_block.get("RESULT", {})

    # 요청 결과 코드
    print("[요청 결과 코드]")
    print(result_info.get("CODE"))

    # 요청 결과 메시지
    print("[요청 결과 메시지]")
    print(result_info.get("MESSAGE"))

    # 실제 엘리베이터 목록
    rows = elevator_block.get("row", [])

    # 목록이 없으면 빈 리스트 반환
    if not rows:
        print("[정리 종료] row 데이터 없음")
        return []

    print("[이번에 받아온 row 개수]")
    print(len(rows))

    # 정리된 엘리베이터 데이터를 담을 리스트
    elevator_list = []

    # row 데이터를 하나씩 처리
    for index, row in enumerate(rows, start=1):
        print(f"[{index}번째 데이터 처리 시작]")

        # 원본 좌표
        node_wkt = row.get("NODE_WKT")

        # 좌표를 경도와 위도로 분리
        longitude, latitude = split_node_wkt(node_wkt)

        # 역 이름
        station_name = row.get("SBWY_STN_NM")

        # 엘리베이터 1개 안내 문구 생성
        message = make_elevator_message(
            station_name=station_name,
            longitude=longitude,
            latitude=latitude
        )

        # 필요한 값만 새 dict로 정리
        elevator = {
            # 노드 유형
            "node_type": row.get("NODE_TYPE"),

            # 원본 좌표
            "node_wkt": node_wkt,

            # 분리한 경도
            "longitude": longitude,

            # 분리한 위도
            "latitude": latitude,

            # 노드 ID
            "node_id": row.get("NODE_ID"),

            # 노드 유형 코드
            "node_type_code": row.get("NODE_TYPE_CD"),

            # 구 코드
            "district_code": row.get("SGG_CD"),

            # 구 이름
            "district_name": row.get("SGG_NM"),

            # 동 코드
            "dong_code": row.get("EMD_CD"),

            # 동 이름
            "dong_name": row.get("EMD_NM"),

            # 지하철역 코드
            "station_code": row.get("SBWY_STN_CD"),

            # 지하철역 이름
            "station_name": station_name,

            # 사용자 안내 문구
            "message": message
        }

        print("노드 ID:", elevator["node_id"])
        print("역 이름:", elevator["station_name"])
        print("구 이름:", elevator["district_name"])
        print("동 이름:", elevator["dong_name"])
        print("좌표:", elevator["node_wkt"])
        print("경도:", elevator["longitude"])
        print("위도:", elevator["latitude"])

        # 정리된 데이터를 리스트에 추가
        elevator_list.append(elevator)

        print(f"[{index}번째 데이터 처리 완료]")

    print("[엘리베이터 데이터 정리 완료]")

    return elevator_list


def make_elevator_summary_message(station_name, elevator_list):
    """
    엘리베이터 전체 안내 문구 생성
    """

    print("[전체 안내 문구 생성 시작]")
    print("역 이름:", station_name)
    print("엘리베이터 개수:", len(elevator_list))

    # 검색 결과가 없을 때
    if len(elevator_list) == 0:
        message = f"{station_name} 주변 엘리베이터 위치 정보를 찾지 못했습니다."
        print(message)
        return message

    # 첫 문장
    # 총 몇 개인지 안내
    message = f"{station_name} 주변 엘리베이터 위치 정보가 {len(elevator_list)}개 확인되었습니다.\n\n"

    # 엘리베이터 좌표를 하나씩 추가
    for index, elevator in enumerate(elevator_list, start=1):
        longitude = elevator.get("longitude")
        latitude = elevator.get("latitude")

        message += (
            f"{index}번째 위치는 "
            f"경도 {longitude}, "
            f"위도 {latitude} 지점입니다.\n"
        )

    # 마지막 문장
    message += "\n현재 맘서브웨이 지도 기능은 준비 중입니다."

    print("[전체 안내 문구 생성 완료]")
    print(message)

    return message

# main.py 리펙토링 

def get_elevator_preview():
    """
    엘리베이터 테스트 데이터 조회
    """

    # API 원본 데이터 요청
    raw_data = get_elevator_data(start_index=1, end_index=5)

    # 필요한 데이터만 정리
    elevator_list = parse_elevator_data(raw_data)

    # 조회 결과 반환
    return {
        "success": True,
        "message": "엘리베이터 데이터 조회 완료",
        "count": len(elevator_list),
        "data": elevator_list
    }


def get_elevator_by_station(station_name):
    """
    역 이름 기준 엘리베이터 검색
    """

    # 역 제거
    # 서울역 → 서울
    search_station_name = station_name.replace("역", "")

    # 전체 엘리베이터 데이터 조회
    raw_data = get_elevator_data(start_index=1, end_index=600)

    # 데이터 정리
    elevator_list = parse_elevator_data(raw_data)

    # 검색 결과 저장
    matched_elevators = []

    # 역 이름 비교
    for elevator in elevator_list:

        # API 역 이름
        data_station_name = elevator.get("station_name")

        # 역 제거
        clean_data_station_name = str(
            data_station_name
        ).replace("역", "")

        # 역 이름 일치
        if clean_data_station_name == search_station_name:
            matched_elevators.append(elevator)

    # 검색 결과 없음
    if len(matched_elevators) == 0:

        final_message = (
            f"{station_name} 주변 "
            f"엘리베이터 위치 정보를 찾지 못했습니다."
        )

        return {
            "success": False,
            "station_name": station_name,
            "message": final_message,
            "count": 0,
            "data": []
        }

    # 안내 문구 생성
    final_message = make_elevator_summary_message(
        station_name=station_name,
        elevator_list=matched_elevators
    )

    # 검색 결과 반환
    return {
        "success": True,
        "station_name": station_name,
        "message": final_message,
        "count": len(matched_elevators),
        "data": matched_elevators
    }

    # final_message = make_elevator_summary_message(
    #     station_name=station_name,
    #     elevator_list=matched_elevators
    # )

    # return {
    #     "success": True,
    #     "station_name": station_name,
    #     "message": final_message,
    #     "count": len(matched_elevators),
    #     "data": matched_elevators
    # }