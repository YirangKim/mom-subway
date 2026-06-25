from fastapi import FastAPI

from services.arrival_service import get_arrival
from services.congestion_service import get_congestion
from services.dairy_room_service import get_dairy_room

app = FastAPI()


@app.get("/")
def home():
    return {"message": "mom-subway api running"}


@app.get("/arrival")
def arrival():
    return get_arrival()


@app.get("/congestion")
def congestion():
    return get_congestion()


@app.get("/dairy-room")
def dairy_room():
    return get_dairy_room()