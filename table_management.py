"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Script used to determine how to seat customers in such a way to reduce the number of tables and ensure minimum distances.
# Applied to Sagra Dosson 2020
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from __future__ import print_function
import sys
import getopt
from fpdf import FPDF

y_scroll = 40.0 # y-coordinate to start printing the tables disposition
x_scroll = 0.0 # x-coordinate to start printing the tables disposition
column = 1

class PDF2(FPDF):

    def print_riservato(self, referente):
        self.set_xy(0.0,0.0)
        self.set_text_color(0, 0, 0)
        self.set_font('poppins_medium', '', 150)
        self.cell(w=297.0, h=100.0, align='C', txt="RISERVATO", border=0)
        
        self.set_xy(0.0,150.0)
        self.set_font('poppins_medium', '', 80)
        self.cell(w=297.0, h=250.0, align='C', txt="{}".format(referente), border=0)

# Class to generate PDF
class PDF(FPDF):
    
    def check_end_column_page(self):
        global x_scroll
        global y_scroll
        
        if self.get_y() - 250 > 0:
            print("ok")
            if x_scroll == 0.0:
                x_scroll = 100.0
                y_scroll = 40.0
            else:
                self.add_page()
                x_scroll = 0.0
                y_scroll = 0.0
            
            self.set_xy(x_scroll, y_scroll)
    
    def print_border(self):
        self.set_line_width(0.0)
        self.line(5.0,5.0,205.0,5.0) # top one
        self.line(5.0,292.0,205.0,292.0) # bottom one
        self.line(5.0,5.0,5.0,292.0) # left one
        self.line(205.0,5.0,205.0,292.0) # right one
    
    def print_logo(self):
        self.set_xy(90,6.0)
        self.image('san_vigilio.png',  link='https://www.parrocchiadosson.it/sagra/prenotazioni', type='png', w=30, h=30)
    
    def print_title(self, tot_posti):
        self.set_xy(0.0,24.0)
        self.set_font('poppins_medium', '', 30)
        self.set_text_color(0, 0, 0)
        self.cell(w=210.0, h=40.0, align='C', txt="DISTRIBUZIONE TAVOLI ({} posti)".format(tot_posti), border=0)
        
    """def print_tot_posti(self, tot_posti):
        global y_scroll
        
        x_scroll = 0.0
        self.set_xy(x_scroll,y_scroll)
        self.set_font('poppins_medium', '', 30)
        self.set_text_color(0, 0, 0)
        self.cell(w=210.0, h=40.0, align='C', txt="POSTI TOTALI: {}".format(tot_posti), border=0)
    """
        
    def print_distribution(self, num_tavolo, ref, posti_pr):
        global y_scroll
        global x_scroll
        
        self.set_xy(x_scroll, y_scroll)
        self.set_text_color(0, 0, 0)
        self.set_font('poppins_medium', '', 24)
        
        self.check_end_column_page() # to generate new column or new page
        
        self.cell(w=110.0, h=40.0, align='C', txt="TAVOLO {}".format(num_tavolo), border=0)
        
        self.set_font('poppins_regular', '', 16)
        if type(ref) == list:
            for i, (r,p) in enumerate(zip(ref, posti_pr),0):
                y_scroll += 8.0
                self.check_end_column_page() # to generate new column or new page
                self.set_xy(x_scroll, y_scroll)
                self.cell(w=110.0, h=40.0, align='C', txt="{} ({} posti)".format(r, p), border=0)
        else:
            y_scroll += 8.0
            self.check_end_column_page() # to generate new column or new page
            self.set_xy(x_scroll, y_scroll)
            self.cell(w=110.0, h=40.0, align='C', txt="{} ({} posti)".format(ref, posti_pr), border=0)
        
        y_scroll += 16.0


MAX_TAVOLI = 6 # maximum number of seats in a table
DISTANCE_CONSTANT = 2 # fixed number to ensure distance between people

def get_data(day, pranzo):
    
    temp = {}
    
    f = open("prenotazioni.txt", "r")
    lines = f.readlines()
    for line in lines:
        l = line.split('|')
        l = l[1:]
        
        day_temp = int(l[1])
        pranzo_temp = int(l[2])
        
        if day_temp == day and pranzo_temp == pranzo: # select GIORNO and PRANZO
            temp[l[3]] = int(l[4])
    f.close()
    
    # SI SUPPONE NON CI SIANO REFERENTI CON NOMI DOPPI (Python dict does not support duplicated keys)
    temp = sorted(temp.items(), key=lambda x: x[1], reverse=True)
    
    prenotazioni = {}
    
    for key, value in temp:
        prenotazioni[key] = value
    
    return prenotazioni

# Main algorithm
def main(day, pranzo, pdf):
    prenotazioni = get_data(day, pranzo)
    # temp_prenotazioni = prenotazioni.copy()
    
    print(prenotazioni)
    
    tot_posti = 0
    for k, v in prenotazioni.items():
        tot_posti += v
    
    pdf.print_title(tot_posti)
    
    num_tavoli = 0
    
    while len(prenotazioni) > 0:
        referente = list(prenotazioni.keys())[0]
        posti_prenotati = prenotazioni[referente]
        
        if posti_prenotati % MAX_TAVOLI == 0:
            num_tavoli += 1
            del prenotazioni[referente]
            
            print("\nTAVOLO {}:".format(num_tavoli))
            print("   ", referente, "({} posti)".format(posti_prenotati))
            
            pdf.print_distribution(num_tavoli, referente, posti_prenotati)
        else:
            # Find the minimum number of tables needed to store the actual posti_prenotati
            temp_num_tavoli = 1
            while posti_prenotati > MAX_TAVOLI*temp_num_tavoli:
                temp_num_tavoli += 1
            
            # Compute the available seats subtracting the actual posti_prenotati
            posti_disp = MAX_TAVOLI*temp_num_tavoli - posti_prenotati
            posti_disp -= DISTANCE_CONSTANT
            
            num_tavoli += 1
            del prenotazioni[referente]
            
            print("\nTAVOLO {}:".format(num_tavoli))
            print("   ", referente, "({} posti)".format(posti_prenotati))
            
            ref = []
            posti_pr = []
            
            ref.append(referente)
            posti_pr.append(posti_prenotati)
            
            
            found = False
            i = 0
            while posti_disp > 0 and not found and i < posti_disp:
                keys = [key for (key, value) in prenotazioni.items() if value == posti_disp-i]
                
                if len(keys) != 0:
                    for k in keys:
                        if prenotazioni[k] % MAX_TAVOLI != 0 and posti_disp >= prenotazioni[k]:
                            print("   ", k, "({} posti)".format(prenotazioni[k]))
                            
                            ref.append(k)
                            posti_pr.append(prenotazioni[k])
                            
                            posti_disp -= prenotazioni[k]
                            posti_disp -= DISTANCE_CONSTANT
                            i = 0
                            
                            found = True
                            del prenotazioni[k]
                else:
                    i += 1

            pdf.print_distribution(num_tavoli, ref, posti_pr)
            
    # pdf.print_tot_posti(tot_posti)
    print("\nTAVOLI DA UTILIZZARE: ", num_tavoli)

if __name__ == '__main__':

    short_options = "g:p:h"
    long_options = ["giorno=", "pranzo=", "help"]
    
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    help = None
    day = None
    pranzo = None
    
    # Evaluate given options
    for current_argument, current_value in arguments:
        if current_argument in ("-g", "--giorno"):
            day = int(current_value)
        elif current_argument in ("-p", "--pranzo"):
            pranzo = int(current_value)
        elif current_argument in ("-h", "--help"):
            help = 1
            print("\nExecute this script passing three values:")
            print("-g or --giorno to set the day")
            print("-p or --pranzo to set the lunch (0 or 1)")
    
    if day is not None and pranzo is not None:
        # PDF object
        pdf = PDF(orientation='P', unit='mm', format='A4')
        
        pdf.add_font('poppins_medium', '', 'Poppins_Medium.ttf', uni=True)
        pdf.add_font('poppins_regular', '', 'Poppins_Regular.ttf', uni=True)
        
        pdf.add_page()
        pdf.set_auto_page_break(1)
        #pdf.print_border()
        pdf.print_logo()
        pdf.set_author('Davide')
        
        main(day, pranzo, pdf)
        
        pdf.output('tavoli_{}_sett.pdf'.format(day),'F')
        
        
        """ Generate PDF with "Riservato XXX" """
        pren = get_data(day, pranzo)
        pdf2 = PDF2(orientation='L', unit='mm', format='A4')
        pdf2.add_font('poppins_medium', '', 'Poppins_Medium.ttf', uni=True)
        pdf2.add_page()
        pdf2.set_author('Davide')
        
        for k,v in pren.items():
            pdf2.print_riservato(k)
            
        pdf2.output('riservato_{}_sett.pdf'.format(day),'F')
        
    else:
        print("\nBPP needs three arguments. See -h or --help\n")
