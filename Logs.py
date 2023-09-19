from datetime import datetime
import Config as cn
from colorama import init
init(autoreset=True)
from colorama import Fore,Back,Style


def add_log(msg_type,str):
    message_type = 'u'
    message_color = Style.RESET_ALL
    match msg_type:
        case 'e':
            message_type = '[ERR]'
            message_color = Fore.RED + Style.BRIGHT
        case 'i':
            message_type = '[INF]'
            message_color = Style.DIM
        case 'w':
            message_type = '[WAR]'
            message_color = Fore.YELLOW
        case 'g':
            message_type = '[GOO]'
            message_color = Fore.GREEN + Style.BRIGHT


    if cn.logging == True:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(message_color + '['+time+']' + message_type + str)    