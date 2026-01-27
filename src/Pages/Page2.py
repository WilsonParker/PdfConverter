import re
from typing import Any

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page2(BasePage):

    def dividePage(self, pdfData: dict, extractData: dict) -> list:
        pass

    def getMaxLength(self) -> int:
        return 0

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

        if isinstance(pdfData['page1'], list):
            page1Data = pdfData['page1'][0]
            page1DataTables = []
            for data in pdfData['page1']:
                page1DataTables.extend(data['tables'])
        else:
            page1Data = pdfData['page1']
            page1DataTables = pdfData['page1']['tables']

        extractedData = self.buildBaseData2(words, page1Data)
        headerTables = []

        text = page.extract_text()
        totalCount = len(page1DataTables)
        headerTableNumbres = self.getHeaderTableNumbers(text)
        paymentMaturityStr = self.extractPaymentMaturityStr(text)
        paymentMaturityDate = self.extractPaymentMaturityDate(text)

        for n, number in enumerate(headerTableNumbres):
            for i, table in enumerate(page1DataTables):
                index = int(number.replace("(", "").replace(")", "")) - 1
                if i != index:
                    continue
                # (1) 삼성생명
                table['company_name'] = f"{number} {table['company_name']}"
                # 2년납/55세 만기
                table['payment_maturity_str'] = paymentMaturityStr[n]
                # 2023.10.31~2055.10.30
                table['payment_maturity_date'] = paymentMaturityDate[n]
                headerTables.append(table)

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table({
            "vertical_strategy": "lines",  # 우선 실선이 있는지 확인
            "horizontal_strategy": "lines",
            # 만약 실선이 없다면 아래 explicit_vertical_lines를 활성화하세요.
            # "vertical_strategy": "explicit",
            # "explicit_vertical_lines": [좌표값들...],

            "snap_tolerance": 3,
            "text_x_tolerance": 2,
            "text_y_tolerance": 3,  # 행 높이 인식을 더 정교하게 함
            "intersection_y_tolerance": 10,
        })

        extractLines = page.extract_text().splitlines()

        for i, line in enumerate(extractLines):
            if "상해사망" in line:
                startLineIndex = i
                break

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
                # print(cleanRow)
                items.append(self.buildTable(cleanRow, extractLines[startLineIndex], headerTableNumbres, totalCount))
                startLineIndex = self.nextLineIndex(extractLines, startLineIndex)

        tables.append(self.buildTableGroup(previousGroup, items))

        extractedData["headerTables"] = headerTables
        extractedData["tables"] = tables
        # print(extractedData)
        return extractedData

    def nextLineIndex(self, extractLines: list, currentIndex: int) -> int:
        nextIndex = currentIndex + 1
        pattern = re.compile(r'[\d,]+(?:만|억)|\b0\b|-')
        while nextIndex < len(extractLines):
            line = extractLines[nextIndex].strip()
            if bool(pattern.search(line)):
                break
            else:
                nextIndex += 1
        return nextIndex

    def buildTable(self, row, line: str, headerTableNumbres, totalCount: int) -> dict:
        # extractTable 에서 index 6 이 없을 경우가 있음
        if len(row) > 6:
            lastValue = row[6]
        else:
            pattern = r"([\d,]+억(?:\s*[\d,]+만)?|[\d,]+만)|(-)"

            # 추출 후 빈 값을 제외하고 리스트화
            result = [m[0] or m[1] for m in re.findall(pattern, line)]

            # headerTableNumbres에서 totalCount보다 작거나 같은 숫자의 개수를 셉니다.
            count = sum(1 for num_str in headerTableNumbres if int(num_str.strip('()')) <= totalCount)

            # 빈 컬럼이 있는지 확인
            hasEmptyColumn = count > 0 and len(result) < 5

            if hasEmptyColumn:
                lastValue = ""
            else:
                lastValue = result[4]

        return {
            "name": row[1],
            "total": row[2],
            "items": [
                row[3],
                row[4],
                row[5],
                # index 6 이 없을 경우
                lastValue,
            ]
        }

    def buildTableGroup(self, group: str, items: list) -> dict:
        return {
            "groupName": group,
            "items": items
        }

    def extractPaymentMaturityStr(self, text: str) -> list[Any]:
        # 정규식 패턴: 숫자+년납/숫자+세 만기
        pattern = re.compile(r'(?:\d+년납/)?\d+세\s*만기')

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
