#!/usr/bin/env python3

from sqlalchemy import create_engine
import datetime

from flask import Flask
app = Flask(__name__)


@app.route("/")
def customizingThis():
    return ('I am default')

@app.route("/pnl")
def PNL():
    fileStr = open('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/log/pnl.html', 'r').read()
    return (fileStr)

@app.route("/pnl_dummy")
def PNL_DUMMY():
    fileStr = open('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/log/pnl_dummy.html', 'r').read()
    return (fileStr)

if __name__ == '__main__':
    app.run()

