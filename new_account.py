from nebpysdk.src.account.Account import Account
from nebpysdk.src.core.Address import Address
from nebpysdk.src.core.Transaction import Transaction
from nebpysdk.src.core.TransactionBinaryPayload import TransactionBinaryPayload
from nebpysdk.src.core.TransactionCallPayload import TransactionCallPayload
from nebpysdk.src.client.Neb import Neb
import json
import random
import string
import time

def newAccount(json_list,password_list,addrno,amount):

    # generate a new account
    account = Account()
    
    # export account
    password = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    account_json = account.to_key(bytes(password.encode()))
    print(account_json)

    json_list[addrno] = account_json
    password_list[addrno] = password
    
    # load account
    account = Account.from_key(account_json, bytes(password.encode()))
    print(account.get_address_str())
    print(account.get_private_key())
    print(account.get_public_key())

    neb = Neb("https://mainnet.nebulas.io")
    keyJson = '{"version": 4, "id": "661f6b70-b9b3-11e9-9fee-8c859052a951", "address": "n1ae3JErG9V779Tnx8jWy11JYnaBiN5Y5S9", "crypto": {"ciphertext": "4ebba0473c262492bbb4013326e54ce06bf0595acfe93b54aefa04dca03b8cf4", "cipherparams": {"iv": "9e702902fddb5679ca996caa2fb52faf"}, "cipher": "aes-128-ctr", "kdf": "scrypt", "kdfparams": {"dklen": 32, "salt": "0f48ca8c4b5267061aa9f619db5fd076a74fc4862fd69ca99d7aa8667c323271", "n": 4096, "r": 8, "p": 1}, "mac": "468c115d184c999463de48c5a6f361005e86dae956cfb544bd6795e201449b40", "machash": "sha3256"}}'
    password = "whatever518"
    
    # prepare from&to addr
    from_account = Account.from_key(keyJson, bytes(password.encode()))
    from_addr = from_account.get_address_obj()
    to_addr = Address.parse_from_string(account.get_address_str())
    print("from_addr", from_addr.string())
    print("to_addr  ", to_addr.string())
    
    # prepare transaction, get nonce first
    resp = neb.api.getAccountState(from_addr.string()).text
    
    print(resp)
    resp_json = json.loads(resp)
    print(resp_json)
    nonce = int(resp_json['result']['nonce'])
    
    chain_id = 1
    # PayloadType
    payload_type = Transaction.PayloadType("binary")
    # payload
    payload = TransactionBinaryPayload("binary").to_bytes()
    # gasPrice
    gas_price = 20000000000
    # gasLimit
    gas_limit = 60000
    
    # binary transaction example
    tx = Transaction(chain_id, from_account, to_addr, amount, nonce + 1, payload_type, payload, gas_price, gas_limit)
    tx.calculate_hash()
    tx.sign_hash()
    res = neb.api.sendRawTransaction(tx.to_proto()).text
    
    print(res)
    obj = json.loads(res)
    txhash = obj["result"]["txhash"]

    while(True):
        try:
            res = neb.api.getTransactionReceipt(txhash).text
            obj = json.loads(res)
            status = obj["result"]["status"]
        except:
            continue
        if status != 2:
            print(res)
            break
        else:
            time.sleep(1)
            print("Waiting the transaction to be confirmed.")

    return json_list, password_list

