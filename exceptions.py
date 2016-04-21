#! /usr/bin/env python


class OandaError(Exception):
    """ Generic error class, catches oanda response errors """
    def __init__(self, error_response):
        self.error_response = error_response
        msg = 'Oanda API returned error code {0} - {1}'.format(error_response['code'], error_response['message'])
        super(OandaError, self).__init__(msg)


class BadEnvironment(Exception):
    """ Environment should be: sandbox, practice or live. """
    def __init__(self, environment):
        msg = "Environment \'{0}\' does not exist".format(environment)
        super(BadEnvironment, self).__init__(msg)
