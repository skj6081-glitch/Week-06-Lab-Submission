#!/usr/bin/env python3
"""Week 6 · does your work pass?"""
import argparse, importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results = []


def record(task, name, status, detail=""):
    results.append((task, name, status, detail))
    print({PASS: "  ok  ", FAIL: " FAIL ", SKIP: " skip "}[status]
          + f" [{task}] {name}" + (f"  - {detail}" if detail else ""))


def test_task1():
    try:
        m = importlib.import_module("task1_linkstate")
    except Exception as e:
        return record(1, "task1_linkstate.py imports", FAIL, repr(e))
    src = open(os.path.join(HERE, "task1_linkstate.py"), encoding="utf-8").read()
    record(1, "R6 no networkx", FAIL if "import networkx" in src else PASS)
    try:
        rc = m.verify()
    except Exception as e:
        return record(1, "verify runs", FAIL, repr(e))
    record(1, "all checks", PASS if rc == 0 else FAIL)


def test_task2():
    needed = {
        "traceroute.txt": "A1 three traceroutes",
        "route-before.txt": "B1 tables before the cut",
        "route-after.txt": "B3 tables after the cut",
        "reconverge.txt": "B4 measured reconvergence time",
    }
    for fname, label in needed.items():
        path = os.path.join(OUT, fname)
        if not os.path.exists(path):
            record(2, label, FAIL, f"out/{fname} missing")
            continue
        size = os.path.getsize(path)
        record(2, label, PASS if size > 0 else FAIL, f"{size:,} bytes")

    tr = os.path.join(OUT, "traceroute.txt")
    if os.path.exists(tr):
        text = open(tr, encoding="utf-8", errors="replace").read()
        hops = sum(1 for l in text.splitlines() if l.strip()[:2].strip().isdigit())
        record(2, "traceroute output has hops", PASS if hops >= 3 else FAIL,
               f"{hops} hop lines")


def test_task3():
    try:
        bench = importlib.import_module("bench")
        T = importlib.import_module("task3_reconverge")
    except Exception as e:
        return record(3, "modules import", FAIL, repr(e))
    graph, events = bench.build()
    base = bench.run(T.FullRecompute, "baseline", graph, events)
    try:
        mine = bench.run(T.YourRouter, "yours", graph, events, check=True)
    except NotImplementedError:
        return record(3, "YourRouter implemented", FAIL, "still a stub")
    except Exception as e:
        return record(3, "YourRouter runs", FAIL, repr(e))
    record(3, "R3 table correct after every event",
           PASS if mine["wrong"] == 0 else FAIL, f"{mine['wrong']} wrong")
    saved = 1 - mine["spf"] / base["spf"]
    record(3, "R4 fewer SPF runs", PASS if saved > 0.05 else FAIL,
           f"{saved:.0%} avoided")
    record(3, "R5 wall-time argument in observation.md", SKIP, "graded by a human")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, choices=[1, 2, 3])
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for n, fn in [(1, test_task1), (2, test_task2), (3, test_task3)]:
        if a.task in (None, n):
            print(f"\n=== Task {n}")
            fn()
    print()
    failed = sum(1 for *_, s, _ in results if s == FAIL)
    skipped = sum(1 for *_, s, _ in results if s == SKIP)
    print(f"  {len(results) - failed - skipped} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
