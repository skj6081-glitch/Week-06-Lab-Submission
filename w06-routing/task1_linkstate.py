#!/usr/bin/env python3
import argparse
import heapq

TOPOLOGY = {
    "u": {"v": 2, "w": 5, "x": 1},
    "v": {"u": 2, "w": 3, "x": 2},
    "w": {"u": 5, "v": 3, "x": 3, "y": 1, "z": 5},
    "x": {"u": 1, "v": 2, "w": 3, "y": 1},
    "y": {"w": 1, "x": 1, "z": 2},
    "z": {"w": 5, "y": 2},
}

def dijkstra(graph, source):
    costs = {source: 0}
    pq = [(0, source)]
    while pq:
        curr_cost, u = heapq.heappop(pq)
        if curr_cost > costs.get(u, float('inf')):
            continue
        for v, weight in graph.get(u, {}).items():
            new_cost = curr_cost + weight
            if new_cost < costs.get(v, float('inf')):
                costs[v] = new_cost
                heapq.heappush(pq, (new_cost, v))
    costs.pop(source, None)
    return costs

def forwarding_table(graph, source):
    costs = {source: 0}
    first_hops = {}
    pq = [(0, source, None)]
    while pq:
        curr_cost, u, f_hop = heapq.heappop(pq)
        if curr_cost > costs.get(u, float('inf')):
            continue
        for v, weight in graph.get(u, {}).items():
            new_cost = curr_cost + weight
            new_f_hop = v if u == source else f_hop
            if new_cost < costs.get(v, float('inf')):
                costs[v] = new_cost
                first_hops[v] = new_f_hop
                heapq.heappush(pq, (new_cost, v, new_f_hop))
            elif new_cost == costs.get(v, float('inf')):
                if new_f_hop < first_hops[v]:
                    first_hops[v] = new_f_hop
                    heapq.heappush(pq, (new_cost, v, new_f_hop))
    return first_hops

def link_down(graph, a, b):
    g = {n: dict(e) for n, e in graph.items()}
    g[a].pop(b, None)
    g[b].pop(a, None)
    return g

EXPECTED_COST_U = {"v": 2, "w": 3, "x": 1, "y": 2, "z": 4}
EXPECTED_TABLE_U = {"v": "v", "w": "x", "x": "x", "y": "x", "z": "x"}

def verify():
    fails = 0
    try:
        cost = dijkstra(TOPOLOGY, "u")
    except NotImplementedError:
        print("  dijkstra is still a stub"); return 1
    ok = cost == EXPECTED_COST_U
    print(f"  {'ok  ' if ok else 'FAIL'}  costs from u: {cost}")
    if not ok: print(f"        expected {EXPECTED_COST_U}")
    fails += not ok

    try:
        table = forwarding_table(TOPOLOGY, "u")
    except NotImplementedError:
        print("  forwarding_table is still a stub"); return 1
    ok = table == EXPECTED_TABLE_U
    print(f"  {'ok  ' if ok else 'FAIL'}  table at u:  {table}")
    if not ok: print(f"        expected {EXPECTED_TABLE_U}")
    fails += not ok

    for n in TOPOLOGY:
        t = forwarding_table(TOPOLOGY, n)
        missing = set(TOPOLOGY) - {n} - set(t)
        bad = [d for d, h in t.items() if h not in TOPOLOGY[n]]
        ok = not missing and not bad
        print(f"  {'ok  ' if ok else 'FAIL'}  table at {n} covers all, hops are neighbours" + (f"  missing={missing} bad={bad}" if not ok else ""))
        fails += not ok

    cut = link_down(TOPOLOGY, "u", "x")
    after = forwarding_table(cut, "u")
    ok = after != table
    print(f"  {'ok  ' if ok else 'FAIL'}  u reroutes when u-x goes down: {after}")
    fails += not ok
    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
