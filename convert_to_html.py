import pdfplumber

from src.Pages.Page1 import Page1
from src.Pages.Page2 import Page2
from src.Utils.PdfUtil import PdfUtil

pdfUtil = PdfUtil()

composites = [
    Page1(),
    Page2(),
]

print(pdfUtil.getPaths("./input"))

for pdfPath in pdfUtil.getPaths("./input"):
    try:
        with pdfplumber.open(pdfPath) as pdf:
            for item in composites:
                if item.isCorrect(pdf):
                    item.extract(pdf)
            break
    except FileNotFoundError:
        print(f"오류: '{pdfPath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")