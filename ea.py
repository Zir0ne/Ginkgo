#! /usr/bin/env python

import oandapy


class EA(oandapy.Streamer):
    """ 交易策略, 根据汇率实时变化做出响应 """
    def __init__(self, environment, access_token):
        super(EA, self).__init__(environment, access_token)

    def on_success(self, data):
        """ Called when data is successfully retrieved from the stream
            Override this to handle your streaming data.
            :param data: response object sent from stream
        """
        return True

    def on_error(self, data):
        """ Called when stream returns non-200 status code
            Override this to handle your streaming data.
            :param data: error response object sent from stream
        """
        return
