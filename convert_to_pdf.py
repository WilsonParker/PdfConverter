from src.Utils.FileUtil import FileUtil
from src.Utils.PdfUtil import PdfUtil

pdfUtil = PdfUtil()
fileUtil = FileUtil()

try:
    for pdfPath in fileUtil.getPaths(fileUtil.getInputPath()):
        data = pdfUtil.convertPdfToData(pdfPath)
        # print(data)
        htmlStr = pdfUtil.convertDataToPythonHtml(data)
        pdfUtil.convertHtmlToPdf(htmlStr, fileUtil.getFileName(pdfPath))
        # break
except FileNotFoundError:
    raise RuntimeError(f"오류: '{pdfPath}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    raise RuntimeError(f"PDF 처리 중 오류 발생: {e} {pdfPath}")
