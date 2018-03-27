import fdb
from datetime import datetime

from load_config import load_config
from config_log import *


def connection():
    config = load_config()
    con = fdb.connect(dsn=config['PathBD'],
                      user='sysdba',
                      password='masterkey')
    return con


def consulta_sql(sql, parameters=()):
    try:
        con = connection()
        cur = con.cursor()
        cur.execute(sql, parameters)
        return cur
    except Exception as e:
        save_log_exception(e)


def executa_sql(sql, parameters=()):
    try:
        con = connection()
        cur = con.cursor()
        cur.execute(sql, parameters)
        outputParams = cur.fetchone()
        con.commit()
        cur.close()
        con.close()
        return outputParams
    except Exception as e:
        save_log_exception(e)


def inclui_cidade(nome_cidade, uf, cep):
    consulta = 'select first 1 id, nome from cidade where nome = ? and uf = ?'
    cur = consulta_sql(consulta, [nome_cidade.upper(), uf.upper()])
    cidade_id = cur.fetchall()
    cur.close()
    if len(cidade_id) > 0:
        return cidade_id[0][0]
    else:
        insert = """INSERT INTO CIDADE (EMPRESA_ID, USUARIO_ID, NOME, UF,
                 TIPO, PAIS_ID, SITUACAO, CEP)
                 VALUES
                ((select id from empresa
                   where empresa.registro_principal=1),
                 (select usuario_id from empresa
                   where empresa.registro_principal=1),
                  ?, ?, 1,
                 (select first 1 id from pais where pais.nome='BRASIL'),
                 1, ?) returning ID;"""
        out = executa_sql(insert, parameters=[nome_cidade.upper(),
                                              uf.upper(), cep[:5]])
        return out


def inclui_endereco_parceiro_negocio(rua, nro, complemento, bairro, cep,
                                     cidade_id, cliente_id):
    insert = """INSERT INTO ENDERECO_PARCEIRO
            (EMPRESA_ID, USUARIO_ID, TIPO,
            LOGRADOURO, NUMERO, COMPLEMENTO, BAIRRO, CEP, CIDADE_ID,
            PARCEIRO_NEGOCIO_ID, SITUACAO, ENDERECO_PRINCIPAL)
            VALUES (
                (select id from empresa
                    where empresa.registro_principal=1),
                (select usuario_id from empresa
                    where empresa.registro_principal=1),
                4, ?, ?, ?, ?, ?, ?, ?, 1, 1) returning ID"""

    executa_sql(insert, parameters=[rua.upper(),
                                    nro,
                                    complemento.upper(),
                                    bairro.upper(),
                                    cep.upper(),
                                    cidade_id,
                                    cliente_id])


def get_numero_rua(rua):
    rua = rua.upper()
    new_rua = rua.split(',')
    if len(new_rua) <= 1:
        new_rua = rua.split('Nº')
    if len(new_rua) <= 1:
        spl = len(rua)//2
        new_rua = [rua[:spl], rua[spl:]]

    numeros = [int(s) for s in new_rua[1].split() if s.isdigit()]
    return 'S/N' if len(numeros) == 0 else numeros[0]


def inclui_cliente(cliente):
    nome = cliente['razao_social']
    fantasia = cliente['nome_fantasia']
    if fantasia == '':
        fantasia = nome
    fones = '; '.join([fone['numero'] for fone in cliente['telefones']])
    e_mails = '; '.join([email['email'] for email in cliente['emails']])
    obs = cliente['observacao']

    if cliente['tipo'] == 'F':
        tipo_pessoa = 0
        cpf = cliente['cnpj']
        cnpj = None
        ie = 'ISENTO'
    else:
        tipo_pessoa = 1
        cnpj = cliente['cnpj']
        cpf = None
        ie = cliente['inscricao_estadual']

    insert = """INSERT INTO PARCEIRO_NEGOCIO (EMPRESA_ID, USUARIO_ID, SITUACAO,
                CLIENTE, FORNECEDOR, FUNCIONARIO, MOTORISTA, AGENCIABANCARIA,
                TRANSPORTADORA, SOCIO, VENDEDOR, EXPORTADOR, IMPORTADOR,
                DATA_CADASTRO, NOME, FANTASIA, FONES, E_MAILS, CPF, CNPJ,
                INSCRICAO_ESTADUAL, TIPO_PESSOA, OBS) VALUES (
                (select id from empresa
                       where empresa.registro_principal=1),
                (select usuario_id from empresa
                       where empresa.registro_principal=1),
                1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, current_date,
                ?, ?, ?, ?, ?, ?, ?, ?, ?)
                returning ID;"""
    cliente_id = executa_sql(insert, parameters=[nome.upper(),
                                                 fantasia.upper(),
                                                 fones, e_mails,
                                                 cpf, cnpj, ie, tipo_pessoa,
                                                 obs.upper()])

    cidade_id = inclui_cidade(nome_cidade=cliente['cidade'],
                              uf=cliente['estado'],
                              cep=cliente['cep'])

    if cidade_id > 0 and cliente_id[0] > 0:
        numero = get_numero_rua(rua=cliente['rua'])
        inclui_endereco_parceiro_negocio(rua=cliente['rua'],
                                         nro=numero,
                                         complemento=cliente['complemento'],
                                         bairro=cliente['bairro'],
                                         cep=cliente['cep'],
                                         cidade_id=cidade_id,
                                         cliente_id=cliente_id[0])

    return cliente_id[0]


def consulta_produto_pelo_id(codigo_meus_pedidos):
    consulta = 'select id, nome from produto where id = ?'
    cur = consulta_sql(consulta, [codigo_meus_pedidos])
    produto_id = cur.fetchall()
    cur.close()
    if len(produto_id) > 0:
        return produto_id[0][0], produto_id[0][1]
    else:
        return 0, 'NAO RELACIONADO'


def consulta_ultima_alteracao_cliente():
    # ?alterado_apos=2014-02-28%2012:32:55
    consulta = 'select max(data_hora_alteracao) from clientes_meus_pedidos'
    cur = consulta_sql(consulta)
    data_hora = cur.fetchall()
    if not (data_hora[0][0] is None):
        return '?alterado_apos={}%20{}'.format(data_hora[0][0].date(),
                                               data_hora[0][0].time())
    else:
        return ''


def relaciona_cliente_meus_pedidos(parceiro_negocio_id,
                                   codigo_cliente_mp,
                                   nome_mp, data_hora_alteracao):
    # data_hora_alteracao = data_hora_alteracao.strftime('%Y-%m-%d %H:%M:%S')
    nome_mp = nome_mp[:60]
    cur = consulta_sql("""select id from clientes_meus_pedidos
                                      where parceiro_negocio_id = ?
                                      and meus_pedidos_id = ?""",
                       parameters=[parceiro_negocio_id, codigo_cliente_mp])
    relacao_existente = cur.fetchall()
    if len(relacao_existente) == 0:
        insert = """ INSERT INTO CLIENTES_MEUS_PEDIDOS (USUARIO_ID,
                 EMPRESA_ID, SITUACAO, PARCEIRO_NEGOCIO_ID, MEUS_PEDIDOS_ID,
                 NOME_MEUS_PEDIDOS, DATA_HORA_ALTERACAO)
                 values ((select first 1 id from usuario
                           where usuario.master=1),
                          (select first 1 id from empresa
                           where empresa.registro_principal=1),
                          1, ?, ?, ?, ?)
                 returning ID;"""
        out = executa_sql(insert,
                          parameters=[parceiro_negocio_id, codigo_cliente_mp,
                                      nome_mp, data_hora_alteracao])
        return out[0]
    else:
        return relacao_existente[0][0]


def consulta_parceiro_negocio_por_id(parceiro_negocio_id):
    consulta = """select parceiro_negocio.id, parceiro_negocio.nome,
                  parceiro_negocio.fantasia, parceiro_negocio.tipo_pessoa,
                  parceiro_negocio.cnpj, parceiro_negocio.cpf,
                  parceiro_negocio.inscricao_estadual, ep.logradouro,
                  ep.numero, ep.complemento, ep.cep, ep.bairro,
                  cidade.nome cidade_nome, cidade.uf cidade_uf,
                  parceiro_negocio.e_mails, parceiro_negocio.fones
                  from parceiro_negocio
                  inner join endereco_parceiro ep on
                      ep.parceiro_negocio_id = parceiro_negocio.id
                      and ep.endereco_principal = 1
                  inner join cidade on cidade.id = ep.cidade_id
                  where parceiro_negocio.id = ? """
    cur = consulta_sql(consulta, [parceiro_negocio_id])
    pn = cur.fetchone()
    columns = [column[0] for column in cur.description]
    if pn is not None:
        pn = dict(zip(columns, pn))
        fones = pn['FONES'].split(';')
        emails = pn['E_MAILS'].split(';')
        tipo = 'J' if pn['TIPO_PESSOA'] == 1 else 'F'
        fantasia = pn['FANTASIA'] if pn['TIPO_PESSOA'] == 1 else ''
        cnpj = pn['CNPJ'] if pn['TIPO_PESSOA'] == 1 else pn['CPF']
        ie = pn['INSCRICAO_ESTADUAL'] if pn['TIPO_PESSOA'] == 1 else ''
        parceiro_negocio = {'razao_social': pn['NOME'],
                            'tipo': tipo,
                            'nome_fantasia': fantasia,
                            'cnpj': cnpj,
                            'inscricao_estadual': ie,
                            'rua': pn['LOGRADOURO']+', '+pn['NUMERO'],
                            'complemento': pn['COMPLEMENTO'],
                            'cep': pn['CEP'],
                            'bairro': pn['BAIRRO'],
                            'cidade': pn['CIDADE_NOME'],
                            'estado': pn['CIDADE_UF'],
                            'observacao': '',
                            'emails': emails,
                            'telefones': fones}
        return parceiro_negocio


def consulta_parceiro_negocio(cnpj_cpf, nome):
    if len(cnpj_cpf) == 11 or len(cnpj_cpf) == 14:
        campo = 'cpf' if len(cnpj_cpf) == 11 else 'cnpj'
        consulta = 'select first 1 id from parceiro_negocio where '+campo+'=?'
        cur = consulta_sql(consulta, [cnpj_cpf, cnpj_cpf])
        parceiro_negocio_id = cur.fetchall()
        if len(parceiro_negocio_id) > 0:
            return parceiro_negocio_id[0][0]
        else:
            return 0
    else:
        consulta = 'select first 1 id from parceiro_negocio where nome=?'
        cur = consulta_sql(consulta, [nome.upper()])
        parceiro_negocio_id = cur.fetchall()
        if len(parceiro_negocio_id) > 0:
            return parceiro_negocio_id[0][0]
        else:
            return 0


if __name__ == '__main__':
    pass
