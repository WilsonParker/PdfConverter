from abc import ABC, abstractmethod
from typing import Any

from src.Utils.FileUtil import FileUtil
from src.Utils.StringUtil import StringUtil


class BasePage(ABC):
    def __init__(self):
        super().__init__()
        self.fileUtil = FileUtil()
        self.stringUtil = StringUtil()

    # 페이지를 구분할 key
    @abstractmethod
    def getKey(self) -> str:
        pass

    # 현재 페이지 정보를 실행하는게 맞는지 파악 합니다
    @abstractmethod
    def isCorrect(self, page) -> bool:
        pass

    # 페이지 데이터를 추출 합니다
    @abstractmethod
    def extract(self, page) -> dict:
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

    # 기본 데이터 추출 (페이지 1, 2 공통)
    def baseDataPage1And2(self, words) -> dict:
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
            "number_of_insurance_contracts": words[11],
            # 월 보험료
            "monthly_insurance_premium": words[12],
            # 손해 보험
            "non_life_insurance": words[14],
            # 생명 보험
            "life_insurance": words[15],
            # 공제/체신보험
            "mutual_aid/postal_insurance": words[16],
            # 탬플릿 이름
            "template": self.getTemplatePage(),
        }
