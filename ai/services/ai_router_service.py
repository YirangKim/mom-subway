# ai_router_service.py

from ai.models.intent_model import classify_intent, classify_split_multi_intent

from backend.services.dairy_room_service import get_dairy_room_summary_by_station_name
from backend.services.elevator_service import get_elevator_by_station
from backend.services.arrival_service import get_arrival_by_station
#FAQ 
from ai.services.faq_service import get_faq_tip

from ai.services.confidence_service import get_confidence
from ai.services.ai_action_service import get_action_recommendation


def make_dairy_room_answer(station_name: str, dairy_room_data: dict):
    # 수유실 개수 확인
    dairy_room_count = dairy_room_data.get("dairy_room_count", 0)

    if dairy_room_count > 0:
        return f"{station_name}역 기준으로 수유실 {dairy_room_count}개가 확인됐어요."

    return f"{station_name}역 기준으로 현재 확인된 수유실 정보가 없어요."


def make_elevator_answer(station_name: str, elevator_data: dict):
    # 엘리베이터 개수 확인
    elevator_count = elevator_data.get("count", 0)

    if elevator_count > 0:
        return f"엘리베이터 위치 {elevator_count}개가 확인됐어요."

    return "현재 확인된 엘리베이터 위치 정보가 없어요."


def make_arrival_answer(arrival_data: dict):
    # 도착정보 메시지 확인
    messages = arrival_data.get("messages", [])

    if not messages:
        return "열차 도착정보를 확인하지 못했어요."

    # API 지연 메시지 처리
    if arrival_data.get("status") == "delayed":
        return "열차 도착정보는 현재 서울시 API 응답이 지연되고 있어요."

    # 정상 도착정보 메시지 요약
    if len(messages) == 1:
        return messages[0]

    # 여러 개면 앞의 2개까지만 요약
    main_messages = messages[:2]

    return " ".join(main_messages)


def make_total_answer(station_name: str, data: dict):
    # 전체 안내 요약문 생성

    dairy_room_answer = make_dairy_room_answer(
        station_name,
        data.get("dairy_room", {})
    )

    elevator_answer = make_elevator_answer(
        station_name,
        data.get("elevator", {})
    )

    arrival_answer = make_arrival_answer(
        data.get("arrival", {})
    )

    return f"{dairy_room_answer} {elevator_answer} {arrival_answer}"


def make_answer(station_name: str, intent: str, data):
    # intent별 요약문 생성

    if intent == "dairy_room":
        return make_dairy_room_answer(station_name, data)

    if intent == "elevator":
        return make_elevator_answer(station_name, data)

    if intent == "arrival":
        return make_arrival_answer(data)

    if intent == "all":
        return make_total_answer(station_name, data)

    return "요청하신 정보를 확인하기 어려워요."

def make_detail(intent: str, data):
    # 프론트용 핵심 요약 데이터 생성

    if intent == "dairy_room":
        return {
            "dairy_room_count": data.get("dairy_room_count", 0),
            "candidate_count": data.get("candidate_count", 0)
        }

    if intent == "elevator":
        return {
            "elevator_count": data.get("count", 0)
        }

    if intent == "arrival":
        messages = data.get("messages", [])

        arrival_status = "available"

        if data.get("status") == "delayed":
            arrival_status = "delayed"
        elif messages and "지연" in messages[0]:
            arrival_status = "delayed"
        elif not messages:
            arrival_status = "empty"

        return {
            "arrival_status": arrival_status,
            "arrival_count": data.get("count", 0)
        }

    if intent == "all":
        dairy_room_data = data.get("dairy_room", {})
        elevator_data = data.get("elevator", {})
        arrival_data = data.get("arrival", {})

        arrival_messages = arrival_data.get("messages", [])

        arrival_status = "available"

        if arrival_data.get("status") == "delayed":
            arrival_status = "delayed"
        elif arrival_messages and "지연" in arrival_messages[0]:
            arrival_status = "delayed"
        elif not arrival_messages:
            arrival_status = "empty"

        return {
            "dairy_room_count": dairy_room_data.get("dairy_room_count", 0),
            "elevator_count": elevator_data.get("count", 0),
            "arrival_status": arrival_status,
            "arrival_count": arrival_data.get("count", 0)
        }

    return {}

def run_service_by_intent(station_name: str, intent: str):
    # intent별 기존 서비스 실행

    if intent == "dairy_room":
        return get_dairy_room_summary_by_station_name(station_name)

    if intent == "elevator":
        return get_elevator_by_station(station_name)

    if intent == "arrival":
        return get_arrival_by_station(station_name)

    return {}

def make_faq_debug(ai_tip):
    # FAQ 개발용 후보 로그 생성

    if not ai_tip:
        return {
            "faq_candidates": []
        }

    candidates = ai_tip.get("candidates", [])

    if not candidates:
        return {
            "faq_candidates": [
                {
                    "question": ai_tip.get("matched_question"),
                    "category": ai_tip.get("category"),
                    "score": ai_tip.get("score")
                }
            ]
        }

    return {
        "faq_candidates": [
            {
                "question": item.get("matched_question"),
                "category": item.get("category"),
                "score": item.get("score")
            }
            for item in candidates[:3]
        ]
    }

def clean_ai_tip(ai_tip):
    # 사용자 응답용 FAQ 정리

    if not ai_tip:
        return None

    return {
        "title": ai_tip.get("title"),
        "content": ai_tip.get("content"),
        "matched_question": ai_tip.get("matched_question"),
        "category": ai_tip.get("category"),
        "score": ai_tip.get("score"),
        "distance": ai_tip.get("distance"),
        "source": ai_tip.get("source")
    }

def clean_recommendation(recommendation):
    # 사용자 응답용 Action 추천 정리

    if not recommendation:
        return None

    return {
        "priority": recommendation.get("priority"),
        "action": recommendation.get("action"),
        "sub_action": recommendation.get("sub_action"),
        "reason": recommendation.get("reason"),
        "score": recommendation.get("score"),
        "similarity_score": recommendation.get("similarity_score")
    }

def handle_ai_request(station_name: str, message: str):
    # 다중 intent 분류
    multi_result = classify_split_multi_intent(message)

    intents = multi_result["intents"]
    matches = multi_result["matches"]

    # intent가 없을 때
    if not intents:
        return {
            "station_name": station_name,
            "message": message,
            "intent": "unknown",
            "intents": [],
            "matches": [],
            "confidence": "unknown",
            "answer": "요청을 정확히 판단하기 어려워요. 수유실, 엘리베이터, 도착정보 중 필요한 정보를 다시 입력해 주세요.",
            "detail": {},
            "ai_tip": None,
            "debug": {
                "faq_candidates": []
            },
            "recommendation": clean_recommendation(
                get_action_recommendation(message, [], {}, [])
            ),
            "data": {}
        }

    # intent가 1개면 기존 단일 구조 유지
    if len(intents) == 1:
        intent = intents[0]

        data = run_service_by_intent(
            station_name=station_name,
            intent=intent
        )

        answer = make_answer(
            station_name=station_name,
            intent=intent,
            data=data
        )

        detail = make_detail(
            intent=intent,
            data=data
        )

        # 단일 intent 
        raw_ai_tip = get_faq_tip(
            message=message,
            intent=intent
        )

        debug = make_faq_debug(raw_ai_tip)
        ai_tip = clean_ai_tip(raw_ai_tip)
        raw_recommendation = get_action_recommendation(message, intents, detail, matches)
        recommendation = clean_recommendation(raw_recommendation)

        first_match = matches[0]
        confidence = get_confidence(first_match["score"])

        return {
            "station_name": station_name,
            "message": message,
            "intent": intent,
            "intents": intents,
            "matched_text": first_match["matched_text"],
            "score": first_match["score"],
            "distance": first_match["distance"],
            "confidence": confidence,
            "answer": answer,
            "detail": detail,
            "ai_tip": ai_tip,
            "debug": debug,
            "recommendation" : recommendation,
            "data": data
        }

    # intent가 여러 개면 여러 서비스 실행
    data = {}

    for intent in intents:
        data[intent] = run_service_by_intent(
            station_name=station_name,
            intent=intent
        )

    # 다중 intent용 answer 생성
    answer_parts = []

    if "dairy_room" in data:
        answer_parts.append(
            make_dairy_room_answer(
                station_name,
                data["dairy_room"]
            )
        )

    if "elevator" in data:
        answer_parts.append(
            make_elevator_answer(
                station_name,
                data["elevator"]
            )
        )

    if "arrival" in data:
        answer_parts.append(
            make_arrival_answer(
                data["arrival"]
            )
        )

    answer = " ".join(answer_parts)

    # 다중 intent용 detail 생성
    detail = {}

    if "dairy_room" in data:
        detail["dairy_room_count"] = data["dairy_room"].get("dairy_room_count", 0)

    if "elevator" in data:
        detail["elevator_count"] = data["elevator"].get("count", 0)

    if "arrival" in data:
        arrival_data = data["arrival"]
        arrival_messages = arrival_data.get("messages", [])

        arrival_status = "available"

        if arrival_data.get("status") == "delayed":
            arrival_status = "delayed"
        elif not arrival_messages:
            arrival_status = "empty"

        detail["arrival_status"] = arrival_status
        detail["arrival_count"] = arrival_data.get("count", 0)

    # FAQ 미니 RAG 팁 조회
    # 여러 intent일 때는 전체 문장을 기준으로 팁 검색
    raw_ai_tip = get_faq_tip(
        message=message,
        intent="all"
    )

    debug = make_faq_debug(raw_ai_tip)
    ai_tip = clean_ai_tip(raw_ai_tip)
    raw_recommendation = get_action_recommendation(message, intents, detail, matches)
    recommendation = clean_recommendation(raw_recommendation)

    top_score = max(match.get("score", 0) for match in matches)
    confidence = get_confidence(top_score)

    return {
        "station_name": station_name,
        "message": message,
        "intent": "multi",
        "intents": intents,
        "matches": matches,
        "confidence": confidence,
        "answer": answer,
        "detail": detail,
        "ai_tip": ai_tip,
        "debug": debug,
        "recommendation" : recommendation,
        "data": data
    }