import re

from .BasePage import BasePage


# 전체 보장 현황 페이지
class Page2(BasePage):

    def getKey(self) -> str:
        return "page2_2"

    def isCorrect(self, page) -> bool:
        # 텍스트 추출 (가장 일반적)
        lines = page.extract_text().splitlines()
        print(lines)
        return "님의 전체 보장현황" in lines[0].strip() if lines else "" and lines[5].strip() == "상해사망"

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
                    # 경증치매진단
                    "mildDementiaDiagnosis": {
                        "total": words[50],
                        "nonLife": words[52],
                        "life": words[53],
                        "mutual": words[54],
                    },
                    # 간병인/간호간병상해일당
                    "caregiver/NursingCareInjuryDailyAllowance": {
                        "total": words[58],
                        "nonLife": words[60],
                        "life": words[61],
                        "mutual": words[62],
                    },
                    # 간병인/간호간병질병일당
                    "caregiver/NursingCareDiseaseDailyAllowance": {
                        "total": words[64],
                        "nonLife": words[66],
                        "life": words[67],
                        "mutual": words[68],
                    },
                },
                # 암 진단
                "cancerDiagnosis": {
                    # 일반암
                    "generalCancer": {
                        "total": words[70],
                        "nonLife": words[72],
                        "life": words[73],
                        "mutual": words[74],
                    },
                    # 유사암
                    "similarCancer": {
                        "total": words[76],
                        "nonLife": words[78],
                        "life": words[79],
                        "mutual": words[80],
                    },
                    # 고액암
                    "highCostCancer": {
                        "total": words[82],
                        "nonLife": words[84],
                        "life": words[85],
                        "mutual": words[86],
                    },
                    # 고액(표적) 항암치료비
                    "highCost(Targeted)AnticancerTreatmentExpenses": {
                        "total": words[88],
                        "nonLife": words[90],
                        "life": words[91],
                        "mutual": words[92],
                    },
                },
                # 뇌/심장 진단
                "brain/heartDiagnosis": {
                    # 뇌혈관질환
                    "cerebrovascularDisease": {
                        "total": words[94],
                        "nonLife": words[96],
                        "life": words[97],
                        "mutual": words[98],
                    },
                    # 뇌졸충
                    "stroke": {
                        "total": words[100],
                        "nonLife": words[102],
                        "life": words[103],
                        "mutual": words[104],
                    },
                    # 뇌출혈
                    "cerebralHemorrhage": {
                        "total": words[106],
                        "nonLife": words[108],
                        "life": words[109],
                        "mutual": words[110],
                    },
                    # 허혈성심장질환
                    "ischemicHeartDisease": {
                        "total": words[112],
                        "nonLife": words[114],
                        "life": words[115],
                        "mutual": words[116],
                    },
                    # 급성심근경색증
                    "acuteMyocardialInfarction": {
                        "total": words[118],
                        "nonLife": words[120],
                        "life": words[121],
                        "mutual": words[122],
                    },
                },
            }
        }

        print(extractedData)
        return extractedData
