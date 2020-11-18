from __future__ import print_function
from fpdf import FPDF

# Class to generate PDF
class PDF(FPDF):
    
    def print_num(self, num):
        self.set_xy(0.0,0.0)
        self.set_font('poppins_medium', '', 500)
        self.set_text_color(0, 0, 0)
        self.cell(w=297.0, h=210.0, align='C', txt="{}".format(num), border=0)
        

if __name__ == '__main__':

    """ PDF con numeri dei tavoli """
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.add_font('poppins_medium', '', 'Poppins_Medium.ttf', uni=True)
    pdf.set_author('Davide')
    pdf.add_page()
    #pdf.set_auto_page_break(1)
    
    for i in range(1,51):
        pdf.print_num(i)
    
    pdf.output('numeri_tavoli.pdf','F')
