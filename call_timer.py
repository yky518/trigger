from nebpysdk.src.account.Account import Account
from nebpysdk.src.core.Address import Address
from nebpysdk.src.core.Transaction import Transaction
from nebpysdk.src.core.TransactionBinaryPayload import TransactionBinaryPayload
from nebpysdk.src.core.TransactionCallPayload import TransactionCallPayload
from nebpysdk.src.client.Neb import Neb
import json
import threading
import time
from new_account import newAccount
import random


class Call_trigger:
    def __init__(self, keyJson, password):
        self.neb = Neb("https://testnet.nebulas.io")
        self.keyJson = keyJson
        self.password = password
        self.interval = 20
        self.height_begin = 0
        self.height_next = 0
        self.distribute = "n1sZLHKWuXAz13oLyF775c38Z9PcR4bTXbk"
        self.staking_proxy = 'n1pff2q7R3bz3vu3SdEu4PvmJEJHxijJmEF'

    def get_nonce(self, from_addr):

        # get nonce
        resp = self.neb.api.getAccountState(from_addr.string()).text
        print(resp)
        resp_json = json.loads(resp)
        print(resp_json)
        nonce = int(resp_json['result']['nonce']) + int(resp_json['result']['pending'])
        return nonce

    def getReceipt(self,txhash):

        while(True):
            try:
                res = self.neb.api.getTransactionReceipt(txhash).text
                obj = json.loads(res)
                status = obj["result"]["status"]
            except:
                continue
            if status != 2:
                return res
            else:
                time.sleep(1)
                print("Waiting the transaction to be confirmed.")

    def call_contract(self, func, args, contract_addr):

        # payload
        payload = TransactionCallPayload(func, args).to_bytes()

        # PayloadType
        payload_type = Transaction.PayloadType("call")

        # gasPrice
        gas_price = 20000000000

        # gasLimit
        gas_limit = 100000

        # prepare from&to addr
        from_account = Account.from_key(self.keyJson, bytes(self.password.encode()))
        from_addr = from_account.get_address_obj()
        to_addr = Address.parse_from_string(contract_addr)
        print("from_addr", from_addr.string())
        print("to_addr  ", to_addr.string())

        #nonce
        nonce=self.get_nonce(from_addr)

        # calls
        chain_id = 1001
        tx = Transaction(chain_id, from_account, to_addr, 0, nonce + 1, payload_type, payload, gas_price, gas_limit)
        tx.calculate_hash()
        tx.sign_hash()
        res = self.neb.api.sendRawTransaction(tx.to_proto()).text

        print(res)
        obj = json.loads(res)
        txhash = obj["result"]["txhash"]

        return txhash

    def check_balance(self):

        # prepare from&to addr
        from_account = Account.from_key(self.keyJson, bytes(self.password.encode()))
        from_addr = from_account.get_address_obj()

        #nonce
        nonce = self.get_nonce(from_addr)
        #get current page count
        re1 = self.neb.api.call(from_addr.string(), self.staking_proxy, "0", nonce+1, "200000", "200000", {'function': 'getCurrentPageCount', 'args':'[]'}).text

        print(re1)
        obj = json.loads(re1)
        pages = int(obj['result']['result'])

        # check
        for page in range(pages):
            result = self.neb.api.call(from_addr.string(), self.staking_proxy, "0", nonce+1, "200000", "200000", {'function': 'check', 'args': '[%d]'% page}).text
            print(result)

    def calculate(self, sessionid):

        # prepare from address
        from_account = Account.from_key(self.keyJson, bytes(self.password.encode()))
        from_addr = from_account.get_address_obj()

        #nonce
        nonce = self.get_nonce(from_addr)
        #calculate
        print(sessionid)
        txhash = self.call_contract("calculateTotalValue", "[%s]" % str(sessionid), self.staking_proxy)
        res = self.getReceipt(txhash)
        print(res)
        obj = json.loads(res)
        status = obj["result"]["status"]
        hasNext = obj["result"]["hasNext"]
        sessionid = obj['result']['sessionid']
        # next calculate
        if status ==1 and hasNext:
            self.calculate(sessionid)

    def distribute_trigger(self):
        #call the trigger
        txhash = self.call_contract("trigger", "[]", self.distribute)
        res = self.getReceipt(txhash)
        obj = json.loads(res)
        status = obj["result"]["status"]
        hasNext = obj["result"]["hasNext"]

        if status ==1 and hasNext:
            self.distribute_trigger()


    def daily_timer(self):
        #time_skip, 300seconds, 288 times a day
        time_skip = 300
        seconds_one_day = 24 * 60 * 60
        times_one_day = int(seconds_one_day / time_skip)

        #check the balance
        check_times = 3
        possibility = check_times / times_one_day
        rand = 0# random.random()
        if rand < possibility:
            res = self.check_balance()

        #block height now
        results = self.neb.api.getNebState().text
        obj = json.loads(results)
        height_now = int(obj["result"]["height"])
        print("height now: %d, height next: %d"%(height_now, self.height_next))

        #Run the trigger
        self.height_next = 0
        if height_now > self.height_next:
            #calculate
            self.calculate('null')

            #distribute
            self.distribute_trigger()

            #change the height_next
            self.height_next += 6000



        #call next Timer
        print('当前线程数为{}'.format(threading.activeCount()))
        timer = threading.Timer(time_skip, self.daily_timer)
        timer.start()

    def core(self):
        #block height now and height of next circle
        results = self.neb.api.getNebState().text
        obj = json.loads(results)
        self.height_begin = int(obj["result"]["height"])
        self.height_next = self.height_begin + 6000

        threading.Timer(1, self.daily_timer).start()

if __name__ == "__main__":
    keyJson = '{"version": 4, "id": "180cdc40-c5a4-11e9-b691-8c859052a951", "address": "n1HVrEzu9mFnEvM2UgoWtUR6Dq1PAZrXQzF", "crypto": {"ciphertext": "7e6d5d03a971382bffaa71967aff7c570e1c1b777d867dcc22924d0827eadce2", "cipherparams": {"iv": "3364f44a31345de97f36925126589c42"}, "cipher": "aes-128-ctr", "kdf": "scrypt", "kdfparams": {"dklen": 32, "salt": "8b74ce3001be76c31c6aa079c425114a4db1fce5911717801ec5c9675af07a04", "n": 4096, "r": 8, "p": 1}, "mac": "08476a286e05104f292404717b1d3c6fef4436385f7923b5a947ddd5fefbc23a", "machash": "sha3256"}}'
    password = 'whatever555'

    caller = Call_trigger(keyJson, password)
    caller.core()
