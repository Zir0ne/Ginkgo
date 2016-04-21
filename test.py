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
            print('id: {0:d}\nname: {1:s}\ncurrency: {2:s}\nmargin_rate: {3:f}'.\
                format(account['accountId'], account['accountName'], account['accountCurrency'], account['marginRate']))

    # 启动实时汇率获取
    rates.start(accountId=account_id, instruments='AUD_CAD')
    time.sleep(5)

    # 关闭api函数工作线程
    api.deinit()
    # 关闭实时汇率获取线程
    rates.stop()


if __name__ == "__main__":
    api = rest.Api(environment, access_token)
    rates = stream.Stream(environment, access_token, True)
    events = stream.Stream(environment, access_token, False)
    main()
