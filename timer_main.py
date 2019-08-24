import threading
import call_timer
import datetime


def daily_call():
    keyJson = '{"version": 4, "id": "661f6b70-b9b3-11e9-9fee-8c859052a951", "address": "n1ae3JErG9V779Tnx8jWy11JYnaBiN5Y5S9", "crypto": {"ciphertext": "4ebba0473c262492bbb4013326e54ce06bf0595acfe93b54aefa04dca03b8cf4", "cipherparams": {"iv": "9e702902fddb5679ca996caa2fb52faf"}, "cipher": "aes-128-ctr", "kdf": "scrypt", "kdfparams": {"dklen": 32, "salt": "0f48ca8c4b5267061aa9f619db5fd076a74fc4862fd69ca99d7aa8667c323271", "n": 4096, "r": 8, "p": 1}, "mac": "468c115d184c999463de48c5a6f361005e86dae956cfb544bd6795e201449b40", "machash": "sha3256"}}'
    password = "whatever518"
    contract = "n1JmhE82GNjdZPNZr6dgUuSfzy2WRwmD9zy"

    now_time = datetime.datetime.now()
    caller = Call_trigger(keyJson, password, contract)
#    caller.api_call()
    count=0
    keys_list=[keyJson, password, contract,count]
    threading.Timer(30, call_func1, keys_list).start()

    print('当前线程数为{}'.format(threading.activeCount()))
#    result=caller.callContract(func1,args1)
#    print(result)
    timer=threading.Timer(60,daily_call)
    timer.start()

timer=threading.Timer(1,daily_call)
timer.start()
