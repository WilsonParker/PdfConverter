import re


class StringUtil:

    # 소괄호 제거
    def removeParentthses(self, text: str) -> str:
        return text.strip("()")

    # 특수문자 제거
    def removeSpecialCharacters(self, text: str) -> str:
        return re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
