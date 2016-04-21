#! /usr/bin/env python

import json
import requests
import threading
from exceptions import BadEnvironment


class Stream:
    """ Provides functionality for HTTPS streaming
        User should provide two callback function to receive streaming data or error information
    """
    def __init__(self, environment, access_token, rates_stream):
        """ Instantiates an instance of Oanda streaming API wrapper """
        if environment == 'practice':
            self.api_url = 'https://stream-fxpractice.oanda.com'
        elif environment == 'live':
            self.api_url = 'https://stream-fxtrade.oanda.com'
        else:
            raise BadEnvironment(environment)

        self.access_token = access_token
        self.client = requests.Session()
        self.client.stream = True
        self.rates_stream = rates_stream
        self.connected = False
        self.thread = None

        if self.access_token:
            self.client.headers['Authorization'] = 'Bearer ' + self.access_token

    def start(self, on_stream=None, on_error=None, **params):
        """ Open a streaming connection to receive real time market prices for specified instruments, or events depend
            on rates_stream True or False
            :param on_stream: [Optional] Callback function, invoked when new rate coming
            :param on_error: [Optional] Callback function, invoked when error occur
            :param params: Docs: http://developer.oanda.com/rest-live/streaming
        """
        self.connected = True
        self.thread = threading.Thread(target=self.__thread,
                                       args=('v1/prices' if self.rates_stream else 'v1/events', on_stream, on_error),
                                       kwargs=params)
        self.thread.start()

    def stop(self):
        """ Close streaming """
        if self.thread and self.connected:
            self.connected = False
            self.thread.join()

    def __thread(self, endpoint, on_stream, on_error, **params):
        """ Starts the stream with the given parameters
            :param endpoint: [Required] 'v1/prices' or 'v1/events'
            :param on_stream: [Optional] invoked when new stream data coming
            :param on_error: [Optional] invoked when error occur
            :param ignore_heartbeat: [Optional] Whether or not to display the heartbeat. Default: True
        """
        on_stream_func = on_stream if on_stream else self.__on_stream
        on_error_func = on_error if on_error else self.__on_error
        params = params or dict()
        ignore_heartbeat = None
        if 'ignore_heartbeat' in params:
            ignore_heartbeat = params['ignore_heartbeat']
        requests_args = dict()
        requests_args['params'] = params
        url = '{0}/{1}'.format(self.api_url, endpoint)

        while self.connected:
            response = self.client.get(url, **requests_args)
            if response.status_code != 200:
                on_error_func(str(response.content))
            else:
                for line in response.iter_lines(90):
                    if not self.connected:
                        break
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if not (ignore_heartbeat and 'heartbeat' in data):
                            on_stream_func(data)

    def __on_stream(self, data):
        """ Default streaming data handler. Used when user doesn't provide one instead """
        print((' rates: ' if self.rates_stream else 'events: ') + str(data))

    def __on_error(self, error_str):
        """ Default streaming error handler. Used when user doesn't provide one instead """
        print((' rates error: ' if self.rates_stream else 'events error: ') + error_str)
