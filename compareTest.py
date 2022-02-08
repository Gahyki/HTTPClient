import json

# Opening JSON file
f1 = open("outputHttpc.json")
f2 = open("outputCurl.json")

httpc_out = json.load(f1)
curl_out = json.load(f2)

if httpc_out["args"]:
    for k, v in httpc_out["args"].items():
        print(f"TEST COMPARE ARGS {k} EQUALS")
        print(v == curl_out["args"][k])

if "files" in httpc_out and httpc_out["files"]:
    print("TEST COMPARE FILES EQUALS")
    print(httpc_out["files"] == curl_out["files"])

if "data" in httpc_out and httpc_out["data"]:
    print("TEST COMPARE DATA EQUALS")
    print(httpc_out["data"] == curl_out["data"])

for k, v in httpc_out["headers"].items():
    if k in ["Content-Length", "Content-Type", "X-Amzn-Trace-Id"]:
        continue
    print(f"TEST COMPARE HEADER {k} EQUALS")
    print(v == curl_out["headers"][k])

print("TEST COMPARE URL EQUALS")
print(httpc_out["url"] == curl_out["url"])

# Closing file
f1.close()
f2.close()
