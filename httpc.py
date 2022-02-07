#!/usr/bin/env python3

from urllib import parse
import socket
import argparse
import sys


def run_get(verbose, header, url):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parsed_url = parse.urlsplit(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else '/'
    query = f"?{parsed_url.query}" if parsed_url.query else ''
    header_str = '\r\n'.join([': '.join(h.split(':')) for h in header]) + '\r\n'
    try:
        conn.connect((host, 80))
        request = str.encode(f"GET {path}{query} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n{header_str}\r\n\r\n")
        conn.send(request)
        response = conn.recv(10000)
        response = response.decode("utf-8")
        if verbose:
            print(response)
        else:
            print(response[response.index('\r\n\r\n')+4:])

    finally:
        conn.close()

def run_post(verbose, header, data, file, url):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parsed_url = parse.urlsplit(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else '/'
    query = f"?{parsed_url.query}" if parsed_url.query else ''
    content_lenght = len(data)
    header_str = '\r\n'.join([': '.join(h.split(':')) for h in header]) + '\r\n'
    try:
        conn.connect((host, 80))
        request = str.encode(f"POST {path}{query} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nContent-Length: {content_lenght}\r\n{header_str}\r\n{data}\r\n\r\n")
        print(request)
        conn.send(request)
        response = conn.recv(10000)
        response = response.decode("utf-8")
        if verbose:
            print(response)
        else:
            print(response[response.index('\r\n\r\n')+4:])
    finally:
        conn.close()

def run_client(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((host, port))
        print("Type any thing then ENTER. Press Ctrl+C to terminate")
        while True:
            line = sys.stdin.readline(1024)
            request = line.encode("utf-8")
            conn.sendall(request)
            # MSG_WAITALL waits for full request or error
            response = conn.recv(len(request), socket.MSG_WAITALL)
            sys.stdout.write("Replied: " + response.decode("utf-8"))
    finally:
        conn.close()

def run():
    cmdargs = list(sys.argv)
    argslen = len(cmdargs)

    if argslen < 1:
        print("Missing arguments. Run [help] for usage")
        return

    if cmdargs[1] == "help":
        if argslen > 2 and cmdargs[2] == "get":
            print("""httpc help get

usage: httpc get [-v] [-h key:value] URL

Get executes a HTTP GET request for a given URL.
    -v Prints the detail of the response such as protocol, status, and headers.
    -h key:value Associates headers to HTTP Request with the format 'key:value'.
            """)
        
        elif argslen > 2 and cmdargs[2] == "post":
            print("""httpc help post

usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL

Post executes a HTTP POST request for a given URL with inline data or from file.
    -v Prints the detail of the response such as protocol, status, and headers.
    -h key:value Associates headers to HTTP Request with the format 'key:value'.
    -d string Associates an inline data to the body HTTP POST request.
    -f file Associates the content of a file to the body HTTP POST request.
Either [-d] or [-f] can be used but not both.
            """)
        else:
            print("""httpc help

httpc is a curl-like application but supports HTTP protocol only.
Usage:
    httpc command [arguments]
The commands are:
    get executes a HTTP GET request and prints the response.
    post executes a HTTP POST request and prints the response.
    help prints this screen.

Use "httpc help [command]" for more information about a command.
            """)
        return

    parser = argparse.ArgumentParser(add_help=False,
                                     description="httpc is a curl-like application but supports HTTP protocol only.")
    parser.add_argument('request', choices=['get', 'post'])
    parser.add_argument("-v", help="Prints the detail of the response such as protocol, status, and headers.",
                        action='store_true', default=False, required=False)
    parser.add_argument("-h", help="key:value Associates headers to HTTP Request with the format 'key:value'.",
                        action='append', default=[], required=False)
    parser.add_argument('url')

    if cmdargs[1] == "get":
        args = parser.parse_args()
        run_get(args.v, args.h, args.url)


    elif cmdargs[1] == "post":
        action = parser.add_mutually_exclusive_group(required=False)
        action.add_argument('-d', help="Associates an inline data to the body HTTP POST request.", required=False)
        action.add_argument('-f', help="Associates the content of a file to the body HTTP POST request.",
                            required=False)

        args = parser.parse_args()

        print(args.v)
        print(args.h)
        print(args.d)
        print(args.f)
        print(args.url)
        print("---------------------------")
        run_post(args.v, args.h, args.d, args.f, args.url)

    else:
        print("Missing arguments. Run [help] for usage")
        return


if __name__ == "__main__":
    run()

# run_client(args.host, args.port)
