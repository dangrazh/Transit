# =============================================================================
# External dependencies (packages that need to be installed):
# - PyPDF2
# - tabula-py
# =============================================================================


from PyPDF2 import PdfFileReader
#from PyPDF2.pdf import Destination
import tabula
#from pprint import pprint


# pdfminer imports
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTFigure, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser


class BookmarksTree:
    
    def __init__(self, list_in):
        self.bookmarks = []
        self._process_outline(list_in)
 
    
    def prettify(self, out_stream=None):
        
        for line in self.bookmarks:
            spacing = '  ' * (line[0] - 1)
            line_out = f'{line[0]}    {spacing}{line[1]}'
            
            if hasattr(out_stream, 'write'):
                out_stream.write(line_out + '\n')
            else:
                print(line_out)
        
        
    
    def _process_outline(self, list_in, level=0):
        
        level += 1
        
        for item in list_in:
            if isinstance(item, dict):
                self.bookmarks.append([level, item['/Title']])
            elif isinstance(item, list):
                self._process_outline(item, level)
            else:
                self.bookmarks.append([level, item])
        
        

def read_file_pypdf(file):

    with open(pdf_file_name, 'rb') as f_in:
        reader = PdfFileReader(f_in)
        
        no_of_pages = reader.numPages
        print(f'no of pages in document: {no_of_pages}')
        
        pfd_page = reader.getPage(327)
        pfd_txt = pfd_page.extractText()
        print(pfd_txt)




def read_file_pdfminer(file):
    
    text = ""
    stack = []

    with open(file, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        page = list(PDFPage.create_pages(doc))[327]
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        layout = device.get_result()
    
        for obj in layout:
            if isinstance(obj, LTTextBox):
                text += obj.get_text()
    
            elif isinstance(obj, LTFigure):
                stack += list(obj)

        print(text)
        print('-' * 40)
        print(stack)


#-------------------------------------------------------------------------------
# The script entry point
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    """
    This is the main body of the script 
    """

    # set the path and file name
    pdf_path = r'\\ubsprod.msad.ubs.net\groupshares\SWISS-DD\PROD_SUPP\PROJECTS\_25_Tools\17_ISO20022_Parser\Implementation Guidelines\ISO'
    pdf_file = r'ISO20022_MDRPart2_PaymentsClearingAndSettlement_2019_2020_v1.pdf'
    pdf_file_name = pdf_path + '\\' + pdf_file
    
    # Read the pdf file
    print('Reading the pdf file')
    
#    read_file_pypdf(pdf_file_name)
    read_file_pdfminer(pdf_file_name)

    # Read the same file with tabula
#    tables = tabula.read_pdf(pdf_file_name, multiple_tables=True, lattice=True, pages='all')
#    print(len(tables))
#    for df in tables:
#        #print all elements which have children
##        print(df[df[3] == '±'])
#        print(df)
    



#    # Get the bookmarks form pdf file
#    print('Getting the bookmarks from pdf file')
#    reader = PdfFileReader(pdf_file_name)
#    outlines = reader.outlines
#    
#    # Process the bookmarks
#    print('Process the bookmarks retreived')
#    bmt = BookmarksTree(outlines)
#    
#    #now print the bookmarks
#    print('Process the bookmarks')
#    with open('MDR_bookmarks_pacs.txt', 'w') as f_out:
#        bmt.prettify(f_out)
# 
#    print('Processing completed!')
