import fitz  # PyMuPDF
import re

def remove_numerical_text(input_path, output_path):
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"파일을 열 수 없습니다: {e}")
        return

    # 숫자를 포함하는 모든 텍스트를 찾기 위한 정규식 (하나 이상의 숫자를 포함하는 모든 문자열)
    numerical_pattern = re.compile(r'.*\d.*') 

    print(f"🔄 숫자 관련 텍스트 제거 시작: {input_path} -> {output_path}")

    for page_num, page in enumerate(doc):
        # 페이지 내의 모든 단어 정보를 가져옵니다 (x0, y0, x1, y1, "text", ...)
        words = page.get_text("words")
        
        removal_rects = []

        for w in words:
            text = w[4]
            rect = fitz.Rect(w[0], w[1], w[2], w[3]) # 텍스트 좌표

            # 텍스트에 숫자가 포함되어 있으면 제거 대상으로 판단
            if numerical_pattern.search(text):
                removal_rects.append(rect)

        # 제거 작업: 감지된 모든 영역을 흰색 사각형으로 덮어씌웁니다.
        for rect in removal_rects:
            # 흰색으로 채우기 (R, G, B = 1, 1, 1)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    # 변경된 문서를 새로운 이름으로 저장
    doc.save(output_path)
    print("✅ 제거 완료!")

# 실행
if __name__ == "__main__":
    # 업로드된 파일명 (b.pdf)
    input_file = "b.pdf" 
    output_file = "b_removed.pdf" # 결과 파일명
    
    remove_numerical_text(input_file, output_file)