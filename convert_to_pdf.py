from src.Utils.PdfUtil import PdfUtil

pdfUtil = PdfUtil()

data = pdfUtil.convertPdfToData()
html_str = pdfUtil.convertDataToHtml(data)
pdfUtil.convertStrHtmlToPdf(html_str)
