import json
from typing import Any

import pdfplumber
from jinja2 import Template
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from src.Pages.Page1 import Page1
from src.Utils.FileUtil import FileUtil


class PdfUtil:
    def __init__(self):
        super().__init__()
        self.fileUtil = FileUtil()
        self.composites = [
            Page1(),
            # Page2(),
        ]

    # pdf 에서 데이터를 읽어서 딕셔너리로 반환 합니다
    def convertPdfToData(self) -> dict[str, Any]:
        resultData = {}

        # 경로 데이터 초기화
        for item in self.composites:
            resultData[item.getKey()] = []

        try:
            for pdfPath in self.fileUtil.getPaths(self.fileUtil.getInputPath()):
                print(pdfPath)
                with pdfplumber.open(pdfPath) as pdf:
                    for pageNumber, page in enumerate(pdf.pages, start=1):
                        for item in self.composites:
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

        print(resultData)
        return resultData

    # 데이터를 HTML로 변환 합니다
    def convertDataToHtml(self, data: dict[Any, Any]) -> str:
        renderedHtml = ""
        for key, value in data.items():
            # 2. HTML 템플릿 파일 읽기 (제공해주신 HTML 내용을 template_str에 넣거나 파일에서 읽음)
            with open(f"{self.fileUtil.getTemplatePath()}/{value["template"]}", 'r', encoding='utf-8') as f:
                template_str = f.read()

            # 3. Jinja2를 사용하여 데이터 주입
            # json.dumps를 사용해 파이썬 리스트를 JS 배열 문자열로 변환합니다.
            template = Template(template_str)
            renderedHtml += template.render(json_data=json.dumps(value, ensure_ascii=False))

            # 4. 결과 저장
            with open('result.html', 'w', encoding='utf-8') as f:
                f.write(renderedHtml)

        return renderedHtml

    # string html 을 pdf 로 변환 합니다
    async def convertStrHtmlToPdfAwait(self, html: str) -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html)

            # 핵심: 네트워크와 리소스가 완전히 로드될 때까지 대기
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")

            # PDF 생성
            await page.pdf(path=f"{self.fileUtil.getOutputPath()}/output.pdf", format="A4", print_background=True)
            await browser.close()

    def convertStrHtmlToPdf(self, html):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # 로컬 파일 접근 권한을 허용하여 CSS를 읽어오도록 설정
            context = browser.new_context(bypass_csp=True)
            page = context.new_page()

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

            # HTML 문자열 주입
            page.set_content(html)

            # 핵심: 네트워크와 리소스가 완전히 로드될 때까지 대기
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")

            # PDF 생성 옵션
            page.pdf(
                path=f"{self.fileUtil.getOutputPath()}/output.pdf",
                format="A4",
                print_background=True,  # 배경색/이미지 포함 (매우 중요)
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"}
            )
            browser.close()