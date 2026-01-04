import pdfplumber
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import io
import os

#  텍스트 추출
def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text


#  텍스트 추출
def parse_a_pdf(text):
    data = {}

    data["name"] = re.search(r"(김정화)", text).group(1)
    data["age"] = re.search(r"\((\d+)세", text).group(1)
    data["datetime"] = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text).group()

    def find_amount(label):
        m = re.search(label + r"\d[\d,]*억\s?\d[\d,]*만|\d[\d,]*억|\d[\d,]*만|-", text)
        return m.group(1) if m else "-"

    data["상해사망"] = find_amount("상해사망")
    data["질병사망"] = find_amount("질병사망")
    data["장기요양간병비"] = find_amount("장기요양간병비")
    data["경증치매진단"] = find_amount("경증치매진단")
    data["간병인/간호간병상해일당"] = find_amount("간병인/간호간병상해일당")
    data["간병인/간호간병질병일당"] = find_amount("간병인/간호간병질병일당")
    data["일반암"] = find_amount("일반암")
    data["유사암"] = find_amount("유사암")
    data["고액암"]= find_amount("고액암")
    data["고액(표적)항암치료비"] = find_amount("고액(표적)항암치료비")
    data["뇌혈관질환"] = find_amount("뇌혈관질환")
    data["뇌졸중"] = find_amount("뇌졸중")
    data["급성심근경색"] = find_amount("급성심근경색증")

    return data

a_text = extract_text_from_pdf("a.pdf")
print(a_text)
parsed_data = parse_a_pdf(a_text)
print(parsed_data)
# create_b_pdf(parsed_data, "b_output.pdf")

col1 = 180
row_start = 620
row_size = 15

FIELDS = [
    "상해사망",
    "질병사망",
    "1",
    "2",
    "장기요양간병비"
    "경증치매진단"
    "간병인/간호간병상해일당"
    "간병인/간호간병질병일당"
    "일반암",
    "유사암",
    "고액암",
    "고액(표적)항암치료비",
    "뇌혈관질환",
    "뇌졸중",
    "급성심근경색",
]

FIELD_POS = {
    "name": (120, 790),
    "age": (200, 790),
    "datetime": (380, 770),
}

for i, field in enumerate(FIELDS):
    FIELD_POS[field] = (col1, row_start - (row_size * i))

#  b.pdf 위에 값 입히기
def fill_b_pdf(template_path, output_path, data):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 10)

    # 좌표에 값 쓰기
    for key, (x, y) in FIELD_POS.items():
        can.drawString(x, y, str(data.get(key, "")))

    can.save()
    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    template_pdf = PdfReader(template_path)

    writer = PdfWriter()

    for i in range(len(template_pdf.pages)):
        base_page = template_pdf.pages[i]
        if i == 0:
            base_page.merge_page(overlay_pdf.pages[0])
        writer.add_page(base_page)

    with open(output_path, "wb") as f:
        writer.write(f)

def delete_if_exists(filename):
    """
    지정된 파일이 현재 경로에 존재하는지 확인하고 제거합니다.
    """
    # 파일명
    file_to_check = filename

    # os.path.exists()를 사용하여 파일 존재 여부 확인
    if os.path.exists(file_to_check):
        try:
            # 파일 제거 (삭제)
            os.remove(file_to_check)
            print(f"✅ '{file_to_check}' 파일이 존재하여 성공적으로 제거되었습니다.")
        except OSError as e:
            # 파일이 존재하지만, 권한 문제 등으로 삭제에 실패한 경우
            print(f"❌ '{file_to_check}' 파일 삭제 중 오류 발생: {e}")
    else:
        print(f"ℹ️ '{file_to_check}' 파일이 존재하지 않습니다. 제거 작업이 필요하지 않습니다.")

# 실행: 'b_filled.pdf' 파일에 대해 함수 호출
if __name__ == "__main__":
    delete_if_exists("b_filled.pdf")

fill_b_pdf(
    template_path="b_removed.pdf",
    output_path="b_filled.pdf",
    data=parsed_data
)

print("b_filled.pdf 생성 완료")