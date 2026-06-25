# 실시간 지하철 도착정보 API 담당
# arrival_service.py


# 환경변수 사용
import os
# 실시간 지하철 도착정보 API 처리
import requests
# .env 파일 읽기
from dotenv import load_dotenv
# .env 불러오기
load_dotenv()


# .env에서 인증키 가져오기
API_KEY = os.getenv("ARRIVAL_SERVICE_KEY")


def get_realtime_station_arrival(station_name):
    """
    역 이름으로 실시간 도착정보 가져오기
    """

    # API 키 확인
    if not API_KEY:
        print("[에러] ARRIVAL_SERVICE_KEY 없음")
        return {
            "error": "missing_api_key",
            "message": "API 인증키가 없습니다."
        }

    # 조회 시작
    print(f"[API 요청 시작] {station_name}역")

    # 서울시 지하철 도착정보 API 주소
    url = f"http://swopenAPI.seoul.go.kr/api/subway/{API_KEY}/json/realtimeStationArrival/0/5/{station_name}"

    # URL 생성 확인
    print("[URL 생성 완료]")
    print(url)

    try:
        # API 요청 직전 확인
        print("[requests.get 실행 직전]")

        # API 요청 보내기
        # timeout=10: 10초 안에 응답 없으면 중단
        response = requests.get(url, timeout=10)

        # API 요청 완료 확인
        print("[requests.get 실행 완료]")

        # 응답 코드 확인
        print(f"[응답 코드] {response.status_code}")

        # 응답 원문 일부 확인
        print("[응답 원문 일부]")
        print(response.text[:500])

        # JSON → 파이썬 데이터
        api_data = response.json()

        # 변환 확인
        print("[JSON 변환 완료]")

        # API 결과 반환
        return api_data

    except requests.exceptions.Timeout:
        # API 서버가 10초 안에 응답하지 않은 경우
        print("[에러] API 응답 시간 초과")

        return {
            "success": False,
            "status": "delayed",
            "error": "timeout",
            "message": "서울시 API 응답이 지연되고 있습니다."
        }

    except requests.exceptions.RequestException as error:
        # 인터넷 연결, URL, 서버 요청 문제
        print("[에러] API 요청 실패")
        print(error)

        return {
            "error": "request_failed",
            "message": "서울시 API 요청에 실패했습니다."
        }

    except ValueError:
        # JSON 변환 실패
        print("[에러] JSON 변환 실패")
        print(response.text[:500])

        return {
            "error": "json_error",
            "message": "API 응답을 JSON으로 바꾸지 못했습니다."
        }


def make_arrival_message(station_name):
    """
    도착정보를 안내 문장으로 변환
    """

    # 문장 변환 시작
    print(f"[문장 변환 시작] {station_name}역")

    # API 데이터 받기
    api_data = get_realtime_station_arrival(station_name)

    # API 요청 자체가 실패한 경우
    if "error" in api_data:
        print("[조회 실패] API 요청 에러")
        return [api_data["message"]]

    # 도착정보 없을 때
    if "realtimeArrivalList" not in api_data:
        print("[조회 실패] realtimeArrivalList 없음")
        print("[API 응답 확인]")
        print(api_data)

        return [f"{station_name}역 도착 정보를 가져오지 못했습니다."]

    # 도착정보 확인
    print("[조회 성공]")

    # 열차 목록 꺼내기
    arrival_list = api_data["realtimeArrivalList"]

    # 열차 개수 확인
    print(f"[열차 개수] {len(arrival_list)}개")

    # 엄마용 안내 문장 리스트
    mom_messages = []

    # 열차 정보 하나씩 처리
    for index, train in enumerate(arrival_list, start=1):
        print(f"[{index}번째 처리]")

        # 목적지와 방면
        train_line = train["trainLineNm"]

        # 도착 상태
        arrival_msg = train["arvlMsg2"]

        # 현재 위치
        current_station = train["arvlMsg3"]

        # 상행/하행
        updown_line = train["updnLine"]

        # 막차 여부
        last_car = train["lstcarAt"]

        # 막차 문구 변환
        if last_car == "1":
            last_car_text = "막차입니다"
        else:
            last_car_text = "막차는 아닙니다"

        # 안내 문장 생성
        message = (
            f"{train_line} 열차는 {arrival_msg}입니다. "
            f"현재 위치는 {current_station}, 방향은 {updown_line}입니다. "
            f"{last_car_text}."
        )

        # 리스트에 추가
        mom_messages.append(message)

    # 문장 개수 확인
    print(f"[완료] {len(mom_messages)}개")

    # 안내 문장 반환
    return mom_messages


def get_arrival_by_station(station_name):
    """
    역 이름 기준 도착정보 조회
    """

    # 도착정보 생성
    messages = make_arrival_message(station_name)

    # 결과 반환
    return {
        "station_name": station_name,
        "count": len(messages),
        "messages": messages
    }