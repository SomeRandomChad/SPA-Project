from app.llm.parse import ModelOutputError, parse_rephrase_response


def test_parse_accepts_plain_json():
    s = '{"professional":"a","casual":"b","polite":"c","social":"d"}'
    res = parse_rephrase_response(s)
    assert res.professional == "a"
    assert res.casual == "b"
    assert res.polite == "c"
    assert res.social == "d"


def test_parse_accepts_extra_text_around_json():
    s = 'here you go:\n{"professional":"a","casual":"b","polite":"c","social":"d"}\nthanks'
    res = parse_rephrase_response(s)
    assert res.social == "d"


def test_parse_rejects_missing_keys():
    s = '{"professional":"a"}'
    try:
        parse_rephrase_response(s)
        assert False, "expected ModelOutputError"
    except ModelOutputError:
        pass

def test_parse_rejects_malformed_json():
    s = '{"professional":"a",'
    try:
        parse_rephrase_response(s)
        assert False, "expected ModelOutputError"
    except ModelOutputError:
        pass


def test_parse_accepts_json_in_code_fences():
    s = """```json
{"professional":"a","casual":"b","polite":"c","social":"d"}
```"""
    res = parse_rephrase_response(s)
    assert res.casual == "b"