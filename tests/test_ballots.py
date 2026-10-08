import ast
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import pytest

START = int(datetime(2026, 10, 7, 12, tzinfo=timezone.utc).timestamp())
URL = "https://raw.githubusercontent.com/publisher/preferences/" + "a" * 40 + "/ballot.txt"
TEXT = "Portability is least preferred. Reliability is preferred to Affordability."
CHOICES = "Reliability;Affordability;Portability"


def addr(value):
    return "0x" + value.hex() if isinstance(value, bytes) else str(value)


def warp(vm, value):
    vm.warp(value)
    # gltest 0.29.2 refreshes sender fields, not raw datetime, after deployment.
    # Native GenVM provides a fresh raw message per transaction.
    from genlayer import gl
    gl.message_raw["datetime"] = value


def mock(vm, order=None, uncertain=False, text=TEXT, status=200):
    vm.clear_mocks()
    raw = text.encode() if isinstance(text, str) else text
    vm.mock_web(r".*ballot\.txt", {"status": status, "body": raw})
    vm.mock_llm(r"(?s).*Interpret the voter's public preference document.*",
                json.dumps({"order": [0, 1, 2] if order is None else order, "uncertain": uncertain}))
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def contract(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-07T12:00:00Z")
    return direct_deploy("contracts/SourceRankedBallotBox.py")


def open_poll(contract, creator, voters=None, name="demo", deadline=START + 3600):
    contract.open_poll(name, CHOICES, ",".join(addr(v) for v in (voters or [creator])), deadline)
    return contract.poll_key(addr(creator), name)


@pytest.fixture
def helpers():
    tree = ast.parse(Path("contracts/SourceRankedBallotBox.py").read_text())
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
                ("canonical", "digest", "parse_order", "equivalent", "add_order", "strongest_paths", "source_allowed")]
    namespace = {"hashlib": hashlib, "json": json, "re": __import__("re")}
    exec(compile(ast.Module(body=selected, type_ignores=[]), "actual_contract_helpers", "exec"), namespace)
    return namespace


def test_counted_semantic_ranking_and_result(contract, direct_vm, direct_alice, helpers):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm)
    contract.cast_source(key, "one", URL, source_hash)
    ballot = contract.get_ballot(key, addr(direct_alice))
    assert ballot["state"] == "COUNTED" and ballot["order"] == [0, 1, 2]
    assert ballot["spec"]["poll"] == key
    contract.finalize(key)
    result = contract.get_poll(key)["result"]
    assert result["state"] == "DECIDED" and result["winners"] == ["Reliability"]
    assert result["matrix"] == [[0, 1, 1], [0, 0, 1], [0, 0, 0]]
    root, payload = result["root"], {k: v for k, v in result.items() if k != "root"}
    assert root == helpers["digest"](payload)


def test_semantics_change_tally_not_just_format(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm, [2, 1, 0], text="Portability first, then Affordability, then Reliability.")
    contract.cast_source(key, "one", URL, source_hash)
    contract.finalize(key)
    result = contract.get_poll(key)["result"]
    assert result["winners"] == ["Portability"]
    assert result["matrix"][2][0] == 1 and result["matrix"][0][2] == 0


def test_ambiguity_terminal_abstention_not_invented_order(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm, [], True)
    contract.cast_source(key, "one", URL, source_hash)
    assert contract.get_ballot(key, addr(direct_alice))["state"] == "ABSTAINED"
    with direct_vm.expect_revert("voter slot spent"):
        contract.cast_source(key, "resample", URL, source_hash)
    contract.finalize(key)
    result = contract.get_poll(key)["result"]
    assert result["state"] == "EMPTY" and result["winners"] == []
    assert len(result["abstained"]) == 1 and result["counted"] == []


def test_wrong_hash_withheld_retry_does_not_count(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm)
    contract.cast_source(key, "bad", URL, "b" * 64)
    attempt = contract.get_attempt(key, addr(direct_alice), "bad")
    assert attempt["state"] == "WITHHELD" and attempt["reason"] == "HASH_MISMATCH"
    assert contract.get_poll(key)["processed"] == 0
    with direct_vm.expect_revert("no terminal ballot"):
        contract.get_ballot(key, addr(direct_alice))
    contract.cast_source(key, "correct", URL, source_hash)
    assert contract.get_poll(key)["counted"] == 1


def test_attempt_replay_and_retry_limit(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    mock(direct_vm)
    contract.cast_source(key, "bad", URL, "b" * 64)
    with direct_vm.expect_revert("spent attempt"):
        contract.cast_source(key, "bad", URL, "b" * 64)
    for i in range(3):
        contract.cast_source(key, "more" + str(i), URL, "b" * 64)
    with direct_vm.expect_revert("retry limit"):
        contract.cast_source(key, "fifth", URL, "b" * 64)


def test_voter_replay_preserves_tally(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm)
    contract.cast_source(key, "one", URL, source_hash)
    with direct_vm.expect_revert("voter slot spent"):
        contract.cast_source(key, "two", URL, source_hash)
    assert contract.get_poll(key)["counted"] == 1


def test_cross_poll_authorization_and_namespaces(contract, direct_vm, direct_alice, direct_bob):
    first = open_poll(contract, direct_alice, [direct_alice], "first")
    second = open_poll(contract, direct_alice, [direct_bob], "second")
    source_hash = mock(direct_vm)
    contract.cast_source(first, "same", URL, source_hash)
    with direct_vm.expect_revert("voter not eligible"):
        contract.cast_source(second, "same", URL, source_hash)
    assert contract.get_poll(second)["counted"] == 0
    direct_vm.sender = direct_bob
    contract.cast_source(second, "same", URL, source_hash)
    assert contract.get_ballot(second, addr(direct_bob))["spec"]["poll"] == second
    assert contract.get_ballot(first, addr(direct_alice))["spec"]["poll"] == first


def test_closure_no_creator_veto_and_missing_voters(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    key = open_poll(contract, direct_alice, [direct_alice, direct_bob])
    source_hash = mock(direct_vm)
    contract.cast_source(key, "one", URL, source_hash)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("waiting for voters"):
        contract.finalize(key)
    warp(direct_vm, "2026-10-07T13:00:00Z")
    contract.finalize(key)
    result = contract.get_poll(key)["result"]
    assert result["winners"] == ["Reliability"] and len(result["missing"]) == 1
    with direct_vm.expect_revert("terminal poll"):
        contract.finalize(key)
    with direct_vm.expect_revert("poll closed"):
        contract.cast_source(key, "late", URL, source_hash)


def test_exact_deadline_rejects_vote_and_allows_empty_close(contract, direct_vm, direct_alice):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm)
    warp(direct_vm, "2026-10-07T13:00:00Z")
    with direct_vm.expect_revert("poll closed"):
        contract.cast_source(key, "late", URL, source_hash)
    contract.finalize(key)
    assert contract.get_poll(key)["state"] == "EMPTY"


def test_pairwise_tie_kept_without_arbitrary_winner(contract, direct_vm, direct_alice, direct_bob):
    key = open_poll(contract, direct_alice, [direct_alice, direct_bob])
    source_hash = mock(direct_vm)
    contract.cast_source(key, "one", URL, source_hash)
    direct_vm.sender = direct_bob
    source_hash = mock(direct_vm, [1, 0, 2])
    contract.cast_source(key, "one", URL, source_hash)
    contract.finalize(key)
    result = contract.get_poll(key)["result"]
    assert result["state"] == "TIED" and result["winner_indices"] == [0, 1]


def test_majority_cycle_uses_indirect_paths(helpers):
    matrix = [[0, 3, 1], [2, 0, 4], [4, 1, 0]]
    paths, winners = helpers["strongest_paths"](matrix)
    assert paths[1][0] == 4 and paths[0][1] == 3
    assert winners == [1]


def test_consensus_comparison_rejects_rank_state_binding_and_hash_disagreement(helpers):
    report = {"order": [0, 1, 2], "uncertain": False, "state": "COUNTED", "hash": "a" * 64, "poll": "one"}
    assert helpers["equivalent"](report, report)
    for field, replacement in [("order", [1, 0, 2]), ("uncertain", True), ("state", "ABSTAINED"), ("hash", "b" * 64), ("poll", "two")]:
        assert not helpers["equivalent"](report, {**report, field: replacement})


@pytest.mark.parametrize("order,uncertain", [([0, 0, 2], False), ([0, 1], False), ([0, 1, 3], False), ([False, 1, 2], False), ([0, 1, 2], "false"), ([0, 1, 2], True)])
def test_malformed_model_vector_does_not_count(contract, direct_vm, direct_alice, order, uncertain):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm, order, uncertain)
    with direct_vm.expect_revert("malformed ranking"):
        contract.cast_source(key, "one", URL, source_hash)
    assert contract.get_poll(key)["counted"] == 0


@pytest.mark.parametrize("text,status,reason", [("error", 404, "HTTP_ERROR"), (b"\xff", 200, "INVALID_UTF8"), ("x" * 8193, 200, "SOURCE_SIZE"), ("", 200, "SOURCE_SIZE"), ("x\x00", 200, "INVALID_TEXT")])
def test_unusable_source_cannot_spend_slot(contract, direct_vm, direct_alice, text, status, reason):
    key = open_poll(contract, direct_alice)
    source_hash = mock(direct_vm, text=text, status=status)
    contract.cast_source(key, "one", URL, source_hash)
    assert contract.get_attempt(key, addr(direct_alice), "one")["reason"] == reason
    assert contract.get_poll(key)["processed"] == 0


@pytest.mark.parametrize("choices", ["OnlyOne", "Same;Same", "Reliability;reliability", " A;BB", "AA;BB;", "AA;BB\n", "A;BB"])
def test_invalid_choices(contract, direct_vm, direct_alice, choices):
    with direct_vm.expect_revert("invalid choices"):
        contract.open_poll("bad", choices, addr(direct_alice), START + 3600)


def test_roster_and_namespace_and_history_roots(contract, direct_vm, direct_alice, direct_bob, helpers):
    with direct_vm.expect_revert("duplicate or zero voter"):
        contract.open_poll("bad", CHOICES, addr(direct_alice) + "," + addr(direct_alice), START + 3600)
    first = open_poll(contract, direct_alice)
    direct_vm.sender = direct_bob
    second = open_poll(contract, direct_bob)
    assert first != second
    for event in contract.history(0, 20):
        assert event["root"] == helpers["digest"]({k: v for k, v in event.items() if k != "root"})
    events = contract.history(0, 20)
    assert events[1]["previous"] == events[0]["root"]


def test_source_restrictions_and_schema(helpers):
    assert helpers["source_allowed"](URL)
    for url in [URL.replace("a" * 40, "main"), URL.replace("https:", "http:"), URL.replace("/ballot.txt", "/../ballot.txt"), "https://127.0.0.1/ballot.txt"]:
        assert not helpers["source_allowed"](url)
    assert helpers["parse_order"]({"order": [], "uncertain": True}, 3) is not None
    assert helpers["parse_order"]({"order": [0, 1, 2], "uncertain": False, "score": 99}, 3) is None


@pytest.mark.parametrize("method", ["open_poll", "cast_source", "finalize"])
def test_native_value_rejected(contract, direct_vm, direct_alice, method):
    key = open_poll(contract, direct_alice)
    direct_vm.value = 1
    with direct_vm.expect_revert("native value not accepted"):
        if method == "open_poll":
            contract.open_poll("funded", CHOICES, addr(direct_alice), START + 3600)
        elif method == "cast_source":
            contract.cast_source(key, "one", URL, "a" * 64)
        else:
            contract.finalize(key)
