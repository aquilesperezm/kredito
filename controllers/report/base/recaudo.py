class RecaudoReport:

    def __init__(self) -> None:
        pass

    def html_report(self, query_result=None):

        css_border = "border: 0.14em solid;"
        content_body = ""
        for index, item in enumerate(query_result):
            content_body += f"""
                <tr>
                    <td style="border-left: 0.1em solid black">{item['fecha_pago']}</td>
                    <td>{item['credito_fecha_aprobado']}</td>
                    <td>{item['credito_codigo']}</td>
                    <td>{item['cliente_nombres']}</td>
                    <td>{item['cliente_numero_identificacion']}</td>
                    <td>{item['cliente_celular']}</td>
                    <td>{item['cliente_direccion']}</td>
                    <td>{item['credito_valor_final']}</td>
                    <td>{item['credito_pagado']}</td>
                    <td>{item['numero_de_cuotas']}</td>
                    <td>{item['transaccion']}</td>
                    <td>{item['valor_pago']}</td>
                    <td style="border-right: 0.1em solid black">{item['total_credito_acumulado']}</td>"""
            
            if (index == len(query_result)-1):
                content_body += f"""
                    </tr>
                    <tr>
                        <td colspan="12">Total a Recibir: {item['total_recibir']}</td>
                    </tr>
                """
            else:
                content_body += f"""
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
                <table>
                    <thead>
                        <tr>
                            <th>Fecha del Pago</th>
                            <th>Fecha Aprobacion Credito</th>
                            <th>Codigo Credito</th>
                            <th>Nombres Cliente</th>
                            <th>Identificacion Cliente</th>
                            <th>Celular Cliente</th>
                            <th>Direccion Cliente</th>
                            <th>Total a Pagar</th>
                            <th>Pagado</th>
                            <th>Cantidad Cuotas</th>
                            <th>Transaccion Pago</th>
                            <th>Valor Cuota</th>
                            <th>Total Recibido del credito</th>
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