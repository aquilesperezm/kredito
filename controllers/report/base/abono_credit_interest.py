class AbonoCreditInterestReport:
    def __init__(self) -> None:
        pass

    def html_report(self, query_result=None):
        css_border = "border: 0.14em solid;"

        # content_body = ""
        # for index, item in enumerate(query_result):
        #     content_body += f"""
        #         <tr>
        #             <td style="border-left: 0.1em solid black">{item['consecutivo']}</td>
        #             <td>{item['start_payment_at']}</td>
        #             <td>{item['code_transaction']}</td>
        #             <td>{item['way_to_pay']}</td>
        #             <td>{item['pago_valor']}</td>
        #             <td style="border-right: 0.1em solid black">{item['update_by_Usuario']}</td>
        #         </tr>
        #     """
        
        css ="""
            th, td {
                padding: 0.3em;
            }
            td{
                border-top: 0.1em solid black;
                border-bottom: 0.1em solid black;
            }
            .title{
                text-align: center;
            }
        """        

        data = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
                <style>
                    {css}
                </style>
            </head>
            <body>
            <h1 class="title"> Reporte de Cartera</h1>
            <div class="content-div">
                <h3>Reporte por Fecha Abono Interes</h3>
                <h5>Prestado a Clientes: {query_result[0]['prestado_a_clientes']}</h5>
                <h5>Pagado por Clientes: {query_result[0]['pagado_por_clientes']}</h5>
                <h5>Abono a Credito (83%): {query_result[0]['credit_value']}</h5>
                <h5>Abono a Intereses (17%): {query_result[0]['intereses_value']}</h5>
                <br/>
                <br/>
                <h3>Pagos Dia Seleccionado</h3>
                <h5>Cantidad Pago Total a Recibir: {query_result[0]['total_recibir']}</h5>
                <h5>Abono Pago a Credito (83%): {query_result[0]['credit_payment']}</h5>
                <h5>Abono Pago a Interes (17%): {query_result[0]['intereses_payment']}</h5>
            </div>
            </body>
            </html>
        """
        return data