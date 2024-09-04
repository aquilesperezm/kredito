class DeudaByClientReport:

    def __init__(self) -> None:
        pass

    def html_report(self, query_result=None):

        css_border = "border: 0.14em solid;"
        content_body = ""
        for index, item in enumerate(query_result):
            content_body += f"""
                <tr>
                    <td style="border-left: 0.1em solid black">{item['start_credit_at']}</td>
                    <td>{item['code2']}</td>
                    <td>{item['first_name']} {item['last_name']}</td>
                    <td>{item['finaliza_credito']}</td>
                    <td>{item['phone']}</td>
                    <td>{item['utility']}</td>
                    <td>{item['value_paid']}</td>
                    <td>{item['quota']}</td>
                    <td>{item['total_cuotas_pagas']}</td>
                    <td>{float(item['utility'])/int(item['quota'])}</td>
                    <td>{item['ultimo_pago']}</td>
                    <td style="border-right: 0.1em solid black">{item['total_dia_mora']}</td>
                </tr>
            """
        
        css ="""
            body{
                font-size: 0.8em;
            }
            th, td {
                padding: 0.3em;
            }
            td{
                border-top: 0.1em solid black;
                border-bottom: 0.1em solid black;
            }
            @page {
                size: letter;
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
                <h5>Reporte de Deuda por cliente</h5>
                <table>
                    <thead>
                        <tr>
                            <th>Fecha Aprobacion Credito</th>
                            <th>Codigo Credito</th>
                            <th>Nombres Cliente</th>
                            <th>Debe finalizar</th>
                            <th>Celular Cliente</th>
                            <th>Total a Pagar</th>
                            <th>Pagado</th>
                            <th>Cantidad Cuotas</th>
                            <th>Total Cuotas Pagas</th>
                            <th>Valor Cuota</th>
                            <th>Ultimo Pago</th>
                            <th>Dias en Mora</th>
                        </tr>
                    </thead>
                    <tbody>
                        {content_body}
                    </tbody>
                </table>
            </body>
            </html>
        """
        return data