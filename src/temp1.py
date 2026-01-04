import fitz  # PyMuPDF
import re

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def convert_pdf_numbers(input_path, output_path):
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"파일을 열 수 없습니다: {e}")
        return

    # 숫자 패턴 정규식 (천 단위 콤마 포함)
    # 예: 100, 1,000, 13.5 등 매칭 (날짜 포맷인 2025-12-04 등은 제외하기 위해 단순 숫자 위주로 탐색)
    number_pattern = re.compile(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?')

    print(f"🔄 변환 시작: {input_path} -> {output_path}")

    for page_num, page in enumerate(doc):
        # 페이지 내의 모든 단어 정보를 가져옵니다 (x0, y0, x1, y1, "text", block_no, line_no, word_no)
        words = page.get_text("words")
        
        # 수정을 위해 페이지에서 감지된 텍스트들을 리스트로 관리
        replacements = []

        for w in words:
            original_text = w[4]
            rect = fitz.Rect(w[0], w[1], w[2], w[3]) # 텍스트 좌표

            # 1. 텍스트에서 숫자만 추출 (콤마 제거)
            clean_text = original_text.replace(',', '')

            # 2. 숫자인지 판별 (날짜(2025-12-04)나 전화번호 등 특수문자가 섞인 경우 제외하고 순수 숫자만 타겟팅)
            if clean_text.isdigit():
                val = int(clean_text)
                
                # 날짜(연도)나 전화번호 앞자리 등은 곱하지 않으려면 여기에 조건을 추가해야 합니다.
                # 현재는 요청대로 모든 발견된 숫자를 2배로 합니다.
                new_val = val * 2
                new_text = f"{new_val:,}" # 천 단위 콤마 다시 추가
                
                replacements.append((rect, original_text, new_text))
            
            elif is_float(clean_text):
                val = float(clean_text)
                new_val = val * 2
                
                # 소수점 처리 (필요시 포맷 조정)
                if new_val.is_integer():
                    new_text = f"{int(new_val):,}"
                else:
                    new_text = f"{new_val:,.2f}"
                
                replacements.append((rect, original_text, new_text))

        # 3. 덮어쓰기 작업 (Redaction -> Insert)
        for rect, old_text, new_text in replacements:
            # (1) 기존 텍스트 가리기 (흰색 사각형으로 덮음)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

            # (2) 새로운 텍스트 삽입
            # 폰트 크기는 높이에 맞춰 대략적으로 조정 (조정 필요시 fontsize 수정)
            fontsize = rect.height * 0.8 
            
            # 텍스트 삽입 (위치는 rect의 시작점)
            # 한글 폰트 깨짐 방지를 위해 내장 폰트 혹은 별도 폰트 지정 필요할 수 있음
            # 여기서는 기본 헬베티카(Helvetica) 사용하되, 한글/특수문자는 fitz가 자동 처리 시도함
            try:
                page.insert_text(
                    (rect.x0, rect.y1 - (rect.height * 0.15)), # 베이스라인 조정
                    new_text,
                    fontsize=fontsize,
                    color=(0, 0, 0) # 검정색
                )
            except Exception as e:
                print(f"텍스트 삽입 오류: {e}")

    doc.save(output_path)
    print("✅ 변환 완료!")

# 실행
if __name__ == "__main__":
    # 업로드된 파일명 (1.pdf)
    input_file = "1.pdf" 
    output_file = "2.pdf"
    
    convert_pdf_numbers(input_file, output_file)