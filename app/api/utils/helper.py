# -*- coding: utf-8 -*-


def valid_int(param):
    try:
        p = int(param)
    except (ValueError, TypeError):
        raise ValueError("expect a number but {} given".format(type(param)))

    return p
