import requests
import json
import csv

from load_config import *
from config_log import *
from bd import *


def inclui_cliente_meus_pedidos(parceiro_negocio_id):
    try:
        url = '{}meuspedidos.com.br/api/v1/clientes'.format(url_prefix())
        novo_registro = consulta_parceiro_negocio_por_id(parceiro_negocio_id)
        print(novo_registro)
        response = requests.post(url, json=novo_registro, headers=headers())
        if response.status_code == 201:
            relaciona_lista_clientes()
        else:  # 412 é erro
            info_retorno = json.loads(response.text)
            save_log_info(info_retorno)
            file_name = 'output/ret_inc_id_{}.json'.format(parceiro_negocio_id)
            with open(file_name, 'w') as outfile:
                json.dump(info_retorno, outfile)

    except Exception as e:
        raise save_log_exception(e)


def relaciona_lista_clientes():
    try:
        filtro_data = consulta_ultima_alteracao_cliente()
        url = '{}meuspedidos.com.br/api/v1/clientes{}'.format(url_prefix(),
                                                              filtro_data)
        response = requests.get(url, headers=headers())
        save_log_info('obtem_lista_clientes {}.'.format(response))

        data = json.loads(response.text)

        for row in data:
            parceiro_negocio_id = consulta_parceiro_negocio(
                                                    row['cnpj'],
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
#    relaciona_lista_clientes()
