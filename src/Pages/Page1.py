from .BasePage import BasePage


class Page1(BasePage):
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
            result.append(pdfData)

        # 새로운 데이터가 남아 있을 경우 새로운 페이지로 추가
        if originSize + newSize >= self.getMaxLength():
            slicedTable = extractData['tables'][remainedSize: newSize]

            cloneExtractData = extractData.copy()
            cloneExtractData['tables'] = slicedTable
            result.append(cloneExtractData)

        return result

    def getMaxLength(self) -> int:
        return 20

    def getKey(self) -> str:
        return "page1"

    def getTemplatePage(self) -> str:
        return "template-01-contract-overview.html"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 전체 계약리스트" in lines[0].strip() if lines else ""

    def extract(self, page, pdfData: dict) -> dict:
        words = self.convertWords(page)
        # self.printWords(words)

        # 표 추출 (이미지 속 표 구조를 감지)
        extractTable = page.extract_table()

        tables = []
        if extractTable:
            for row in extractTable:
                # row는 ['1', 'ABL생명', '무)급여실손...', '2023-10-31', ...] 형태의 리스트입니다.
                # None 데이터 제거 및 줄바꿈(\n) 처리
                cleanRow = [str(cell).replace('\n', '') if cell else "" for cell in row]
                tables.append(self.appendTable(cleanRow))

        extractedData = self.buildBaseData(words)
        self.printWords(words)
        print(extractedData)

        extractedData["tables"] = tables
        # print(extractedData)
        return extractedData

    def appendTable(self, row) -> dict:
        return {
            # 회사명
            "company_name": row[1],
            # 상품명
            "product_name": row[2],
            # 계약 시작일
            "contract_start_date": row[3],
            # 계약 만료일
            "contract_end_date": self.dateUtil.addYearsToDate(row[3], row[5]) if row[4] != "" else '',
            # 납입 주기
            "payment_cycle": row[4],
            # 납입 기간
            "payment_term": row[5],
            # 만기
            "maturity": row[6],
            # 월 보험료
            "monthly_premium": row[7],
        }
