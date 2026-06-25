# ai/utils/message_splitter.py
# 자연어 전처리

def split_user_message(message: str):
    # 사용자 문장을 요청 단위로 나누기

    text = message.strip()

    # 연결 표현 정리
    text = text.replace("이랑", ",")
    text = text.replace("랑", ",")
    text = text.replace("하고", ",")
    text = text.replace("그리고", ",")
    text = text.replace("또", ",")

    # 쉼표 기준 분리
    parts = text.split(",")

    split_messages = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        # 너무 짧은 요청에도 안내 표현 붙이기
        if "알려줘" not in part and "확인" not in part:
            part = part + " 알려줘"

        split_messages.append(part)

    return split_messages