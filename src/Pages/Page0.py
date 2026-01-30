from .BasePage import BasePage


class Page0(BasePage):

    def dividePage(self, pdfData: dict, extractData: dict) -> list:
        pass

    def getMaxLength(self) -> int:
        return 0

    def getKey(self) -> str:
        return "page0"

    def getTemplatePage(self) -> str:
        return "template-00-cover.html"

    def isCorrect(self, page) -> bool:
        return False

    def extract(self, page, pdfData: dict) -> dict:
        return {}