from sys import exc_info
from traceback import format_tb, format_exception_only, format_stack


def format_exception(e):
    exception_list = format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(format_tb(exc_info()[2]))
    exception_list.extend(format_exception_only(exc_info()[0], exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str
