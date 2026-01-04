from .BasePage import BasePage


class Page2(BasePage):
    def isCorrect(self, page) -> bool:
        return False
    
    def extract(self, page) -> dict:
        pass

