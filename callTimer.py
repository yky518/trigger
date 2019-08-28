# -*- coding:utf-8 -*-
# neb, account, contract 所有信息在__init__中修改，

from nebpysdk.src.account.Account import Account
from nebpysdk.src.core.Address import Address
from nebpysdk.src.core.Transaction import Transaction
from nebpysdk.src.core.TransactionCallPayload import TransactionCallPayload
from nebpysdk.src.client.Neb import Neb
import json
import threading
import time
import random
import re


class CallTrigger:

    def __init__(self):
        self.neb = Neb("https://testnet.nebulas.io")
        self.chain_id = 1001
        # account & address
        self.from_account = Account("5876489b63d456e3c82b043d235b46f76d4503b613230ed47d10bc4921e22f6a")
        self.from_addr = self.from_account.get_address_obj()

        # block height
        self.height_begin = 0
        self.height_next = 0

        # time_skip, 300seconds
        self.time_skip = 300

        # times checking the balance，3 times one day
        self.check_times = 3

        # period height
        self.period_height = 6000

        # contract address
        self.distribute = "n1qndLHUUkePQ9rWU1JZyfZJDqZNH5o3zLg"
        self.staking_proxy = 'n1wXY91Dh7NxWyxpXcPbYJFGoof2mTLWPKw'

    def get_nonce(self):

        # get nonce
        resp = self.neb.api.getAccountState(self.from_addr.string()).text
        print(resp)
        resp_json = json.loads(resp)
        print(resp_json)
        nonce = int(resp_json['result']['nonce']) + int(resp_json['result']['pending'])
        return nonce

    def get_receipt(self, tx_hash):

        while True:
            try:
                res = self.neb.api.getTransactionReceipt(tx_hash).text
                obj = json.loads(res)
                status = obj["result"]["status"]
            except:
                continue
            if status != 2:
                return res
            else:
                time.sleep(5)
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

        # prepare to addr
        to_addr = Address.parse_from_string(contract_addr)
        print("from_addr", self.from_addr.string())
        print("to_addr  ", contract_addr)

        # nonce
        nonce = self.get_nonce()

        # calls
        tx = Transaction(self.chain_id, self.from_account, to_addr, 0, nonce + 1, payload_type, payload, gas_price,
                         gas_limit)
        tx.calculate_hash()
        tx.sign_hash()
        res = self.neb.api.sendRawTransaction(tx.to_proto()).text

        print(res)
        obj = json.loads(res)
        txhash = obj["result"]["txhash"]

        return txhash

    def check_balance(self):

        # nonce
        nonce = self.get_nonce()
        # get current page count
        re1 = self.neb.api.call(self.from_addr.string(), self.staking_proxy, "0", nonce + 1, "200000", "200000",
                                {'function': 'getCurrentPageCount', 'args': '[]'}).text

        print(re1)
        obj = json.loads(re1)
        pages = int(obj['result']['result'])

        # check
        for page in range(pages):
            tx_hash = self.call_contract("check", '[%d]' % page, self.staking_proxy)
            res = self.get_receipt(tx_hash)
            print(res)

    def calculate(self, sessionid):

        # nonce
        nonce = self.get_nonce()
        # calculate
        print(sessionid)
        tx_hash = '6b22c098d3d4ffa150aa98028d84128b8ca2d431f3ffffa258f38b74c2bd74c6' #self.call_contract("calculateTotalValue", "[%s]" % str(sessionid), self.staking_proxy)
        res = self.get_receipt(tx_hash)
        print(res)
        obj = json.loads(res)
        status = obj["result"]["status"]
        if status == 1:
            pattern = re.compile(r'{\"hasNext\":(.*?),\"sessionId\":(.*?)}')
            match = re.search(pattern, obj["result"]["execute_result"])
            hasNext = match.group(1)
            sessionid = int(match.group(2))
            print('hasNext: %s, sessionid: %d' % (hasNext, sessionid))
            if hasNext != 'false':
                # next calculate
                self.calculate(sessionid)
            else:
                return status

        return status

    def distribute_trigger(self):
        # call the trigger
        tx_hash = 'e28619be955f094c36e2c2481c301c94ac66a6576d26a7782b7a243ef774970e' #self.call_contract("trigger", "[]", self.distribute)
        res = self.get_receipt(tx_hash)
        print(res)
        obj = json.loads(res)
        status = obj["result"]["status"]
        execute_result = obj["result"]['execute_result']

        if status == 1:
            pattern = re.compile(r'{\"period\":(.*?),\"start\":(.*?),\"end\":(.*?),\"page\":(.*?),\"hasNext\":(.*?)}')
            match = re.search(pattern, obj["result"]["execute_result"])
            hasNext = match.group(5)
            print('hasNext: %s' % hasNext)

            if hasNext != 'false':
                self.distribute_trigger()

    def daily_timer(self):
        # time_skip, 300seconds, 288 times a day
        seconds_one_day = 24 * 60 * 60
        times_one_day = int(seconds_one_day / self.time_skip)

        # check the balance
        possibility = self.check_times / times_one_day
        rand = random.random()
        if rand < possibility:
            self.check_balance()

        # block height now
        results = self.neb.api.getNebState().text
        obj = json.loads(results)
        height_now = int(obj["result"]["height"])
        print("height now: %d, height next: %d" % (height_now, self.height_next))

        # Run the trigger
        if height_now > self.height_next:
            # calculate

            status = self.calculate('null')

            # distribute
            if status == 1:
                self.distribute_trigger()

            # Change the height_next
            self.height_next += self.period_height

        # call next Timer
        print('current threading:{}'.format(threading.activeCount()))
        timer = threading.Timer(self.time_skip, self.daily_timer)
        timer.start()

    def core(self):
        # block height now and height of next circle
        results = self.neb.api.getNebState().text
        obj = json.loads(results)
        self.height_begin = int(obj["result"]["height"])
        self.height_next = self.height_begin + self.period_height

        threading.Timer(1, self.daily_timer).start()


if __name__ == "__main__":
    caller = CallTrigger()
    caller.core()
