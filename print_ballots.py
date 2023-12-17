#!/usr/bin/env python3
import json, sys

# Example usage:
with open(sys.argv[1]) as f:
    json_data = json.load(f)
for i in json_data:
    print("- "+json.dumps(i))
