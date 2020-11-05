import json
import datetime
import logging

import pystashlog

'''
init logger
'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main():
    print('pystashlog')
    stash = pystashlog.Stash(
        ssl=True,
        ssl_ca_certs='./_examples/secure/tls/server.crt',
        ssl_keyfile='./_examples/secure/tls/server.key',
    )

    # set custom handler with stash
    stash.setLevel(logging.INFO)
    logger.addHandler(stash)

    while True:
        text_input = input('>> ')
        if text_input == 'exit':
            break
        try:
            msg = get_message(text_input)
            logger.info(msg)
            # response = con.read()
            # print('response = ', response)
        except Exception as e:
            print('error ', e)
    
    stash.disconnect()

def get_message(message):
    json_dict = {
        'action': 'submit', 
        'time': str(datetime.datetime.today()), 
        'message': {
            'data': message
        }
    }
    return json.dumps(json_dict)
if __name__ == '__main__':
    main()