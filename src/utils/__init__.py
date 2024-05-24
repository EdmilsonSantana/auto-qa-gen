import json
import os
from typing import Any
import logging
import sys


def load_json(s: str) -> Any:
    return json.loads(s.replace('\n', ' '), strict=False)


def save_json(file: str, data: list[object], append=False):
    if (append and os.path.isfile(file)):
        data.extend(read_json(file))

    with open(file, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False,
                  default=lambda obj: obj.__dict__)


def read_json(file: str) -> Any:
    with open(file, 'r', encoding='utf-8') as fp:
        return json.load(fp)


def chunker(seq: list, size: int):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def config_log() -> logging.Logger:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root.addHandler(handler)

    return root
