import re

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page2(BasePage):

    def getKey(self) -> str:
        return "page2"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        return "님의 전체 보장현황" in lines[0].strip() if lines else ""

    def extract(self, page) -> dict:
        print("*** is page 1 ***")
        # 각 딕셔너리에서 'text' 값만 추출하여 새로운 리스트 생성
        words = self.convertWords(page)
        self.printWords(words)

        extractedData = {
            # 이름
            "name": words[0],
            # 날짜
            "date": f"{words[4]} {words[5]}",
            # 나이
            "age": self.stringUtil.removeParentthses(words[6]),
            # 성별
            "gender": self.stringUtil.removeSpecialCharacters(words[7]),
            # 정상 계약 건수
            "numberOfNormalContracts": words[11],
            # 월 보험료
            "monthlyInsurancePremium": words[12],
            # 손해 보험
            "nonLifeInsurance": words[14],
            # 생명 보험
            "lifeInsurance": words[15],
            # 공제/체신보험
            "mutualAid/PostalInsurance": words[16],
        }

        table = {}

        # 유형 1의 페이지일 경우
        if "상해사망" in words[17]:
            table = {
                "사망장해": [
                    self.appendTableUsingWord(words, 17),
                    self.appendTableUsingWord(words, 23),
                    self.appendTableUsingWord(words, 31),
                    self.appendTableUsingWord(words, 37),
                ],
                "치매간병": [
                    self.appendTableUsingWord(words, 43),
                    self.appendTableUsingWord(words, 49),
                    self.appendTableUsingWord(words, 57),
                    self.appendTableUsingWord(words, 63),
                ],
                "암 진단": [
                    self.appendTableUsingWord(words, 69),
                    self.appendTableUsingWord(words, 75),
                    self.appendTableUsingWord(words, 83),
                    self.appendTableUsingWord(words, 89),
                ],
                "뇌/심장 진단": [
                    self.appendTableUsingWord(words, 95),
                    self.appendTableUsingWord(words, 101),
                    self.appendTableUsingWord(words, 108),
                    self.appendTableUsingWord(words, 115),
                    self.appendTableUsingWord(words, 121),
                ],
            }

        # 유형 2의 페이지일 경우
        if "상해입원의료비" in words[17]:
            table = {
                "실손의료비": [
                    self.appendTableUsingWord(words, 17),
                    self.appendTableUsingWord(words, 23),
                    self.appendTableUsingWord(words, 30),
                    self.appendTableUsingWord(words, 37),
                    self.appendTableUsingWord(words, 43),
                ],
                "수술입원": [
                    self.appendTableUsingWord(words, 49),
                    self.appendTableUsingWord(words, 55),
                    self.appendTableUsingWord(words, 61),
                    self.appendTableUsingWord(words, 68),
                    self.appendTableUsingWord(words, 75),
                    self.appendTableUsingWord(words, 81),
                    self.appendTableUsingWord(words, 87),
                ],
                "운전자 기타": [
                    self.appendTableUsingWord(words, 93),
                    self.appendTableUsingWord(words, 99),
                    self.appendTableUsingWord(words, 105),
                    self.appendTableUsingWord(words, 111),
                    self.appendTableUsingWord(words, 119),
                    self.appendTableUsingWord(words, 125),
                    self.appendTableUsingWord(words, 131),
                    self.appendTableUsingWord(words, 137),
                ],
            }

        extractedData["tables"] = table

        print(extractedData)
        return extractedData

    # 전체 보장 현황 테이블 추가
    # key: 테이블 키
    # name: 담보명
    # total: 총 보장액
    # nonLife: 손해 보험 보장액
    # life: 생명 보험 보장액
    # mutual: 공제/체신보험 보장액
    def appendTable(self, name: str, total: str, nonLife: str, life: str, mutual: str) -> dict:
        return {
            "name": name,
            "total": total,
            "nonLife": nonLife,
            "life": life,
            "mutual": mutual
        }

    def appendTableUsingWord(self, words: list, start: int) -> dict:
        return self.appendTable(words[start], words[start + 2], words[start + 3], words[start + 4], words[start + 5])
