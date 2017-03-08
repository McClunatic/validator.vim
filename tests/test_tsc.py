import json
from lints.typescript import Tsc


def test_tsc():
    msg = ["src/app/test_file(29,9): error TS1005: ',' expected."]

    tsc = Tsc()
    print tsc.filename
    res = Tsc().parse_loclist(msg, 1)
    print 'res:', res
    assert json.loads(res)[0] == {
        "lnum": "29",
        "col": "9",
        "enum": 1,
        "bufnr": 1,
        "type": "E",
        "error": "error TS1005",
        "text": "[tsc]',' expected.",
    }
