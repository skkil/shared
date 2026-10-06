import json

import readability_check as rc


def run(tmp_path, text, *extra, name="d.md"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    code = rc.main(["check", str(f), "--json", *extra])
    return code


def findings(capsys):
    return json.loads(capsys.readouterr().out)["findings"]


def test_english_flags_chat_residue_and_long_sentence(tmp_path, capsys):
    text = ("# Setup\n\nGreat question! " + "This sentence keeps going with many plain words " * 4 + "until it ends.\n")
    assert run(tmp_path, text, "--lang", "en") == 1
    rules = {f["rule"] for f in findings(capsys)}
    assert "sentence-long" in rules
    assert any(r.startswith("banned-en#") for r in rules)


def test_allow_comment_suppresses_a_rule(tmp_path, capsys):
    text = "# Notes\n\nOur robust estimator ignores outliers. <!-- vanessa-allow: banned-en -->\n"
    run(tmp_path, text, "--lang", "en")
    assert not [f for f in findings(capsys) if f["rule"].startswith("banned-en")]


def test_korean_spelling_and_double_passive_fail(tmp_path, capsys):
    text = "# 안내\n\n설정이 저장되요. 이 값은 자동으로 변경되어집니다.\n"
    assert run(tmp_path, text) == 1
    out = findings(capsys)
    assert sum(f["level"] == "FAIL" for f in out) >= 2


def test_korean_register_mix_warns(tmp_path, capsys):
    text = "# 안내\n\n" + "설정을 저장합니다. 파일을 엽니다. " + "버튼을 눌러요. 다시 시도해요. 목록을 봐요.\n"
    run(tmp_path, text)
    assert any(f["rule"] == "ko-register-mix" for f in findings(capsys))


def test_acronym_defined_in_korean_passes(tmp_path, capsys):
    text = "# 연결\n\nSSO(Single Sign-On)를 켜면 한 번만 로그인합니다. SSO는 기본으로 꺼져 있습니다.\n"
    run(tmp_path, text)
    assert not [f for f in findings(capsys) if f["rule"].startswith("acronym")]


def test_voice_config_and_glossary(tmp_path, capsys):
    voice = tmp_path / "voice.md"
    voice.write_text('```vanessa-config\n{"en": {"sentence_words_warn": 5}}\n```\n', encoding="utf-8")
    gloss = tmp_path / "glossary.md"
    gloss.write_text("| Concept | English | Korean | Use | Avoid |\n|---|---|---|---|---|\n| space | workspace | 워크스페이스 | | team room |\n",
                     encoding="utf-8")
    text = "# Spaces\n\nOpen the team room to see every file your team shares today.\n"
    run(tmp_path, text, "--lang", "en", "--voice", str(voice), "--glossary", str(gloss))
    rules = {f["rule"] for f in findings(capsys)}
    assert {"sentence-long", "glossary-avoid"} <= rules


def test_code_and_excerpts_are_skipped(tmp_path, capsys):
    text = ("# Run\n\n```\nGreat question! delve delve\n```\n\n"
            "<details class=\"src-excerpt\"><summary>s</summary>Great question! leverage</details>\n\nRun the job.\n")
    run(tmp_path, text, "--lang", "en")
    assert not [f for f in findings(capsys) if f["rule"].startswith("banned-en")]


def test_store_limits(tmp_path, capsys):
    f = tmp_path / "listing.json"
    f.write_text(json.dumps({"ios": {"name": "A" * 31, "keywords": "receipt, scan"}, "play": {"short": "Fine"}}), encoding="utf-8")
    assert rc.main(["limits", str(f), "--json"]) == 1
    rows = {r["id"]: r for r in json.loads(capsys.readouterr().out)}
    assert rows["ios.name"]["status"] == "FAIL"
    assert rows["ios.keywords"]["status"] == "FAIL"
    assert rows["play.short"]["status"] == "ok"
