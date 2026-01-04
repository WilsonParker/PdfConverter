from abc import ABC, abstractmethod

from src.Utils.PdfUtil import PdfUtil


class BasePage(ABC):
    def __init__(self):
        super().__init__()
        self.pdfUtil = PdfUtil()

    # 현재 페이지 정보를 실행하는게 맞는지 파악 합니다
    @abstractmethod
    def isCorrect(self, page) -> bool:
        pass

    # 페이지 데이터를 추출 합니다
    @abstractmethod
    def extract(self, page) -> dict:
        pass
