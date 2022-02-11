#!/usr/bin/env python3

import random, string
from urllib import parse
import socket
import argparse
import sys


# -------------------- Helper Methods ------------------------
def deconstruct_url(url):
    parsed_url = parse.urlsplit(url)
    host = parsed_url.netloc
    path = parsed_url.path if parsed_url.path else "/"
    query = f"?{parsed_url.query}" if parsed_url.query else ""
    return host, path, query


def get_file_data(file):
    boundary = "--------------------------" + "".join(
        random.choices(string.digits, k=24)
    )
    file = open(file, "r")
    file_str = file.read()
    data = "--" + boundary + "\r\n"
    data += f'Content-Disposition: form-data; name="null"; filename="{file.name}"\r\n'
    data += "Content-Type: text/plain\r\n\r\n"
    data += file_str + "\r\n"
    data += "--" + boundary + "--"
    content_length = len(data) + 2
    file.close()
    return boundary, content_length, data


def output(response, verbose, file=None):
    result = response if verbose else response[response.index("\r\n\r\n") + 4 :]
    if file:
        try:
            f = open(file, "w")
            f.write(result)
        except:
            print("There was an error outputting into file.")
            print(result)
        finally:
            f.close()
    else:
        print(result)


def get_response_code(response):
    status = int(response.split()[1])
    return status


def get_new_location(response):
    res = response.split()
    idx = res.index("location:")
    location = res[idx + 1]
    return location


def send_request(
    host, port, encoded_text, verbose, filename, path, query, method, redirect
):
    for _ in range(10):
        # Setting up socket for TCP connection
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Attempt to connect at port 80
            conn.connect((host, port))
            request = str.encode(f"{method} {path}{query} HTTP/1.1\r\n" + encoded_text)
            # Send request
            conn.send(request)
            # Get http response and print according to verbose settings
            response = conn.recv(100000)
            response = response.decode("utf-8")
            status_code = get_response_code(response)
            if redirect and status_code == 302:
                path = get_new_location(response)
            else:
                output(response, verbose, filename)
                break
        finally:
            # Close TCP connection
            conn.close()


# -------------------- Request Methods ------------------------
def run_get(verbose, header, url, filename, redirect):
    # Deconstructing url to get required data
    host, path, query = deconstruct_url(url)
    # Assemble header(s) and text
    header_str = "\r\n".join([": ".join(h.split(":")) for h in header]) + "\r\n"
    string_to_send = f"Host: {host}\r\nConnection: close\r\n{header_str}\r\n\r\n"
    # Send request
    send_request(
        host, 80, string_to_send, verbose, filename, path, query, "GET", redirect
    )


def run_post(verbose, header, data, file, url, filename, redirect):
    # Deconstructing url
    host, path, query = deconstruct_url(url)
    # Assembling request data
    content_length = 0
    content_type = ""
    if data:
        content_length = len(data)
        content_type = "application/json"
    if file:
        boundary, content_length, data = get_file_data(file)
        content_type = f"multipart/form-data; boundary={boundary}"
    header_str = "\r\n".join([": ".join(h.split(":")) for h in header]) + "\r\n"
    string_to_send = f"Host: {host}\r\n{header_str}Connection: close\r\nContent-Length: {content_length}\r\nContent-Type: {content_type}\r\n\r\n{data}\r\n"
    # Send request
    send_request(
        host, 80, string_to_send, verbose, filename, path, query, "POST", redirect
    )


# -------------------- Main Method ------------------------
def run():
    cmdargs = list(sys.argv)
    argslen = len(cmdargs)

    if argslen < 1:
        print("Missing arguments. Run [help] for usage")
        return

    if cmdargs[1] == "help":
        if argslen > 2 and cmdargs[2] == "get":
            print(
                """httpc help get

usage: httpc get [-v] [-h key:value] URL

Get executes a HTTP GET request for a given URL.
    -v Prints the detail of the response such as protocol, status, and headers.
    -h key:value Associates headers to HTTP Request with the format 'key:value'.
            """
            )

        elif argslen > 2 and cmdargs[2] == "post":
            print(
                """httpc help post

usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL

Post executes a HTTP POST request for a given URL with inline data or from file.
    -v Prints the detail of the response such as protocol, status, and headers.
    -h key:value Associates headers to HTTP Request with the format 'key:value'.
    -d string Associates an inline data to the body HTTP POST request.
    -f file Associates the content of a file to the body HTTP POST request.
Either [-d] or [-f] can be used but not both.
            """
            )
        else:
            print(
                """httpc help

httpc is a curl-like application but supports HTTP protocol only.
Usage:
    httpc command [arguments]
The commands are:
    get executes a HTTP GET request and prints the response.
    post executes a HTTP POST request and prints the response.
    help prints this screen.

Use "httpc help [command]" for more information about a command.
            """
            )
        return

    parser = argparse.ArgumentParser(
        add_help=False,
        description="httpc is a curl-like application but supports HTTP protocol only.",
    )
    parser.add_argument("request", choices=["get", "post"])
    parser.add_argument(
        "-v",
        help="Prints the detail of the response such as protocol, status, and headers.",
        action="store_true",
        default=False,
        required=False,
    )
    parser.add_argument(
        "-h",
        help="key:value Associates headers to HTTP Request with the format 'key:value'.",
        action="append",
        default=[],
        required=False,
    )
    parser.add_argument(
        "-r",
        help="Specify if we want to redirect or not",
        action="store_false",
        default=True,
        required=False,
    )
    parser.add_argument("url")
    parser.add_argument(
        "-o",
        help="Specify the filename where the HTTP client will write the body of the response",
        default=None,
        required=False,
    )
    if cmdargs[1] == "get":
        args = parser.parse_args()
        run_get(args.v, args.h, args.url, args.o, args.r)

    elif cmdargs[1] == "post":
        action = parser.add_mutually_exclusive_group(required=False)
        action.add_argument(
            "-d",
            help="Associates an inline data to the body HTTP POST request.",
            required=False,
        )
        action.add_argument(
            "-f",
            help="Associates the content of a file to the body HTTP POST request.",
            required=False,
        )
        args = parser.parse_args()
        run_post(args.v, args.h, args.d, args.f, args.url, args.o, args.r)

    else:
        print("Missing arguments. Run [help] for usage")
        return


if __name__ == "__main__":
    run()
