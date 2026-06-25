from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 여러줄 주석 C+/
# # get : 주소창으로 데이터 보내기
# # 주소창 사용/간단조회/검색 느낌
# @app.get("/")
# def home():
#     return {"message": "mom-subway api running"}

# # 기본인사
# # http://127.0.0.1:8000/hello 
# @app.get("/hello")
# def hello():
#     return {"message": "안녕하세요"}

# # 이름 받기
# # http://127.0.0.1:8000/user?name=yirang
# @app.get("/user")
# def user(name: str):
#     return {"name": name}

# # 숫자 계산
# # http://127.0.0.1:8000/add?a=3&b=5
# @app.get("/add")
# def add(a: int, b: int):
#     return {"result": a + b}


# post : 주소창으로 데이터 보내기
# body 사용 / body 사용 / 저장/전송 느낌
# 채팅
class ChatRequest(BaseModel):
    message: str # 입력값 


@app.post("/chat")
def chat(data: ChatRequest):
    return {
        "message": data.message #결과값
    }

class LoginRequest(BaseModel):
    id: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    return {
        "id": data.id,
        "message": "로그인 완료"
    }

class FoodRequest(BaseModel):
    food: str 


@app.post("/food")
def food(data: FoodRequest):
    return {
        "recommend": f"{data.food} 정말 맛있죠"
    }