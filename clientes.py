import json
import requests
import csv

from load_config import *
from config_log import *
from bd import *

def inclui_cliente_meus_pedidos(parceiro_negocio_id):
    pass

def relaciona_lista_clientes():
    try:
        filtro_data = consulta_ultima_alteracao_cliente()
        url = '{}meuspedidos.com.br/api/v1/clientes{}'.format(url_prefix(),
                                                              filtro_data)
        response = requests.get(url, headers=headers())
        save_log_info('obtem_lista_clientes {}.'.format(response))

        data = json.loads(response.text)

        for row in data:
            parceiro_negocio_id = consulta_parceiro_negocio(row['cnpj'],
                                                            row['razao_social'])
            if parceiro_negocio_id == 0:
                parceiro_negocio_id = inclui_cliente(cliente=row)

            relaciona_cliente_meus_pedidos(parceiro_negocio_id,
                                           str(row['id']),
                                           row['razao_social'],
                                           row['ultima_alteracao'])
    except Exception as e:
        save_log_exception(e)

if __name__ == '__main__':
    pass
    relaciona_lista_clientes()
