import validators
from exception import *


def check_validity_url(func):
    def wrapper(event, url):
        if not validators.url(url):
            raise NotValidityURL('Not a valid URL!')
        return func(event, url)

    return wrapper
