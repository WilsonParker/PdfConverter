from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page2(BasePage):

    def getKey(self) -> str:
        return "page2"

    def getTemplatePage(self) -> str:
        return "template-02-guarantee-overview.html"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 전체 보장현황" in lines[0].strip() if lines else ""

    def extract(self, page, pdfData: dict) -> dict:
        words = self.convertWords(page)
        # self.printWords(words)

        extractedData = self.buildBaseData(words)
        table = []

        # 유형 1의 페이지일 경우
        if "상해사망" in words[17]:
            table.append(self.bulidTableGroup("사망장해", [
                self.buildTableUsingWord(words, 17),
                self.buildTableUsingWord(words, 23),
                self.buildTableUsingWord(words, 31),
                self.buildTableUsingWord(words, 37),
            ]))

            table.append(self.bulidTableGroup("치매간병", [
                self.buildTableUsingWord(words, 43),
                self.buildTableUsingWord(words, 49),
                self.buildTableUsingWord(words, 57),
                self.buildTableUsingWord(words, 63),
            ]))

            table.append(self.bulidTableGroup("암 진단", [
                self.buildTableUsingWord(words, 69),
                self.buildTableUsingWord(words, 75),
                self.buildTableUsingWord(words, 83),
                self.buildTableUsingWord(words, 89),
            ]))

            table.append(self.bulidTableGroup("뇌/심장 진단", [
                self.buildTableUsingWord(words, 95),
                self.buildTableUsingWord(words, 101),
                self.buildTableUsingWord(words, 108),
                self.buildTableUsingWord(words, 115),
                self.buildTableUsingWord(words, 121),
            ]))

        # 유형 2의 페이지일 경우
        if "상해입원의료비" in words[17]:
            table.append(self.bulidTableGroup("실손의료비", [
                self.buildTableUsingWord(words, 17),
                self.buildTableUsingWord(words, 23),
                self.buildTableUsingWord(words, 30),
                self.buildTableUsingWord(words, 37),
                self.buildTableUsingWord(words, 43),
            ]))

            table.append(self.bulidTableGroup("수술입원", [
                self.buildTableUsingWord(words, 49),
                self.buildTableUsingWord(words, 55),
                self.buildTableUsingWord(words, 61),
                self.buildTableUsingWord(words, 68),
                self.buildTableUsingWord(words, 75),
                self.buildTableUsingWord(words, 81),
                self.buildTableUsingWord(words, 87),
            ]))

            table.append(self.bulidTableGroup("운전자 기타", [
                self.buildTableUsingWord(words, 93),
                self.buildTableUsingWord(words, 99),
                self.buildTableUsingWord(words, 105),
                self.buildTableUsingWord(words, 111),
                self.buildTableUsingWord(words, 119),
                self.buildTableUsingWord(words, 125),
                self.buildTableUsingWord(words, 131),
                self.buildTableUsingWord(words, 137),
            ]))

        extractedData["tables"] = table
        # print(extractedData)
        return extractedData

    # 전체 보장 현황 테이블 추가
    # key: 테이블 키
    # name: 담보명
    # total: 총 보장액
    # nonLife: 손해 보험 보장액
    # life: 생명 보험 보장액
    # mutual: 공제/체신보험 보장액
    def buildTable(self, name: str, total: str, nonLife: str, life: str, mutual: str) -> dict:
        return {
            "name": name,
            "total": total,
            "nonLife": nonLife,
            "life": life,
            "mutual": mutual
        }

    def bulidTableGroup(self, group: str, items: list) -> dict:
        return {
            "groupName": group,
            "items": items
        }

    def buildTableUsingWord(self, words: list, start: int) -> dict:
        return self.buildTable(words[start], words[start + 1], words[start + 3], words[start + 4], words[start + 5])
