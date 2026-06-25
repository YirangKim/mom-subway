# intent_examples.py
# 예시 문장 준비

"""
맘서브웨이 intent 예시 문장 데이터

역할:
- 사용자 자연어 문장을 어떤 기능으로 연결할지 판단하기 위한 기준 문장
- Sentence Transformer로 이 문장들을 벡터화
- ChromaDB에 저장한 뒤 사용자 문장과 유사도 비교
"""

INTENT_EXAMPLES = [
    # 전체 안내
    {
        "text": "수유실 엘리베이터 열차시간 다 알려줘",
        "intent": "all"
    },
    {
        "text": "수유실이랑 엘리베이터랑 도착정보 전부 알려줘",
        "intent": "all"
    },
    {
        "text": "수유실이랑 엘리베이터랑 열차정보 모두 알려줘",
        "intent": "all"
    },
    {
        "text": "아이랑 이동할 때 수유실 엘리베이터 열차시간 전부 알려줘",
        "intent": "all"
    },
    {
        "text": "아기랑 지하철 탈 때 수유실 엘리베이터 도착정보 다 알려줘",
        "intent": "all"
    },
    {
        "text": "유모차로 가는데 수유실 엘리베이터 열차 다 확인해줘",
        "intent": "all"
    },
    # 수유실 안내
    {
        "text": "수유실 알려줘",
        "intent": "dairy_room"
    },
    {
        "text": "수유실 있어?",
        "intent": "dairy_room"
    },
    {
        "text": "아기 수유할 수 있는 공간 알려줘",
        "intent": "dairy_room"
    },
    {
        "text": "기저귀 갈 수 있는 곳 있어?",
        "intent": "dairy_room"
    },
    {
        "text": "기저귀 교환대 있는 곳 알려줘",
        "intent": "dairy_room"
    },
    {
        "text": "유아휴게실 위치 알려줘",
        "intent": "dairy_room"
    },
    {
        "text": "아기랑 있는데 수유실 위치 필요해",
        "intent": "dairy_room"
    },
    {
        "text": "역 안에 아기 돌볼 수 있는 공간 있어?",
        "intent": "dairy_room"
    },
    {
        "text": "수유실 상세정보 보여줘",
        "intent": "dairy_room"
    },
    {
        "text": "아기 기저귀 갈 곳 찾고 있어",
        "intent": "dairy_room"
    },
    {"text": "수유실 정보 알려줘", 
     "intent": "dairy_room"},
    {"text": "수유실 위치 보여줘",
     "intent": "dairy_room"},
    {"text": "수유실 상세정보 보여줘",
      "intent": "dairy_room"},
    {"text": "기저귀 갈 곳 알려줘",
     "intent": "dairy_room"},
    {"text": "이유식 데울 곳 알려줘",
     "intent": "dairy_room"},
    {"text": "분유 먹일 곳 알려줘",
     "intent": "dairy_room"},
    # 엘리베이터 안내
    {
        "text": "엘리베이터 위치 알려줘",
        "intent": "elevator"
    },
    {
        "text": "엘리베이터 어디 있어?",
        "intent": "elevator"
    },
    {
        "text": "유모차라서 엘리베이터 있는 출구 알려줘",
        "intent": "elevator"
    },
    {
        "text": "아이랑 계단 없이 이동하고 싶어",
        "intent": "elevator"
    },
    {
        "text": "휠체어로 이동 가능한 엘리베이터 위치 알려줘",
        "intent": "elevator"
    },
    {
        "text": "역 안에 엘리베이터 있나?",
        "intent": "elevator"
    },
    {
        "text": "유모차 이동 가능한 동선 알려줘",
        "intent": "elevator"
    },
    {
        "text": "엘리베이터 있는 곳으로 나가고 싶어",
        "intent": "elevator"
    },
    {
        "text": "아이 데리고 계단 피해서 이동하려면 어디로 가야 해?",
        "intent": "elevator"
    },
    {
        "text": "엘리베이터 위치 좌표 알려줘",
        "intent": "elevator"
    },
    {"text": "엘리베이터 정보 알려줘", "intent": "elevator"},
    {"text": "엘리베이터 위치 보여줘", "intent": "elevator"},
    {"text": "계단 없는 출구 알려줘", "intent": "elevator"},
    {"text": "유모차로 갈 수 있는 출구 알려줘", "intent": "elevator"},
    {"text": "아기띠 하고 갈 수 있는 길 알려줘", "intent": "elevator"},

    # 도착정보 안내
    {
        "text": "다음 열차 언제 와?",
        "intent": "arrival"
    },
    {
        "text": "도착정보 알려줘",
        "intent": "arrival"
    },
    {
        "text": "열차 도착정보 알려줘",
        "intent": "arrival"
    },
    {
        "text": "지하철 몇 분 뒤 도착해?",
        "intent": "arrival"
    },
    {
        "text": "지하철 도착정보 알려줘",
        "intent": "arrival"
    },
    {
        "text": "다음 전철 언제 와?",
        "intent": "arrival"
    },
    {
        "text": "상행선 언제 도착해?",
        "intent": "arrival"
    },
    {
        "text": "하행선 몇 분 남았어?",
        "intent": "arrival"
    },
    {
        "text": "지금 오는 열차 있어?",
        "intent": "arrival"
    },
    {
        "text": "다음 지하철 도착 시간 알려줘",
        "intent": "arrival"
    },
    {
        "text": "전철 도착정보 확인해줘",
        "intent": "arrival"
    },
    {
        "text": "열차 실시간 도착정보 알려줘",
        "intent": "arrival"
    },
    {"text": "열차 도착시간 알려줘", "intent": "arrival"},
    {"text": "열차 시간 알려줘", "intent": "arrival"},
    {"text": "다음 열차 알려줘", "intent": "arrival"},
    {"text": "지하철 도착정보 알려줘", "intent": "arrival"},
    {"text": "몇 분 뒤에 와", "intent": "arrival"}
]