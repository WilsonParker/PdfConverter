import fitz  # PyMuPDF
import re
import os

# --- 설정 및 보조 함수 ---

# PDF 전체에서 찾아야 할 주요 키(레이블) 목록을 정의합니다.
PREDEFINED_KEYS = [
    "정상계약", "월", "상해사망", "질병사망", "일반암",
    "뇌혈관질환", "허혈성심장질환", "실손", "입원의료비", "통원의료비"
]

def is_numerical_word(text):
    """텍스트에 숫자(0-9)가 포함되어 있는지 확인합니다."""
    clean_text = re.sub(r'[,\원\억\만]', '', text)
    return bool(re.search(r'\d', clean_text))

def get_word_bounding_boxes(doc):
    """PDF에서 모든 단어와 그 좌표를 추출합니다."""
    all_words = []
    for page_num, page in enumerate(doc):
        # 'words' 포맷: (x0, y0, x1, y1, "text", block_no, line_no, word_no)
        words = page.get_text("words")
        for w in words:
            all_words.append({
                'page': page_num,
                'text': w[4],
                'rect': fitz.Rect(w[0], w[1], w[2], w[3]),
                'x0': w[0], 'y0': w[1], 'x1': w[2], 'y1': w[3],
                'height': w[3] - w[1]
            })
    return all_words

def find_nearest_numerical_words(words, key_word):
    """주어진 키 옆에 있는 숫자 값들을 찾습니다 (오른쪽으로 정렬된 값)."""
    key_y_center = (key_word['y0'] + key_word['y1']) / 2
    y_tolerance = (key_word['y1'] - key_word['y0']) / 2

    numerical_values = []
    for word in words:
        if word['page'] != key_word['page']:
            continue

        word_y_center = (word['y0'] + word['y1']) / 2

        if abs(key_y_center - word_y_center) < y_tolerance:
            if word['x0'] > key_word['x1']:
                if is_numerical_word(word['text']):
                    numerical_values.append(word)

    numerical_values.sort(key=lambda w: w['x0'])
    return numerical_values

# --- 로고 추가 함수 ---

def add_logo_to_page(page, logo_path, rect):
    """
    지정된 페이지에 로고 이미지를 삽입합니다.

    :param page: fitz.Page 객체
    :param logo_path: 로고 이미지 파일 경로 (PNG, JPG 등)
    :param rect: 로고가 삽입될 사각형 영역 (fitz.Rect)
    """
    try:
        # insert_image(rect, filename=..., keep_proportion=True)
        # 로고 파일이 존재하고 rect가 유효한 경우에만 삽입
        if os.path.exists(logo_path):
            page.insert_image(rect, filename=logo_path, keep_proportion=True)
            print(f"✨ 페이지 {page.number + 1}에 로고 '{logo_path}' 삽입 완료.")
        else:
            print(f"⚠️ 경고: 로고 파일 '{logo_path}'을(를) 찾을 수 없습니다. 로고 삽입을 건너뜁니다.")
    except Exception as e:
        print(f"❌ 페이지 {page.number + 1}에 로고 삽입 중 오류 발생: {e}")

# --- 메인 실행 함수 ---

def map_and_fill(source_pdf_path, target_pdf_path, output_pdf_path, logo_path=None):

    # 이전 출력 파일 제거 (요청 사항)
    if os.path.exists(output_pdf_path):
        try:
            os.remove(output_pdf_path)
            print(f"🗑️ 이전 파일 '{output_pdf_path}'를 제거했습니다.")
        except Exception as e:
            print(f"❌ 이전 파일 제거 실패: {e}. 작업을 중단합니다.")
            return

    # 1. 문서 로드 및 모든 단어 추출
    doc_source = fitz.open(source_pdf_path)
    doc_target = fitz.open(target_pdf_path)
    source_words = get_word_bounding_boxes(doc_source)
    target_words = get_word_bounding_boxes(doc_target)

    insertions = []

    print(f"🔄 '{target_pdf_path}'에 '{source_pdf_path}'의 값 채우기 시작...")

    # (데이터 매핑 및 삽입 로직은 변경 없이 그대로 유지...)
    processed_target_keys = set()
    for key_text in PREDEFINED_KEYS:
        key_matches_in_target = [w for w in target_words if w['text'] == key_text]
        key_matches_in_source = [w for w in source_words if w['text'] == key_text]

        if not key_matches_in_target or not key_matches_in_source:
            continue

        key_word_target = key_matches_in_target[0]
        key_word_source = key_matches_in_source[0]

        key_id = (key_word_target['page'], key_word_target['x0'], key_word_target['y0'])
        if key_id in processed_target_keys:
            continue

        values_in_source = find_nearest_numerical_words(source_words, key_word_source)

        if not values_in_source:
            processed_target_keys.add(key_id)
            continue

        base_x = key_word_target['x1'] + 10
        base_y = key_word_target['y1']

        APPROX_COLUMN_WIDTH = 150

        for i, value_word in enumerate(values_in_source):
            text_to_insert = value_word['text']
            insert_x = base_x + (i * APPROX_COLUMN_WIDTH)
            font_height = value_word['height']
            fontsize = font_height * 0.8

            insertions.append({
                'page': key_word_target['page'],
                'text': text_to_insert,
                'point': (insert_x, base_y - (font_height * 0.15)),
                'fontsize': fontsize
            })

        processed_target_keys.add(key_id)
    # (데이터 매핑 및 삽입 로직 끝)

    # 4. 대상 문서에 삽입 작업 수행 및 로고 추가
    for page_num in range(len(doc_target)):
        page = doc_target[page_num]

        # 4-1. 텍스트 데이터 삽입
        for item in [i for i in insertions if i['page'] == page_num]:
            try:
                page.insert_text(
                    item['point'],
                    item['text'],
                    fontsize=item['fontsize'],
                    color=(0, 0, 0) # 검정색
                )
            except Exception as e:
                print(f"❌ 페이지 {page_num+1}에 '{item['text']}' 삽입 중 오류 발생: {e}")

        # 4-2. 로고 이미지 삽입 (선택 사항)
        if logo_path:
            # --- 로고 위치 및 크기 설정 ---
            # 예시: 첫 페이지 (page_num == 0)의 우측 상단에 로고를 삽입합니다.
            # (PDF 좌표계: 좌측 하단 (0, 0), 우측 상단 (page.rect.width, page.rect.height))

            # 페이지 크기
            page_width = page.rect.width
            # 로고 크기 설정 (예: 너비 100pt, 높이 50pt)
            logo_width = 100
            logo_height = 50

            # 로고 삽입 위치 (우측 상단 모서리에서 안쪽으로)
            x0 = page_width - logo_width - 30  # 오른쪽 여백 30pt
            y0 = 30                            # 위쪽 여백 30pt
            x1 = x0 + logo_width
            y1 = y0 + logo_height

            logo_rect = fitz.Rect(x0, y0, x1, y1)

            # 모든 페이지에 로고를 넣으려면 `if` 조건 제거,
            # 첫 페이지에만 넣으려면 `if page_num == 0:` 와 같이 사용
            # 여기서는 모든 페이지에 삽입하도록 설정합니다.
            add_logo_to_page(page, logo_path, logo_rect)


    # 5. 새 파일로 저장
    try:
        doc_target.save(output_pdf_path)
        print(f"✅ 작업 완료! 결과 파일: '{output_pdf_path}'")
    except Exception as e:
        print(f"❌ 파일 저장 중 오류 발생: {e}")
    finally:
        doc_source.close()
        doc_target.close()


# 실행
if __name__ == "__main__":
    SOURCE_PDF = "a.pdf"
    TARGET_REMOVED_PDF = "b_removed.pdf"
    OUTPUT_FILLED_PDF = "b_filled.pdf"

    # 📌 여기에 실제 로고 파일 경로를 입력하세요.
    LOGO_IMAGE_PATH = "logo.png"

    # 로고 경로를 추가하여 함수를 실행합니다.
    map_and_fill(SOURCE_PDF, TARGET_REMOVED_PDF, OUTPUT_FILLED_PDF, LOGO_IMAGE_PATH)
