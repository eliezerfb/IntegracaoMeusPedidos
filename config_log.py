import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    filename='log.txt',
                    level=logging.INFO)


def save_log_info(mensagem):
    print(mensagem)
    logging.info(mensagem)


def save_log_exception(mensagem):
    print(mensagem)
    logging.exception(str(mensagem))
