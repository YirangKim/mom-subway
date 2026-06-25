# 엑셀 전체 데이터를 JSON으로 변환
import os
import json
import pandas as pd


# 현재 파일이 있는 폴더 경로
CURRENT_DIR = os.path.dirname(__file__)


# 엑셀 파일 경로
EXCEL_FILE_PATH = os.path.join(CURRENT_DIR, "station_code.xlsx")


# 읽을 엑셀 탭 이름
SHEET_NAME = "역사고유번호"


# 저장할 JSON 파일 경로
JSON_FILE_PATH = os.path.join(CURRENT_DIR, "station_code_raw.json")


def print_progress(step, total_step, message):
    # 진행률 계산
    percent = int((step / total_step) * 100)

    # 진행률 출력
    print(f"[{percent}%] {message}")


def convert_excel_to_raw_json():
    # 전체 단계 수
    total_step = 5

    # 시작 로그
    print_progress(0, total_step, "JSON 변환 시작")

    # 엑셀 탭 읽기
    print_progress(1, total_step, "엑셀 파일 읽는 중")
    df = pd.read_excel(
        EXCEL_FILE_PATH,
        sheet_name=SHEET_NAME
    )

    # 컬럼명 정리
    print_progress(2, total_step, "컬럼명 정리 중")
    df.columns = df.columns.str.strip()

    # 빈 값 정리
    print_progress(3, total_step, "빈 값 정리 중")
    df = df.where(pd.notnull(df), None)

    # 전체 행 변환
    print_progress(4, total_step, "엑셀 데이터를 JSON 형태로 변환 중")
    raw_data = df.to_dict(orient="records")

    # JSON 저장
    print_progress(5, total_step, "JSON 파일 저장 중")
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(
            raw_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    # 변환 결과 확인
    print("====================================")
    print("JSON 변환 완료")
    print(f"저장 위치: {JSON_FILE_PATH}")
    print(f"전체 행 개수: {len(raw_data)}개")
    print("컬럼 목록:")
    print(list(df.columns))
    print("====================================")


# 직접 실행
if __name__ == "__main__":
    convert_excel_to_raw_json()