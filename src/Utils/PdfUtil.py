import pathlib
from pathlib import Path

import pdfplumber


class PdfUtil:

    # PDF 파일들이 들어있는 폴더 경로를 return 합니다
    def getPaths(self, path: str = "../input") -> list[Path] | None:
        folder_path = pathlib.Path(path)

        # 1. 폴더가 실제로 존재하는지 확인
        if not folder_path.exists():
            print(f"오류: 지정된 폴더 '{folder_path}'를 찾을 수 없습니다.")
        else:
            # print(f"--- 폴더 '{folder_path.name}'의 PDF 파일 목록 ---")

            # 2. glob() 메서드를 사용하여 *.pdf 패턴에 일치하는 모든 파일을 찾습니다.
            # rglob()을 사용하면 하위 폴더까지 탐색할 수 있습니다.
            pdfFiles = list(folder_path.glob("*.pdf"))

            if not pdfFiles:
                print(path + "이 폴더에서 PDF 파일을 찾을 수 없습니다.")
            else:
                return pdfFiles

    # pdf path 에 있는 데이터를 추출하여 dict 형태로 반환
    # 예시 사용
    # data_for_html = extract_data_from_pdf('input_a.pdf')
    def extractDataFromPdf(self, pdf: pdfplumber.PDF) -> dict:
        """
        지정된 PDF 파일에서 데이터를 추출합니다.
        (여기서는 첫 페이지의 모든 텍스트를 추출하는 간단한 예시)
        """
        extracted_data = {}
        try:
            first_page = pdf.pages[0]

            # 텍스트 추출 (가장 일반적)
            text_data = first_page.extract_text()
            extracted_data['content_text'] = text_data

            # 표 추출 (구조화된 데이터가 있을 경우)
            # tables = first_page.extract_tables()
            # extracted_data['content_tables'] = tables

            # 간단한 Key-Value 쌍 추출 (예시)
            # 이 부분은 실제 PDF 구조에 따라 정교하게 조정해야 합니다.
            # 예: '문서 번호: 12345'와 같은 패턴을 찾기
            document_number = "N/A"
            if "문서 번호:" in text_data:
                # 매우 간단한 정규식 또는 문자열 처리
                import re
                match = re.search(r"문서 번호:\s*(\w+)", text_data)
                if match:
                    document_number = match.group(1)

            extracted_data['document_id'] = document_number

        except Exception as e:
            print(f"PDF 처리 중 오류 발생: {e}")
            extracted_data['content_text'] = f"Error: {e}"
            extracted_data['document_id'] = "Extraction Failed"

        return extracted_data
