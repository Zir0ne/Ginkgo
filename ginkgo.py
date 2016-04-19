"""
    Ginkgo是一个基于Oanda的REST API的自动交易系统. 基本的交易操作基于官方发布的python接口.
"""

import oandapy
from account import Account

environment  = "practice"
access_token = "711a43d784751e4df5f7fd0166561667-25503832b893d500f28d5ee691a04505"
account_id   = "1205962"


def main():
    api = oandapy.API(environment=environment, access_token=access_token)
    my_account = Account(api, account_id)

    pass


if __name__ == "__main__":
    main()
