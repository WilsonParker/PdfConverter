from abc import ABC, abstractmethod
from typing import Any

from src.Utils.DateUtil import DateUtil
from src.Utils.FileUtil import FileUtil
from src.Utils.StringUtil import StringUtil


class BasePage(ABC):
    def __init__(self):
        super().__init__()
        self.fileUtil = FileUtil()
        self.stringUtil = StringUtil()
        self.dateUtil = DateUtil()

    # 페이지를 구분할 key
    @abstractmethod
    def getKey(self) -> str:
        pass

    # 페이지의 최대 길이
    @abstractmethod
    def getMaxLength(self) -> int:
        pass

    # 테이블 데이터 크기에 따라 페이지를 분할 합니다
    @abstractmethod
    def dividePage(self, pdfData: dict, extractData: dict) -> list:
        pass

    # 현재 페이지 정보를 실행하는게 맞는지 파악 합니다
    @abstractmethod
    def isCorrect(self, page) -> bool:
        pass

    # 페이지 데이터를 추출 합니다
    @abstractmethod
    def extract(self, page, pdfData: dict) -> dict:
        pass

    # 데이터를 변환할 탬플릿 이름을 반환 합니다
    @abstractmethod
    def getTemplatePage(self) -> str:
        pass

    # page.extract_words() 결과를 단어 리스트로 변환합니다
    def convertWords(self, page) -> list[Any]:
        return [w['text'] for w in page.extract_words()]

    # words 를 순서대로 출력하여 디버깅에 도움을 줍니다
    def printWords(self, words):
        for i, word in enumerate(words, start=0):
            # i는 번호, word는 해당 단어의 정보(딕셔너리)
            # print(f"{i}. {word['text']} (위치: {word['x0']}, {word['top']})")
            print(f"{i}. {word}")

    # lines 를 순서대로 출력하여 디버깅에 도움을 줍니다
    def printLines(self, page):
        for i, line in enumerate(page.extract_text().splitlines(), start=0):
            print(f"{i}. {line}")

    # 기본 데이터 추출 (페이지 1, 2 공통)
    def buildBaseData(self, words) -> dict:
        # isNumberOfInsuranceContracts 가 숫자인지 여부 22, 아닌 경우 기본형(37개)/표준형
        if _is_integer(words[11]):
            isNumberOfInsuranceContracts = True
        else:
            isNumberOfInsuranceContracts = False

        return {
            # 고객 이름
            "user_name": words[0],
            # 날짜
            "date": f"{words[4]} {words[5]}",
            # 나이
            "age": self.stringUtil.removeParentthses(words[6]),
            # 성별
            "gender": self.stringUtil.removeSpecialCharacters(words[7]),
            # 정상 계약 건수
            "number_of_insurance_contracts": words[11] if isNumberOfInsuranceContracts else words[12],
            # 월 보험료
            "monthly_insurance_premium": words[12] if isNumberOfInsuranceContracts else words[13],
            # 손해 보험
            "non_life_insurance": words[14],
            # 생명 보험
            "life_insurance": words[15],
            # 공제/체신보험
            "mutual_aid/postal_insurance": words[16],
            # 탬플릿 이름
            "template": self.getTemplatePage(),
            # 페이지 최대 길이
            "max_length": self.getMaxLength(),
        }

    def buildBaseData2(self, words: list, pdfData: dict) -> dict:
        return {
            # 고객 이름
            "user_name": words[0],
            # 날짜
            "date": f"{words[4]} {words[5]}",
            # 나이
            "age": self.stringUtil.removeParentthses(words[6]),
            # 성별
            "gender": self.stringUtil.removeSpecialCharacters(words[7]),
            # 정상 계약 건수
            "number_of_insurance_contracts": pdfData["number_of_insurance_contracts"],
            # 월 보험료
            "monthly_insurance_premium": pdfData["monthly_insurance_premium"],
            # 탬플릿 이름
            "template": self.getTemplatePage(),
            # 페이지 최대 길이
            "max_length": self.getMaxLength(),
        }


def _is_integer(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False
