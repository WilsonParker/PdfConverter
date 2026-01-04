from .BasePage import BasePage


class Page2(BasePage):
    def getKey(self) -> str:
        return "page2"

    def isCorrect(self, page) -> bool:
        return False
    
    def extract(self, page) -> dict:
        pass

