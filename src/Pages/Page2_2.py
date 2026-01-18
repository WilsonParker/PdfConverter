import re
from typing import Any

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page2_2(BasePage):

    def getKey(self) -> str:
        return "page2"

    def getTemplatePage(self) -> str:
        return "template-02-guarantee-overview.html"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 상품별 가입현황" in lines[0].strip() if lines else ""

    def extract(self, page, pdfData: dict) -> dict:
        words = self.convertWords(page)
        # self.printWords(words)

        extractedData = self.buildBaseData2(words, pdfData['page1'])
        headerTables = []

        text = page.extract_text()
        headerTableNumbres = self.getHeaderTableNumbers(text)
        paymentMaturityStr = self.extractPaymentMaturityStr(text)
        paymentMaturityDate = self.extractPaymentMaturityDate(text)

        for n, number in enumerate(headerTableNumbres):
            for i, table in enumerate(pdfData['page1']['tables']):
                index = int(number.replace("(", "").replace(")", "")) - 1
                if i != index:
                    continue
                # 2년납/55세 만기
                table['payment_maturity_str'] = paymentMaturityStr[n]
                # 2023.10.31~2055.10.30
                table['payment_maturity_date'] = paymentMaturityDate[n]
                headerTables.append(table)

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table({
            "vertical_strategy": "text",  # 선이 없어도 텍스트 정렬을 보고 열을 나눔
            "horizontal_strategy": "lines",  # 가로 실선을 기준으로 행을 나눔
            "snap_tolerance": 3,
            "text_x_tolerance": 3,
        })

        tables = []
        if extractTable:
            items = []
            previousGroup = ""
            for row in extractTable:
                # row는 ['1', 'ABL생명', '무)급여실손...', '2023-10-31', ...] 형태의 리스트입니다.
                # None 데이터 제거 및 줄바꿈(\n) 처리
                cleanRow = [str(cell).replace('\n', ' ') if cell else "" for cell in row]

                # 이전 데이터가 있을 경우 추가
                if cleanRow[0] != "" and len(items) > 0:
                    tables.append(self.buildTableGroup(previousGroup, items))

                # 그룹이 있을 경우 초기화
                if cleanRow[0] != "":
                    items = []
                    previousGroup = cleanRow[0]

                items.append(self.buildTable(cleanRow))

        tables.append(self.buildTableGroup(previousGroup, items))

        extractedData["headerTables"] = headerTables
        extractedData["tables"] = tables
        # print(extractedData)
        return extractedData

    def buildTable(self, row) -> dict:
        return {
            "name": row[1],
            "total": row[2],
            "items": [
                row[3],
                row[4],
                row[5],
                # index 6 이 없을 경우
                row[6] if len(row) > 6 else "",
            ]
        }

    def buildTableGroup(self, group: str, items: list) -> dict:
        return {
            "groupName": group,
            "items": items
        }

    def extractPaymentMaturityStr(self, text: str) -> list[Any]:
        # 정규식 패턴: 숫자+년납/숫자+세 만기
        pattern = r'\d+년납/\d+세\s?만기'

        # 모든 매칭 결과 찾기
        return re.findall(pattern, text)

    def extractPaymentMaturityDate(self, text: str) -> list[Any]:
        # 날짜 패턴: 숫자.숫자.숫자~숫자.숫자.숫자
        pattern = r'\d{4}\.\d{2}\.\d{2}~\d{4}\.\d{2}\.\d{2}'

        # 모든 매칭 결과 찾기
        return re.findall(pattern, text)

    # 헤더 테이블 번호 추출
    def getHeaderTableNumbers(self, text: str) -> list[Any]:
        # 정규식 설명: \( (괄호 시작) \d+ (숫자 한 개 이상) \) (괄호 끝)
        pattern = r'\(\d+\)'
        return re.findall(pattern, text)

    # 헤더 테이블 수 계산
    def getHeaderTableCount(self, words: list) -> int:
        count = 1
        for i in range(0, len(words)):
            if re.match(r'^\d+$', words[i]):
                count += 1
        return count
