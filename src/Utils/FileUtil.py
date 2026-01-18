import pathlib
from pathlib import Path


class FileUtil:

    # PDF 파일들이 들어있는 폴더 경로를 return 합니다
    def getPaths(self, path: str = "../input") -> list[Path] | None:
        folder_path = pathlib.Path(path)

        # 1. 폴더가 실제로 존재하는지 확인
        if not folder_path.exists():
            raise RuntimeError(f"오류: 지정된 폴더 '{folder_path}'를 찾을 수 없습니다.")
        else:
            # print(f"--- 폴더 '{folder_path.name}'의 PDF 파일 목록 ---")

            # 2. glob() 메서드를 사용하여 *.pdf 패턴에 일치하는 모든 파일을 찾습니다.
            # rglob()을 사용하면 하위 폴더까지 탐색할 수 있습니다.
            pdfFiles = list(folder_path.glob("*.pdf"))

            if not pdfFiles:
                raise RuntimeError(path + "이 폴더에서 PDF 파일을 찾을 수 없습니다.")
            else:
                return pdfFiles

    # 탬플릿 경로를 반환 합니다
    def getTemplatePath(self) -> str:
        return "resources/templates"

    # 스타일 경로를 반환 합니다
    def getStylePath(self) -> str:
        return "resources/styles"

    # 입력 경로를 반환 합니다
    def getInputPath(self) -> str:
        return "input"

    # 출력 경로를 반환 합니다
    def getOutputPath(self) -> str:
        return "output"

    # 프로젝트 루트 경로를 반환 합니다
    def getRootPath(self) -> Path:
        # 현재 파일(PdfUtil.py)의 위치
        current_file = Path(__file__).resolve()

        # 프로젝트 루트(PdfConverter/)로 이동
        return current_file.parent.parent.parent

    # 주어진 상대 경로를 절대 경로로 변환 합니다
    def getAbsolutePath(self, relativePath: str) -> Path:
        return self.getRootPath() / relativePath