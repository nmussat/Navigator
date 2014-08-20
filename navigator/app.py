#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask

def register_blueprints(app):
    from .navigator import navigator
    app.register_blueprint(navigator, url_prefix='/schemas')

def register_extension(app):
    from .models import db
    db.init_app(app)

def create_app(name):
    app = Flask(name, template_folder='navigator/templates')
    app.config.from_object('settings')
    app.config.from_envvar('APP_SETTINGS')
    register_extension(app)
    register_blueprints(app)
    return app
