import requests
import json
import csv

from load_config import *
from config_log import *
from bd import *


def consulta_pedidos(pedido=True, orcamento=False, cancelado=False):
    try:
        filtro_data = consulta_ultima_alteracao_pedido()
        consulta_pedido = '?status=2' if pedido else ''
        consulta_orcamento = '?status=1' if orcamento else ''
        consulta_cancelado = '?status=0' if cancelado else ''
        url = '{}meuspedidos.com.br/api/v1/pedidos?{}{}{}{}'.format(
                                                                url_prefix(),
                                                                filtro_data,
                                                                pedido,
                                                                orcamento,
                                                                cancelado)

        response = requests.get(url, headers=headers())
        save_log_info('obtem_lista_pedidos {}.'.format(response))

        data = json.loads(response.text)

        for pedido in data:
            print('-'*20)
            id_cliente_erp = consulta_id_cliente_erp(pedido['cliente_id'])
            config = load_config()
            print(pedido['cliente_id'], pedido['status'], pedido['numero'])
            print('ID Cliente no ERP:', id_cliente_erp)
            print('R$', pedido['total'], pedido['condicao_pagamento'])
            print(pedido['data_emissao'])
            print(pedido['observacoes'])
            print('Itens:')
            for item in pedido['items']:
                print(item['produto_codigo'], item['produto_nome'])
                print(item['quantidade'], item['observacoes'])
                print(item['preco_liquido'], item['subtotal'])
            print(pedido['ultima_alteracao'])

    except Exception as e:
        raise save_log_exception(e)
