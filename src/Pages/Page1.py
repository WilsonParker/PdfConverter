import pdfplumber

from .BasePage import BasePage


class Page1(BasePage):

    def isCorrect(self, pdf: pdfplumber.PDF) -> bool:
        print(self.pdfUtil.extractDataFromPdf(pdf))
        return False

    def extract(self, page) -> dict:
        pass
