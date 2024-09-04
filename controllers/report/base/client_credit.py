class ClientCreditReport:

    def __init__(self) -> None:
        pass

    def html_report(self, query_result=None):

        css_border = "border: 0.14em solid;"

        content_body = ""
        for index, item in enumerate(query_result):
            content_body += f"""
                <tr>
                    <td style="border-left: 0.1em solid black">{item['consecutivo']}</td>
                    <td>{item['start_payment_at']}</td>
                    <td>{item['code_transaction']}</td>
                    <td>{item['way_to_pay']}</td>
                    <td>{item['pago_valor']}</td>
                    <td style="border-right: 0.1em solid black">{item['update_by_Usuario']}</td>
                </tr>
            """
        
        css ="""
            th, td {
                padding: 0.3em;
            }
            td{
                border-top: 0.1em solid black;
                border-bottom: 0.1em solid black;
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
            <h5>Fecha Aprobacion Credito: {query_result[0]['start_credit_at']}</h5>
            <h5>Codigo Credito: {query_result[0]['code2']}</h5>
            <h5>Nombres Cliente: {query_result[0]['first_name']} {query_result[0]['last_name']}</h5>
            <h5>Tipo Identificacion Cliente: {query_result[0]['type_identification']}</h5>
            <h5>Numero Identificacion Cliente: {query_result[0]['number_identification']}</h5>
            <h5>Celular Cliente: {query_result[0]['celular']}</h5>
            <h5>Direccion Cliente: {query_result[0]['client_address']}</h5>
            <h5>Valor Credito: {query_result[0]['value']}</h5>
            <h5>Total a Pagar: {query_result[0]['utility']}</h5>
            <h5>Pagado: {query_result[0]['total_pagos']}</h5>
            <h5>Cantidad de Cuotas: {query_result[0]['quota']}</h5>
            <h5>Cantidad Cuotas Pagas: {query_result[0]['total_cuotas_pagas']}</h5>
                <table>
                    <thead>
                        <tr>
                            <th>Cantidad(No es el # de cuota)</th>
                            <th>Fecha Pago</th>
                            <th>Codigo Transaccion</th>
                            <th>Tipo</th>
                            <th>Valor</th>
                            <th>Cobrador</th>
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