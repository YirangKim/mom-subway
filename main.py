# main.py
from fastapi import FastAPI # FastAPI 백엔드 서버
from fastapi.middleware.cors import CORSMiddleware #프론트에서 백엔드 요청 
# 도착정보 서비스
from backend.services.arrival_service import get_arrival_by_station
# 엘리베이터 서비스
from backend.services.elevator_service import (
    get_elevator_preview,
    get_elevator_by_station
)
# 수유실 정보 
from backend.services.dairy_room_service import get_dairy_room_summary_by_station_name

from pydantic import BaseModel
from ai.services.ai_router_service import handle_ai_request

class AiAskRequest(BaseModel):
    station_name: str
    message: str

# FastAPI 앱을 생성합니다.
app = FastAPI(
    title="맘서브웨이 API",
    description="수유실, 엘리베이터, 열차 도착정보 안내 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# 프론트엔드에서 이 백엔드 서버에 접근 허용
# "*"로 전체 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 상태 확인
@app.get(
    "/",
    tags=["기본"],
    summary="서버 상태 확인"
)
def home():

    return {
        "message": "맘서브웨이 백엔드 서버 실행 중"
    }

# 실시간 도착정보
@app.get(
    "/arrival",
    tags=["도착정보"],
    summary="실시간 도착정보 조회"
)
def get_arrival(station_name: str):

    return get_arrival_by_station(station_name)


# 엘리베이터 테스트
@app.get(
    "/elevators",
    tags=["엘리베이터"],
    summary="엘리베이터 테스트 데이터 조회"
)
def elevators():

    # 테스트 데이터 조회
    return get_elevator_preview()


# 역별 엘리베이터 조회
@app.get(
    "/elevator",
    tags=["엘리베이터"],
    summary="역 이름 기준 엘리베이터 조회"
)
def get_elevator(station_name: str):

    # 역 이름 검색
    return get_elevator_by_station(station_name)

#수유실 정보
@app.get("/dairy-room")
def dairy_room(station_name: str):
    # 수유실 요약 결과 반환
    return get_dairy_room_summary_by_station_name(station_name)


@app.post(
    "/ai/ask",
    tags=["AI"],
    summary="사용자 자연어 요청 intent 분류 및 기능 실행"
)
def ask_ai(request: AiAskRequest):
    result = handle_ai_request(
        station_name=request.station_name,
        message=request.message
    )

    return result