import pick_strategies as ps


def test_seeded_pick_is_reproducible_and_distinct(capsys):
    ps.main(["pick", "--format", "headline", "--n", "3", "--seed", "abc", "--voice", "none"])
    first = capsys.readouterr().out
    ps.main(["pick", "--format", "headline", "--n", "3", "--seed", "abc", "--voice", "none"])
    assert first == capsys.readouterr().out
    ids = [ln.split(":")[0].strip("- ").strip() for ln in first.splitlines() if ln.startswith("- ")]
    assert len(ids) == 3 and len(set(ids)) == 3


def test_required_strategy_is_included(capsys):
    ps.main(["pick", "--format", "cta", "--n", "2", "--require", "direct-instruction", "--seed", "x", "--voice", "none"])
    assert "direct-instruction" in capsys.readouterr().out


def test_library_parses():
    lib = ps.load_library()
    assert len(lib) >= 12 and all(s["formats"] for s in lib)
