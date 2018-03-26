import json
import requests
import csv

from load_config import *
from config_log import *
from bd import consulta_produto_pelo_id


def obtem_lista_produtos():
    try:
        url = '{}meuspedidos.com.br/api/v1/produtos'.format(url_prefix())

        response = requests.get(url, headers=headers())
        save_log_info('obtem_lista_produtos {}.'.format(response))

        data = json.loads(response.text)

        with open('output/lista_produtos.csv', 'w', newline='') as csvfile:
            fieldnames = ['codigo_meus_pedidos', 'descricao_meus_pedidos',
                          'codigo_erp', 'descricao_erp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                produto_id, produto_nome = consulta_produto_pelo_id(
                                                                row['codigo']
                                                                )
                writer.writerow({fieldnames[0]: row['codigo'],
                                 fieldnames[1]: row['nome'],
                                 fieldnames[2]: produto_id,
                                 fieldnames[3]: produto_nome
                                 })
    except Exception as e:
        save_log_exception(e)


if __name__ == '__main__':
    obtem_lista_produtos()
