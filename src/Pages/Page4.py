import re

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page4(BasePage):
    def dividePage(self, pdfData: dict, extractData: dict) -> list:
        result = []
        originSize = len(pdfData['tables'])
        newSize = len(extractData['tables'])

        # 남은 크기
        remainedSize = self.getMaxLength() - originSize

        # 최대 길이를 넘지 않는 선에서 데이터 추가
        if originSize < self.getMaxLength():
            slicedTable = extractData['tables'][0:remainedSize]
            pdfData['tables'].extend(slicedTable)

        # 새로운 데이터가 남아 있을 경우 새로운 페이지로 추가
        if originSize + newSize >= self.getMaxLength():
            slicedTable = extractData['tables'][remainedSize: newSize]
            pdfData['tables'].append(slicedTable)

        return result

    def getMaxLength(self) -> int:
        return 20

    def getKey(self) -> str:
        return "page4"

    def getTemplatePage(self) -> str:
        return "template-04-lapsed-cancelled-contracts.html"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 실효/해지계약현황" in lines[0].strip() if lines else ""

    def extract(self, page, pdfData: dict) -> dict:
        words = self.convertWords(page)
        extractedData = self.buildBaseData2(words, pdfData['page1'])

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table({
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
        })

        tables = []
        if extractTable:
            for row in extractTable:
                cleanRow = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                tables.append(self.buildTable(cleanRow))

        extractedData["tables"] = tables

        # print(extractedData)
        return extractedData

    def buildTable(self, row) -> dict:
        return {
            # 순서
            "index": row[0],
            # 상태
            "status": row[1],
            # 회사명
            "company_name": row[2].replace('*',''),
            # 상품명
            "product_name": row[3],
            # 계약 시작일
            "contract_start_date": row[4],
            # 계약 만료일
            "contract_end_date": self.dateUtil.addYearsToDate(row[4], row[6]),
            # 납입주기
            "payment_cycle": row[5],
            # 납입기간
            "payment_period": row[6],
            # 만기
            "maturity": row[7],
            # 월 보험료
            "monthly_insurance_premium": row[8],
        }
