from typing import Any

import pdfplumber
import pdfkit

# 설치: pip install playwright && playwright install chromium
from playwright.sync_api import sync_playwright
from jinja2 import Environment, FileSystemLoader
from src.Pages.Page1 import Page1
from src.Pages.Page2_2 import Page2_2
from src.Pages.Page3 import Page3
from src.Utils.FileUtil import FileUtil


class PdfUtil:
    def __init__(self):
        super().__init__()
        self.fileUtil = FileUtil()
        self.composites = [
            # Page1(),
            # Page2_2(),
            Page3(),
        ]

    # pdf 에서 데이터를 읽어서 딕셔너리로 반환 합니다
    def convertPdfToData(self, path: str) -> dict[str, Any]:
        pdfData = {}

        # 페이지 데이터 초기화
        for item in self.composites:
            pdfData[item.getKey()] = []

        with pdfplumber.open(path) as pdf:
            for pageNumber, page in enumerate(pdf.pages, start=1):
                for item in self.composites:
                    if item.isCorrect(page):
                        extractData = item.extract(page, pdfData)

                        # 테이블 조합
                        if item.getKey() in ['page1', 'page3']:
                            # 이미 table 데이터가 존재할 경우
                            if 'tables' in pdfData[item.getKey()] and 'tables' in extractData and len(
                                    pdfData[item.getKey()]['tables']) > 0:
                                pdfData[item.getKey()]['tables'].extend(extractData['tables'])
                            else:
                                pdfData[item.getKey()] = extractData
                        elif item.getKey() in ['page2']:
                            # page2 일 경우 페이지 별로 새로운 페이지로 추가
                            pdfData[item.getKey()].append(extractData)

        return pdfData

    # 데이터를 HTML로 변환 합니다
    def convertDataToHtml(self, data: dict[Any, Any]) -> list:
        renderedHtml = []
        for key, value in data.items():
            # value 가 array 인 페이지일 경우
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    renderedHtml.append(self.convertHtmlSource(self.fileUtil.readPdf(item["template"], item)))
            else:
                renderedHtml.append(self.convertHtmlSource(self.fileUtil.readPdf(value["template"], value)))

        ##################################################
        print(renderedHtml)

        # 테스트 용
        # 4. 결과 저장
        with open('result.html', 'w', encoding='utf-8') as f:
            f.write("\n".join(renderedHtml))
        ##################################################

        return renderedHtml

    def convertDataToPythonHtml(self, data: dict[Any, Any]) -> list:
        renderedHtml = []

        # 1. 템플릿 파일들이 들어있는 폴더 경로 지정 (현재 폴더인 경우 '.')
        fileLoader = FileSystemLoader(self.fileUtil.getAbsolutePath(self.fileUtil.getTemplatePath()))
        env = Environment(loader=fileLoader)

        for key, value in data.items():
            # value 가 array 인 페이지일 경우
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    # 2. 사용할 HTML 템플릿 파일 로드
                    template = env.get_template(item["template"])
                    renderedHtml.append(template.render(data=item, stylePrint=self.getStylePrintSource(), styleComponents=self.getStyleComponentSource()))
            else:
                # 2. 사용할 HTML 템플릿 파일 로드
                template = env.get_template(value["template"])
                renderedHtml.append(template.render(data=value, stylePrint=self.getStylePrintSource(), styleComponents=self.getStyleComponentSource()))

        # 테스트 용
        # 4. 결과 저장
        with open('result.html', 'w', encoding='utf-8') as f:
            f.write("\n".join(renderedHtml))
        ##################################################

        return renderedHtml

    # HTML 소스 내의 CSS 링크를 실제 CSS 내용으로 치환 합니다
    def convertHtmlSource(self, html) -> str:
        with open(self.fileUtil.getAbsolutePath(f"{self.fileUtil.getStylePath()}/print.css"), 'r') as f:
            cssPrint = f.read()
        with open(self.fileUtil.getAbsolutePath(f"{self.fileUtil.getStylePath()}/components.css"), 'r') as f:
            cssComponent = f.read()

            # 2. HTML 내의 link 태그를 <style> 태그로 치환
        html = html.replace(
            '<link rel="stylesheet" href="/resources/styles/print.css" />',
            f'<style>{cssPrint}</style>'
        )
        html = html.replace(
            '<link rel="stylesheet" href="/resources/styles/components.css" />',
            f'<style>{cssComponent}</style>'
        )
        return html

    # style print 소스 반환
    def getStylePrintSource(self) -> str:
        return self.getStyleSource('print')
    # style print 소스 반환
    def getStyleComponentSource(self) -> str:
        return self.getStyleSource('components')

    def getStyleSource(self, file) -> str:
        with open(self.fileUtil.getAbsolutePath(f"{self.fileUtil.getStylePath()}/{file}.css"), 'r') as f:
            cssPrint = f.read()
            return f'<style>{cssPrint}</style>'

    # html 을 pdf 로 변환 합니다
    def convertHtmlToPdf(self, html: list, output: str) -> None:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()

            # 1. 각 HTML 조각 사이에 페이지 분할 CSS 삽입하여 합치기
            # page-break-after: always는 인쇄 시 강제로 다음 페이지로 넘깁니다.
            combined_html = ""
            for item in html:
                combined_html += f'<div style="page-break-after: always;">{item}</div>'

            # 2. 합쳐진 전체 내용을 한 번에 주입
            page.set_content(combined_html)

            # 리소스 로드 대기
            page.wait_for_load_state("networkidle")

            # 3. PDF 생성 (하나의 파일에 여러 페이지가 들어감)
            page.pdf(
                path=f"{self.fileUtil.getOutputPath()}/{output}",
                format="A4",
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
            )
            browser.close()
