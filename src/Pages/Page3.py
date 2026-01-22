import re

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page3(BasePage):

    def getMaxLength(self) -> int:
        return 37

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
            currentGruop = {}
            currentSubGruop = {}
            previousGroup = ""
            previousSubGroup = ""
            for row in extractTable:
                # row는 ['1', 'ABL생명', '무)급여실손...', '2023-10-31', ...] 형태의 리스트입니다.
                # None 데이터 제거 및 줄바꿈(\n) 처리
                cleanRow = [str(cell).replace('\n', '') if cell else "" for cell in row]

                if cleanRow[0] == "" and cleanRow[1] == "" and cleanRow[2] == "":
                    continue

                # 그룹이 있을 경우 초기화
                if cleanRow[0] != "":
                    previousGroup = cleanRow[0]
                    currentGruop = self.buildTableGroup(previousGroup, [])

                # 서브그룹이 있을 경우 초기화
                if cleanRow[1] != "":
                    previousSubGroup = cleanRow[1]
                    currentGruop['totalSubRowCount'] += 1
                    currentSubGruop = self.buildTableSubGroup(previousSubGroup, [self.buildTable(cleanRow)])

                # 서브그룹의 아이템 추가
                if cleanRow[0] == "" and cleanRow[1] == "":
                    currentGruop['totalSubRowCount'] += 1
                    currentSubGruop['items'].append(self.buildTable(cleanRow))

                # 이전 서브그룹 데이터가 있을 경우 추가
                if cleanRow[1] != "":
                    currentGruop['items'].append(currentSubGruop)

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
            r'\s*([\d,]+(?:만|억)?|0)\s*'        # 금액 (100만, 1,500만, 1억, 0)
            r'(\d{4}-\d{1,2}-\d{1,2})\s*'        # 시작일 (잘린 날짜 포함)
            r'(\d{4}-\d{2}-\d{2})'               # 종료일
        )

        result = re.match(pattern, combined)
        # print(f"combined : {combined}")
        # print(f"result : {result}")

        return {
            # 상품명
            "product_name": row[2],
            # 회사담보명
            "company_collateral": row[3],
            # 가입 금액
            "subscription_amount": result[1],
            # 보험시기
            "insurance_period": result[2],
            # 보험종기
            "insurance_term": result[3],
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
