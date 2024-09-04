from fpdf import FPDF, HTMLMixin
class PDF(FPDF, HTMLMixin):
  
    def footer(self):
        # Page number with condition isCover
        self.set_y(-15) # Position at 1.5 cm from bottom
        self.cell(0, 10, 'Page  ' + str(self.page_no()) + '  |  {nb}', 0, 0, 'C') 
    # def __init__(self, orientation='P',unit='mm',format='A4'):
    #     self.isCover = False
    #     # Override add_page methode
        
            
    # def footer(self):
    #     # Page number with condition isCover
    #     self.set_y(-15) # Position at 1.5 cm from bottom
    #     if self.isCover == False:   
    #         self.cell(0, 10, 'Page  ' + str(self.page_no) + '  |  {nb}', 0, 0, 'C') 
    # def add_page(self,  same= True, orientation='', isCover= False):
	#     FPDF.add_page(self, same= same, orientation=orientation)

class CarteraReport:
    def __init__(self) -> None:
        pass

    def html_report(self, get_query, path_write):
        font_size = 8
        pdf = PDF(orientation="landscape",format=(300, 800))
        # pdf = PDF(orientation="landscape",format="legal")
        pdf.add_page()
        pdf.set_font("Times", size=font_size)
        rows_per_page = 18
        cols_per_page = 22
        print_h = pdf.h - pdf.t_margin - pdf.b_margin
        print_w = pdf.w - pdf.l_margin - pdf.r_margin
        c_h = print_h / rows_per_page
        c_w = print_w / cols_per_page
        # pdf.set_draw_color(255, 0, 0)
        # pdf.set_line_width(1)
        # pdf.rect(0, 0, pdf.w, pdf.h, "D")

        # pdf.set_draw_color(0, 0, 0)
        # pdf.set_line_width(0.2)
        # pdf.rect(0.5, 0.5, pdf.w - 0.5, pdf.h - 0.5, "D")
        # pdf.set_y(-15)
        # pdf.cell(0, 10, 'Page  ' + str(pdf.page_no) + '  |  {nb}', 0, 0, 'C')
        total_prestado = 0
        total_interes = 0
        total_pagado = 0
        total_capital_pagado = 0
        total_interes_pagado = 0
        total_saldo_pendiente = 0
        total_interes_pendiente = 0
        total_capital_pendiente = 0
        count = 0
        total_prestamo = 0
        total_saldo = 0
        # txt_w = pdf.get_string_width(str(item['concat'])) 
        max_length = self.get_max_length_of_names(get_query, pdf)
        pdf.cell(pdf.w, c_h, "Reporte de Cartera", border=0, ln=0, align="C")
        for index, item in enumerate(get_query):
            count += 1
            if count == 1:
                pdf.cell(max_length, c_h, "Nombres", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Nombre Credito", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Fecha Inicio", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Fecha Fin", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Forma de Pago", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Prestado", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Intereses", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Total Prestamo", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Capital Pagado", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Interes Pagado", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Total Pagado", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Saldo Pendiente", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Interes Pendiente", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Capital Pendiente", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Saldo Prestamo", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Total Cuotas", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Cuotas Pagas", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Cuotas Pendientes", border=1, ln=0, align="L")
                pdf.cell(c_w, c_h, "Cuotas en Mora", border=1, ln=0, align="L")
                pdf.ln()
            # txt_w = pdf.get_string_width(str(item['concat']))
            # txt_h = font_size * 0.352778 # convert pt to mm
            total_prestado += float(item['prestado'])
            total_interes += float(item['intereses'])
            total_pagado += float(item['total_pagado'])
            total_capital_pagado += float(item['capital_pagado'])
            total_interes_pagado += float(item['interes_pagado'])
            total_saldo_pendiente += float(item['saldo_pendiente'])
            total_interes_pendiente += float(item['interes_pendiente'])
            total_capital_pendiente += float(item['capital_pendiente'])
            total_prestamo += float(item['total_prestamo'])
            total_saldo += float(item['saldo_pendiente'])
            # pdf.cell(txt_w, txt_h, item['concat'], border=1, ln=0, align="L")
            
            # pdf.multi_cell(c_w, c_h, item['concat'], border=1, ln=0, align="L", max_line_height=pdf.font_size)
            pdf.cell(max_length, c_h, item['concat'], border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, item["nombre_credito"], border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item["fecha_inicio"]), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item["finaliza_credito"]), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item["forma_de_pago"]), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['prestado']))), border=1, ln=0, align="L")                    
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['intereses']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item["total_prestamo"]))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['capital_pagado']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['interes_pagado']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['total_pagado']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['saldo_pendiente']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['interes_pendiente']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item['capital_pendiente']))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str("{:,.2f}".format(float(item["saldo_pendiente"]))), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item['total_cuotas']), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item['cuotas_pagas']), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item['cuotas_pendientes']), border=1, ln=0, align="L")
            pdf.cell(c_w, c_h, str(item['cuotas_mora']), border=1, ln=0, align="L")
            
            if count >= rows_per_page-2:
                pdf.add_page()
                count = 0
            else:
                pdf.ln()
        pdf.cell(max_length, c_h, "Totalizado", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_prestado)), border=1, ln=0, align="L")                    
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_interes)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_prestamo)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_capital_pagado)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_interes_pagado)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_pagado)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_saldo_pendiente)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_interes_pendiente)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_capital_pendiente)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_saldo)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, str("{:,.2f}".format(total_prestado)), border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.cell(c_w, c_h, "", border=1, ln=0, align="L")
        pdf.output(path_write)
        
    def get_max_length_of_names(self, data, pdf):
        max_length =0
        for index, item in enumerate(data):
            if pdf.get_string_width(str(item['concat']))> max_length:
                max_length = pdf.get_string_width(str(item['concat']))
        return max_length