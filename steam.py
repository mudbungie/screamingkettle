#!/usr/bin/python3

# takes a single argument from the command line, which is a shell command
# executes that command upon HTTP request, posts the output as the response
# you'll usually want to enclose the command in quotes to make it a single
# argument.

from bottle import route, run
from sys import argv
from subprocess import check_output

@route('/')
def index():
    command = argv[2].split()
    response = check_output((command)).decode()

    return response

serverPort = argv[1]
run(host='0.0.0.0', port=serverPort)
