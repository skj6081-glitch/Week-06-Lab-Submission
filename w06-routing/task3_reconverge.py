#!/usr/bin/env python3
import heapq

SPF_RUNS = 0

def dijkstra_table(graph, source):
    global SPF_RUNS
    SPF_RUNS += 1
    best = {source: (0, None)}
    pq, done = [(0, source, None)], set()
    while pq:
        cost, node, first_hop = heapq.heappop(pq)
        if node in done:
            continue
        done.add(node)
        best[node] = (cost, first_hop)
        for nbr, w in sorted(graph[node].items()):
            if nbr in done:
                continue
            hop = nbr if node == source else first_hop
            if cost + w < best.get(nbr, (float("inf"), None))[0]:
                best[nbr] = (cost + w, hop)
                heapq.heappush(pq, (cost + w, nbr, hop))
    return {d: h for d, (_, h) in best.items() if d != source and h}

class FullRecompute:
    def __init__(self, graph, source):
        self.graph = {n: dict(e) for n, e in graph.items()}
        self.source = source
        self.table = dijkstra_table(self.graph, source)

    def link_change(self, a, b, cost):
        if cost is None:
            self.graph[a].pop(b, None)
            self.graph[b].pop(a, None)
        else:
            self.graph[a][b] = cost
            self.graph[b][a] = cost
        self.table = dijkstra_table(self.graph, self.source)

class YourRouter:
    def __init__(self, graph, source):
        self.graph = {n: dict(e) for n, e in graph.items()}
        self.source = source
        self.table = {}
        self.distances = {}
        self.parents = {}
        self._recompute()

    def _recompute(self):
        global SPF_RUNS
        SPF_RUNS += 1
        self.table = {}
        self.distances = {self.source: 0}
        self.parents = {self.source: None}
        pq = [(0, self.source, None, None)]
        done = set()
        while pq:
            cost, node, first_hop, parent = heapq.heappop(pq)
            if node in done:
                continue
            done.add(node)
            if node != self.source:
                self.table[node] = first_hop
                self.distances[node] = cost
                self.parents[node] = parent
            for nbr, w in sorted(self.graph[node].items()):
                if nbr in done:
                    continue
                hop = nbr if node == self.source else first_hop
                if cost + w < self.distances.get(nbr, float("inf")):
                    self.distances[nbr] = cost + w
                    self.parents[nbr] = node
                    # 수정된 부분: node를 부모 정보로 추가하여 4개를 큐에 넣음
                    heapq.heappush(pq, (cost + w, nbr, hop, node))

    def link_change(self, a, b, cost):
        if cost is None:
            self.graph[a].pop(b, None)
            self.graph[b].pop(a, None)
        else:
            self.graph[a][b] = cost
            self.graph[b][a] = cost
            
        needs_spf = False
        dist_a = self.distances.get(a, float('inf'))
        dist_b = self.distances.get(b, float('inf'))
        
        if cost is None:
            if self.parents.get(a) == b or self.parents.get(b) == a:
                needs_spf = True
        else:
            old_edge_used = (self.parents.get(a) == b or self.parents.get(b) == a)
            if old_edge_used:
                needs_spf = True
            else:
                if dist_a + cost <= dist_b or dist_b + cost <= dist_a:
                    needs_spf = True
                    
        if needs_spf:
            self._recompute()
