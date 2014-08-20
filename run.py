#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from navigator.app import create_app

if __name__ == '__main__':
    app = create_app(__name__)
    app.run(debug=True)
