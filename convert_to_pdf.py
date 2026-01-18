import json
import pdfplumber

from src.Pages.Page2 import Page2
from src.Pages.Page1 import Page1
from src.Utils.FileUtil import FileUtil
from jinja2 import Template

fileUtil = FileUtil()

composites = [
    Page1(),
    # Page2(),
]

resultData = {
}

# 데이터 초기화
for item in composites:
    resultData[item.getKey()] = []

print(fileUtil.getPaths("./input"))

try:
    for pdfPath in fileUtil.getPaths("./input"):
        print(pdfPath)
        with pdfplumber.open(pdfPath) as pdf:
            for pageNumber, page in enumerate(pdf.pages, start=1):
                for item in composites:
                    if item.isCorrect(page):
                        # 이미 데이터가 존재할 경우
                        if len(resultData[item.getKey()]) > 0:
                            resultData[item.getKey()]['tables'].append(item.extract(page)['tables'])
                        else:
                            resultData[item.getKey()] = item.extract(page)
            break
        break
except FileNotFoundError:
    raise RuntimeError(f"오류: '{pdfPath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    raise RuntimeError(f"PDF 처리 중 오류 발생: {e}")

# print(resultData)

for key, value in resultData.items():
    print(value)

    # 2. HTML 템플릿 파일 읽기 (제공해주신 HTML 내용을 template_str에 넣거나 파일에서 읽음)
    with open(f"resources/templates/{value["template"]}", 'r', encoding='utf-8') as f:
        template_str = f.read()

    # 3. Jinja2를 사용하여 데이터 주입
    # json.dumps를 사용해 파이썬 리스트를 JS 배열 문자열로 변환합니다.
    template = Template(template_str)
    rendered_html = template.render(json_data=json.dumps(value, ensure_ascii=False))

    # 4. 결과 저장
    with open('result.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)
