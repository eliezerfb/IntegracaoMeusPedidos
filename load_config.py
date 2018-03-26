import json


def load_config():
    with open('config.json') as json_data:
        d = json.load(json_data)
    return d


def url_prefix():
    config = load_config()
    homologacao = config['Homologacao']
    if homologacao:
        url = 'https://sandbox.'
    else:
        url = 'https://integracao.'
    return url


def headers():
    config = load_config()
    headers = {
        'cache-control': 'no-cache',
        'ApplicationToken': config['ApplicationToken'],
        'CompanyToken': config['CompanyToken']
    }
    return headers


if __name__ == '__main__':
    print (url_prefix())
    print (headers())
