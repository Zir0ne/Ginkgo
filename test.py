#! /usr/bin/env python

""" 测试封装模块的功能 """

import stream
import rest
import time

environment  = "practice"
access_token = "711a43d784751e4df5f7fd0166561667-25503832b893d500f28d5ee691a04505"
account_id   = "1205962"


def main():
    api.init()
    # 获取账户列表
    response = api.get_accounts(False)
    if response:
        for account in response['accounts']:
            print(str(account))

    # 获取账户详细信息
    response = api.get_account(account_id, False)
    if response:
        print(str(response))

    # 获取货币对列表
    response = api.get_instruments(account_id, False,
                                   #fields='displayName,pip', 没用，不管给什么参数都返回所有的字段
                                   instruments='EUR_USD,AUD_CAD')
    if response:
        print(str(response))

    # 获取当前汇率
    response = api.get_prices(False,
                              instruments='EUR_USD,AUD_CAD',
                              since='2016-04-20T17:41:04')
    if response:
        print(str(response))

    # 获取历史汇率
    response = api.get_history(False,
                               instrument='EUR_USD',
                               count=2,                 # The number of candles to return in the response. Should not be specified if both the start and end parameters are also specified
                               #start='',                # The start timestamp for the range of candles requested
                               #end='',                  # The end timestamp for the range of candles requested
                               granularity='D',         # S5 S10 S15 S30 M1 M2 M3 M4 M5 M10 M15 M30 H1 H2 H3 H4 H6 H8 H12 D W M
                               candleFormat='midpoint', # midpoint or bidask
                               #includeFirst='false',    # If it is set to “true”, the candlestick covered by the start timestamp will be returned
                               #dailyAlignment=17,       # The hour of day used to align candles with hourly, daily, weekly, or monthly granularity
                               #weeklyAlignment='Friday',# The day of the week used to align candles with weekly granularity
                               #alignmentTimezone='America/New_York' # The timezone to be used for the dailyAlignment parameter
                              )
    if response:
        print(str(response))

    #


    # 启动实时汇率获取
#   rates.start(accountId=account_id, instruments='AUD_CAD')
#   time.sleep(5)

    # 关闭api函数工作线程
    api.deinit()
    # 关闭实时汇率获取线程
#   rates.stop()


if __name__ == "__main__":
    api = rest.Api(environment, access_token)
    rates = stream.Stream(environment, access_token, True)
    events = stream.Stream(environment, access_token, False)
    main()
