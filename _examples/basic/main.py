import json
import datetime

from pystashlog import Stash

def main():
    print('pystashlog')
    stash = Stash(ssl=False)

    while True:
        text_input = input('>> ')
        if text_input == 'exit':
            break
        try:
            msg = get_message(text_input)
            stash.write(msg)
            # response = con.read()
            # print('response = ', response)
        except Exception as e:
            print('error ', e)
    
    stash.release()

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