import pathlib
import re
from collections import defaultdict

import pdfplumber


# 최종적으로 추출된 데이터를 저장할 딕셔너리
insurance_data = {
    "member": {},
    "info": {},
    "계약 현황": {},
    "전체 보장 현황": defaultdict(lambda: {"KB손해보험": "-", "손해보험": "-", "생명보험": "-", "공제/제산": "-"}),
}

# ----------------- 설정 -----------------
# PDF 파일들이 들어있는 폴더 경로를 지정합니다
# ex) ./input
def get_paths(path):
    folder_path = pathlib.Path(path)

    # 1. 폴더가 실제로 존재하는지 확인
    if not folder_path.exists():
        print(f"오류: 지정된 폴더 '{folder_path}'를 찾을 수 없습니다.")
    else:
        # print(f"--- 폴더 '{folder_path.name}'의 PDF 파일 목록 ---")

        # 2. glob() 메서드를 사용하여 *.pdf 패턴에 일치하는 모든 파일을 찾습니다.
        # rglob()을 사용하면 하위 폴더까지 탐색할 수 있습니다.
        pdf_files = list(folder_path.glob("*.pdf"))

        if not pdf_files:
            print("이 폴더에서 PDF 파일을 찾을 수 없습니다.")
        else:
            return pdf_files


def read_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.page_number == 1:
                    extract_p1_data(page)
            return insurance_data
    except FileNotFoundError:
        print(f"오류: '{pdf_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")


# 1page 데이터 추출
def extract_p1_data(page):
    full_text = page.extract_text()
    # '\n' 기준으로 나누면, '\r'이 남게 됩니다.
    lines_split_n = full_text.split('\n')

    print(lines_split_n)

    # 이름 추출
    match_name = re.search(r"([가-힣]{2,4})\s*님", lines_split_n[0])
    if match_name:
        insurance_data["member"]["name"] = match_name.group(1)
    print(match_name.group(1))

    # 나이, 성별 추출
    match_age_gender = re.search(r"\(([^)]+)\)", lines_split_n[1])
    if match_age_gender:
        age_gender_str = match_age_gender.group(1) # '53세 ,여자'

        # 나이 추출: 숫자 + '세'
        match_age = re.search(r"(\d+세)", age_gender_str)
        if match_age:
            insurance_data['member']['age'] = match_age.group(1)

        # 성별 추출: '남자' 또는 '여자'
        match_gender = re.search(r"(남자|여자)", age_gender_str)
        if match_gender:
            insurance_data['member']['gender'] = match_gender.group(1)

    # 날짜 추출
    match_date = re.search(r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})", lines_split_n[0])
    if match_date:
        insurance_data["info"]["date"] = match_date.group(1)





    # 예시: 월 보험료 추출
    match_premium = re.search(r'월 보험료\s+(\d{1,3}(?:,\d{3})*)', full_text)
    if match_premium:
        insurance_data["계약 현황"]["월 보험료"] = match_premium.group(1).replace(',', '') + "원"

    # 예시: 계약 건수 (정상계약 10건) 추출
    match_count = re.search(r'정상계약\s+(\d+)', full_text)
    if match_count:
        insurance_data["계약 현황"]["정상 계약 건수"] = match_count.group(1) + "건"

    # 테이블 추출: 결과는 리스트의 리스트 형태입니다.
    tables = page.extract_tables()

    # '전체 보장 현황' 테이블을 찾아서 처리
    # 테이블의 첫 번째 셀이 '담보명'인 표를 찾습니다.
    for table in tables:
        # print(table)
        break
