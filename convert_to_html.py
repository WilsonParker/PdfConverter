import pdfplumber

from src.Pages.Page2 import Page2
from src.Pages.Page1 import Page1
from src.Utils.FileUtil import FileUtil

fileUtil = FileUtil()

composites = [
    # Page1(),
    Page2(),
]

result = {
}

# 데이터 초기화
for item in composites:
    result[item.getKey()] = []

print(fileUtil.getPaths("./input"))

try:
    for pdfPath in fileUtil.getPaths("./input"):
        print(pdfPath)
        with pdfplumber.open(pdfPath) as pdf:
            for pageNumber, page in enumerate(pdf.pages, start=1):
                for item in composites:
                    if item.isCorrect(page):
                        result[item.getKey()].append(item.extract(page))
            break
        break
except FileNotFoundError:
    raise RuntimeError(f"오류: '{pdfPath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    raise RuntimeError(f"PDF 처리 중 오류 발생: {e}")

print(result)
