import json
import re

def load_json(s: str):
    s = s.replace('\n', ' ')
    return json.loads(re.sub(r'(\d)\"', r'\1\\"', s), strict=False)