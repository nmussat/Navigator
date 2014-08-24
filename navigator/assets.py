#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask.ext.assets import Environment, Bundle

assets = Environment()

js = [
    'vendors/jQuery/jquery-2.1.1.js',
    'vendors/jQuery/jquery.hotkeys.js',
    'vendors/Bootstrap/bootstrap.js',
    'vendors/Bootstrap/bootstrap3-typeahead.min.js',
    'vendors/CodeMirror/codemirror.js',
]
assets.register('js', Bundle(*js, output='build/main.js'))

css = [
    'vendors/Bootstrap/bootstrap.css',
    'vendors/CodeMirror/codemirror.css',
    'css/main.css',
]
assets.register('css', Bundle(*css, filters='less,cssmin', output='build/main.css'))
