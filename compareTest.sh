#!/usr/bin/bash

# Compare Post with file
python3 httpc.py post -h email:123@gmail.com -h password:1234 -f "test.txt" http://httpbin.org/post > outputHttpc.json
curl --location --request POST 'http://httpbin.org/post' --header 'email: 123@gmail.com' --header 'password: 1234' --header 'Connection: close' --form '=@"/home/phong/HTTPClient/test.txt"' > outputCurl.json
python3 compareTest.py

# Compare Post with data
python3 httpc.py post -h email:123@gmail.com -h password:1234 -d "Hello World!" http://httpbin.org/post > outputHttpc.json
curl --location --request POST 'http://httpbin.org/post' --header 'content-type: application/json' --header 'email: 123@gmail.com' --header 'password: 1234' --header 'Connection: close' --data-raw 'Hello World!' > outputCurl.json
python3 compareTest.py

# Compare Get
python3 httpc.py get "http://httpbin.org/get?course=networking&assignment=1%27" > outputHttpc.json
curl --location --request GET 'http://httpbin.org/get?course=networking&assignment=1%27' > outputCurl.json
python3 compareTest.py

# Delete output files
rm outputHttpc.json
rm outputCurl.json
