#!/usr/bin/env python
# -*- coding: utf-8 -*-

TESTING = True

MASTER_DATABASE_URI = 'postgresql://localhost/postgres'
TEST_DATABASE_NAME = 'navigator_test'

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/{}'.format(TEST_DATABASE_NAME)
SQLALCHEMY_POOL_SIZE = 1
