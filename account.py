#! /usr/bin/env python

import oandapy
import queue
import multiprocessing
from threading import Event


class AccountRequest:
    """ 封装一个账户管理请求的数据 """
    def __init__(self, endpoint, method='GET', params=None):
        self.event = Event()
        self.endpoint = endpoint
        self.method = method
        self.params = params
        self.reply = None

    def wait_for_complete(self):
        """ For any function below, if choose no wait, you must invoke this function later to retrieve reply """
        self.event.wait()
        return self.reply


class Account(oandapy.API):
    """ 提供与账户管理有关的所有功能, 包括:
        1. 获取指定货币对的当前, 历史汇率
        2. 创建与获取账户信息
        3. 创建, 修改, 关闭订单, 获取订单信息
        4. 获取, 修改, 关闭交易
        5. 获取指定货币对的位置
        6. 获取交易历史记录
        7. Oanda Forex Lab 提供的功能
        账户管理模块运行在独立的进程中
    """
    def __init__(self, environment="practice", access_token=None, headers=None):
        """ Instantiates a account manager
            :param environment 模拟或真实环境
            :param access_token oanda REST API access token
            :param headers
            :param account_id, the account id
        """
        super(Account, self).__init__(environment=environment, access_token=access_token, headers=headers)
        self.process = multiprocessing.Process(target=self.__process_request)
        self.working = False
        self.request_queue = queue.Queue()


    def init(self):
        """ Initialize account module """
        self.working = True
        self.process.start()

    def deinit(self):
        """ De-initialize account module """
        self.working = False
        self.process.join()


    def get_instruments(self, account_id, no_wait, **params):
        """ Get a list of trade-able instruments (currency pairs, CFDs, and commodities) that are available for
            trading with the account specified.
            :param account_id: Required The account id to fetch the list of trade-able instruments for
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: fields, instruments. See http://developer.oanda.com/rest-live/rates/
        """
        if not self.working:
            return None
        r = AccountRequest('v1/instruments', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def __on_error(self, args):
        return str(args)

    def __process_request(self):
        while self.working:
            try:
                req = self.request_queue.get(block=True, timeout=1)
                req.reply = self.request(req.endpoint, req.method, req.params)
                req.event.set()
            except oandapy.OandaError as e:
                req.reply = self.__on_error(e.args)
                req.event.set()
            except queue.Empty:
                continue

    def __get_account_list(self):
        pass

    def __get_account_information(self, account_id):
        pass
