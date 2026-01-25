import re

import copy

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page3(BasePage):

    def dividePage(self, pdfData: dict, extractData: dict) -> list:
        tables = []
        tables.extend(pdfData['tables'])
        tables.extend(extractData['tables'])

        result = []
        dividedTables = self.appendRemainedTable(tables)
        for dividedTable in reversed(dividedTables):
            cloneExtractData = extractData.copy()
            cloneExtractData['tables'] = dividedTable
            result.append(cloneExtractData)
        return result

    def appendRemainedTable(self, remainedTables: dict) -> list:
        result = []
        slicedTable = []
        index = 0
        subGroupLength = 0
        for group in remainedTables:
            if subGroupLength <= self.getMaxLength():
                subGroupLength += group['totalSubRowCount']
                slicedTable.append(group)
            else:
                result.extend(self.appendRemainedTable(remainedTables[index:len(remainedTables)]))
                break
            index += 1
        result.append(slicedTable)
        return result

    def getMaxLength(self) -> int:
        return 40

    def getKey(self) -> str:
        return "page3"

    def getTemplatePage(self) -> str:
        return "template-03-guarantee-details.html"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 담보별 가입 현황" in lines[0].strip() if lines else ""

    def extract(self, page, pdfData: dict) -> dict:
        extractedData = {
            "template": self.getTemplatePage(),
        }

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table({
            "vertical_strategy": "lines",  # 선이 없어도 텍스트 정렬을 보고 열을 나눔
            "horizontal_strategy": "lines",  # 가로 실선을 기준으로 행을 나눔
        })
        tables = []
        if extractTable:
            previousGroup = ""
            previousSubGroup = ""
            currentGruop = self.buildTableGroup(previousGroup, [])
            currentSubGroup = {}
            for row in extractTable:
                # row는 ['1', 'ABL생명', '무)급여실손...', '2023-10-31', ...] 형태의 리스트입니다.
                # None 데이터 제거 및 줄바꿈(\n) 처리
                cleanRow = [str(cell).replace('\n', '') if cell else "" for cell in row]
                # print(f"cleanRow : {cleanRow}")

                if cleanRow[0] == "" and cleanRow[1] == "" and cleanRow[2] == "":
                    continue

                # 그룹이 있을 경우 초기화
                if cleanRow[0] != "":
                    previousGroup = cleanRow[0]
                    currentGruop = self.buildTableGroup(previousGroup, [])

                # 서브그룹이 있을 경우 초기화
                if cleanRow[1] != "":
                    previousSubGroup = cleanRow[1]
                    # print(f"currentGruop : {currentGruop}")
                    currentGruop['totalSubRowCount'] += 1
                    currentSubGroup = self.buildTableSubGroup(previousSubGroup, [self.buildTable(cleanRow)])

                # 서브그룹의 아이템 추가
                if cleanRow[0] == "" and cleanRow[1] == "":
                    currentGruop['totalSubRowCount'] += 1

                    # 페이지 이동으로 인해 데이터가 없는 경우 마지막 데이터 사용
                    if 'items' not in currentSubGroup:
                        pdfData[self.getKey()]['tables'][-1]['items'][-1]['items'].append(self.buildTable(cleanRow))
                        pdfData[self.getKey()]['tables'][-1]['totalSubRowCount'] += 1
                    else:
                        currentSubGroup['items'].append(self.buildTable(cleanRow))

                # 이전 서브그룹 데이터가 있을 경우 추가
                if cleanRow[1] != "":
                    currentGruop['items'].append(currentSubGroup)

                # 이전 그룹 데이터가 있을 경우 추가
                if cleanRow[0] != "":
                    tables.append(currentGruop)

        extractedData["tables"] = tables

        # print(extractedData)
        return extractedData

    def buildTable(self, row) -> dict:
        data = row[4:7]
        combined = "".join(data).replace(" ", "")
        # 정규식 적용 (금액 덩어리와 날짜 덩어리를 추출)
        pattern = re.compile(
            r'([\d,]+(?:만|억)?|0)\D*?(\d{4}-\d{1,2}-\d{1,2})\D*?(\d{4}-\d{2}-\d{2})'
        )
        # combined는 기존처럼 row[4:7]을 합친 문자열
        result = re.search(pattern, combined)

        # print(f"row : {row}")
        # print(f"combined : {combined}")

        return {
            # 상품명
            "product_name": row[2],
            # 회사담보명
            "company_collateral": row[3],
            # 가입 금액
            "subscription_amount": result.group(1) if result and result.group(1) else "",
            # 보험시기
            "insurance_period": result.group(2) if result and result.group(2) else "",
            # 보험종기
            "insurance_term": result.group(3) if result and result.group(3) else "",
        }

    def buildTableGroup(self, group: str, items: list) -> dict:
        return {
            "groupName": group,
            "totalSubRowCount": 0,
            "items": items
        }

    def buildTableSubGroup(self, group: str, items: list) -> dict:
        return {
            "subGroupName": group,
            "items": items
        }
