import re

from .BasePage import BasePage


class Page1(BasePage):

    def getKey(self) -> str:
        return "page1"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        print(page.extract_text())
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
            # 전체 보장 현황 List
            "overallCoverageStatus": {
                # 사망장해
                "deathAndDisability": {
                    # 상해사망
                    "wound": {
                        "total": words[18],
                        "nonLife": words[20],
                        "life": words[21],
                        "mutual": words[22],
                    },
                    # 질병 사망
                    "disease": {
                        "total": words[24],
                        "nonLife": words[26],
                        "life": words[27],
                        "mutual": words[28],
                    },
                    # 상해80% 미만 후유장해
                    "wound80": {
                        "total": words[32],
                        "nonLife": words[34],
                        "life": words[35],
                        "mutual": words[36],
                    },
                    # 질병80% 미만 후유장해
                    "disease80": {
                        "total": words[38],
                        "nonLife": words[40],
                        "life": words[41],
                        "mutual": words[42],
                    },
                },
                # 치매간병
                "dementiaCare": {
                    # 장기요양간병비
                    "longTermCareExpenses": {
                        "total": words[44],
                        "nonLife": words[46],
                        "life": words[47],
                        "mutual": words[48],
                    },
                },
            }
        }

        print(extractedData)
        return extractedData
