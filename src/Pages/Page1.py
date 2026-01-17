from .BasePage import BasePage


class Page1(BasePage):
    def getKey(self) -> str:
        return "page1"

    def isCorrect(self, page) -> bool:
        return False
    
    def extract(self, page) -> dict:
        pass

