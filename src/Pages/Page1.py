from .BasePage import BasePage


class Page1(BasePage):
    def getKey(self) -> str:
        return "page1"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 전체 계약리스트" in lines[0].strip() if lines else ""

    def extract(self, page) -> dict:
        print("*** is page 1 ***")
        # 각 딕셔너리에서 'text' 값만 추출하여 새로운 리스트 생성
        words = self.convertWords(page)

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table()

        tables = []
        if extractTable:
            for row in extractTable:
                # row는 ['1', 'ABL생명', '무)급여실손...', '2023-10-31', ...] 형태의 리스트입니다.
                # None 데이터 제거 및 줄바꿈(\n) 처리
                cleanRow = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                tables.append(self.appendTable(cleanRow))

        extractedData = self.baseDataPage1And2(words)

        # 보험 계약 수
        extractedData['numberOfInsuranceContracts'] = words[11]
        # 월 보험료 합계
        extractedData['totalMonthlyPremium'] = words[12]

        extractedData["tables"] = tables
        # print(extractedData)
        return extractedData

    def appendTable(self, row) -> dict:
        return {
            # 회사명
            "companyName": row[1],
            # 상품명
            "productName": row[2],
            # 계약일
            "contractDate": row[3],
            # 납입 주기
            "paymentCycle": row[4],
            # 납입 기간
            "paymentPeriod": row[5],
            # 만기
            "maturity": row[6],
            # 월 보험료
            "monthlyPremium": row[7],
        }
