#! /usr/bin/env python

import requests
import queue
import threading
import json
from threading import Event
from exceptions import BadEnvironment


class ApiRequest:
    """
        封装一个API请求，交予请求处理进程处理
        在调用任意一个api函数时，如果用户选择no_wait，会得到ApiRequest的一个实例作为返回值
        用户必须自己调用wait_for_complete确保请求被处理；否则直接得到处理结果作为返回值
        对任意的api，请求成功时，处理结果包含了Oanda Web Server返回的结果，失败时为None，注意检查返回值
    """
    def __init__(self, endpoint, method='GET', params=None):
        self.event = Event()
        self.endpoint = endpoint
        self.method = method
        self.params = params
        self.response = None

    def wait_for_complete(self):
        """ For any function below, if choose no wait, you must invoke this function later to retrieve response """
        self.event.wait()
        return self.response


class Api:
    """
        提供Oanda REST API的所有封装, 包括:
        1. 获取指定货币对的当前, 历史汇率
        2. 创建与获取账户信息
        3. 创建, 修改, 关闭订单, 获取订单信息
        4. 获取, 修改, 关闭交易
        5. 获取指定货币对的位置
        6. 获取交易历史记录
        7. Oanda Forex Lab 提供的功能
        所有对API的调用运行在一个独立进程中
    """
    def __init__(self, environment="practice", access_token=None, headers=None):
        """ Instantiates a API wrapper
            :param environment: 模拟或真实环境
            :param access_token: oanda REST API access token
            :param headers:
        """
        if environment == 'sandbox':
            self.api_url = 'http://api-sandbox.oanda.com'
        elif environment == 'practice':
            self.api_url = 'https://api-fxpractice.oanda.com'
        elif environment == 'live':
            self.api_url = 'https://api-fxtrade.oanda.com'
        else:
            raise BadEnvironment(environment)
        self.access_token = access_token
        self.client = requests.Session()
        self.thread = threading.Thread(target=self.__thread_request)
        self.working = False
        self.request_queue = queue.Queue()
        if self.access_token:
            self.client.headers['Authorization'] = 'Bearer ' + self.access_token
        if headers:
            self.client.headers.update(headers)


    def init(self):
        """ Initialize account module """
        self.working = True
        self.thread.start()

    def deinit(self):
        """ De-initialize account module """
        self.working = False
        self.thread.join()


    def get_instruments(self, account_id, no_wait, **params):
        """ Get a list of trade-able instruments (currency pairs, CFDs, and commodities) that are available for
            trading with the account specified.
            :param account_id: Required The account id to fetch the list of trade-able instruments for
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/rates
        """
        if not self.working:
            return None
        params['accountId'] = account_id
        r = ApiRequest('v1/instruments', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_prices(self, no_wait, **params):
        """ Fetch live prices for specified instruments that are available on the OANDA platform
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/rates
        """
        if not self.working:
            return None
        r = ApiRequest('v1/prices', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_history(self, no_wait, **params):
        """ Get historical information on an instrument
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/rates
        """
        if not self.working:
            return None
        r = ApiRequest('v1/candles', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def create_account(self, no_wait, **params):
        """ Create an account. Valid only in sandbox.
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/accounts
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts', method='POST', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_accounts(self, no_wait, **params):
        """ Get a list of accounts owned by the user.
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/accounts
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_account(self, account_id, no_wait, **params):
        """ Get account information.
            :param account_id: Required The account id to fetch the information for
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/accounts
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}'.format(account_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def get_orders(self, account_id, no_wait, **params):
        """ This will return all pending orders for an account. Note: pending take profit or stop loss orders are
            recorded in the open trade object, and will not be returned in this request.
            :param account_id: Required The account id to fetch the orders
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/orders
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/orders'.format(account_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def create_order(self, account_id, no_wait, **params):
        """ Create a new order.
            :param account_id: Required The account id to create the order
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/orders
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/orders'.format(account_id), method='POST', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_order(self, account_id, order_id, no_wait, **params):
        """ Get information for an order.
            :param account_id: Required The account id to fetch the order information for
            :param order_id: Required The order identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/orders
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/orders/{1}'.format(account_id, order_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def modify_order(self, account_id, order_id, no_wait, **params):
        """ Modify an existing order.
            :param account_id: Required The account id to modify the order
            :param order_id: Required The order identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/orders
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/orders/{1}'.format(account_id, order_id), method='PATCH', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def close_order(self, account_id, order_id, no_wait, **params):
        """ Close an existing order.
            :param account_id: Required The account id to close the order
            :param order_id: Required The order identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/orders
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/orders/{1}'.format(account_id, order_id), method='DELETE', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def get_trades(self, account_id, no_wait, **params):
        """ Get a list of open trades.
            :param account_id: Required The account id to fetch trades information
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/trades
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/trades'.format(account_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_trade(self, account_id, trade_id, no_wait, **params):
        """ Get information on a specific trade.
            :param account_id: Required The account id to fetch trade information
            :param trade_id: Required The trade identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/trades
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/trades/{1}'.format(account_id, trade_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def modify_trade(self, account_id, trade_id, no_wait, **params):
        """ Modify an existing trade.
            :param account_id: Required The account id to modify trade
            :param trade_id: Required The trade identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/trades
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/trades/{1}'.format(account_id, trade_id), method='PATCH', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def close_trade(self, account_id, trade_id, no_wait, **params):
        """ Close an open trade.
            :param account_id: Required The account id to close trade
            :param trade_id: Required The trade identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/trades
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/trades/{1}'.format(account_id, trade_id), method='DELETE', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def get_positions(self, account_id, no_wait, **params):
        """ Get a list of all open positions.
            :param account_id: Required The account id to fetch positions information
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/positions
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/positions'.format(account_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_position(self, account_id, instrument, no_wait, **params):
        """ Get the position for an instrument.
            :param account_id: Required The account id to fetch position information
            :param instrument: Required The instrument
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/positions
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/positions/{1}'.format(account_id, instrument), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def close_position(self, account_id, instrument, no_wait, **params):
        """ Close an existing position.
            :param account_id: Required The account id to close position
            :param instrument: Required The instrument
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/positions
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/positions/{1}'.format(account_id, instrument), method='DELETE', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def get_transaction_history(self, account_id, no_wait, **params):
        """ Get transaction history
            :param account_id: Required The account id to fetch transaction history
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/transaction-history
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/transactions'.format(account_id), params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_transaction(self, account_id, transaction_id, no_wait):
        """ Get information for a transaction
            :param account_id: Required The account id to fetch transaction history
            :param transaction_id: Required The transaction identification
            :param no_wait: Indicate whether function will wait for request complete or return immediately
        """
        if not self.working:
            return None
        r = ApiRequest('v1/accounts/{0}/transactions/{1}'.format(account_id, transaction_id))
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def get_eco_calendar(self, no_wait, **params):
        """ Returns up to 1 year of economic calendar info
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/forex-labs/
        """
        if not self.working:
            return None
        r = ApiRequest('labs/v1/calendar', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_historical_position_ratios(self, no_wait, **params):
        """ Returns up to 1 year of historical position ratios
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/forex-labs/
        """
        if not self.working:
            return None
        r = ApiRequest('labs/v1/historical_position_ratios', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_historical_spreads(self, no_wait, **params):
        """ Returns up to 1 year of spread information
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/forex-labs/
        """
        if not self.working:
            return None
        r = ApiRequest('labs/v1/spreads', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_commitments_of_traders(self, no_wait, **params):
        """ Returns up to 4 years of Commitments of Traders data from the CFTC
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/forex-labs/
        """
        if not self.working:
            return None
        r = ApiRequest('labs/v1/commitments_of_traders', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()

    def get_orderbook(self, no_wait, **params):
        """ Returns up to 1 year of OANDA Order Book data
            :param no_wait: Indicate whether function will wait for request complete or return immediately
            :param params: Docs: http://developer.oanda.com/rest-live/forex-labs/
        """
        if not self.working:
            return None
        r = ApiRequest('labs/v1/orderbook_data', params=params)
        self.request_queue.put(r)
        return r if no_wait else r.wait_for_complete()


    def __thread_request(self):
        while self.working:
            try:
                req = self.request_queue.get(block=True, timeout=1)
                method = req.method.lower()
                requests_args = dict()
                requests_args['params' if method == 'get' else 'data'] = req.params or dict()
                response = getattr(self.client, method)('{0}/{1}'.format(self.api_url, req.endpoint), **requests_args)
                content = json.loads(response.content.decode('utf-8'))

                if response.status_code >= 400:
                    #raise OandaError(content)
                    print("OandaError: {0:d} - {1}".format(response.status_code, str(content)))
                else:
                    req.response = content

            except requests.RequestException as e:
                # raise OandaError(e)
                print("RequestException: " + str(e))
            except json.JSONDecodeError as e:
                # raise OandaError(e)
                print("JSONDecodeError: " + str(e))
            except queue.Empty:
                continue

            req.event.set()
