import heapq
import time
import networkx as nx
import osmnx as ox


def load_road_graph(place_name: str, network_type: str = "drive") -> nx.MultiDiGraph:
    """Load a road network graph from OpenStreetMap via OSMnx."""
    G = ox.graph_from_place(place_name, network_type=network_type)
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G


def get_edge_weight(edge_data_dict: dict, weight_attr: str = "length") -> float:
    """Extract the minimum weight across parallel edges between two nodes."""
    weights = []
    for attr in edge_data_dict.values():
        val = attr.get(weight_attr)
        if val is not None and val > 0:
            weights.append(float(val))
    return min(weights) if weights else 1.0


def run_dijkstra(
    G: nx.MultiDiGraph,
    source,
    target,
    weight_attr: str = "length",
) -> dict:
    """Run Dijkstra's shortest path algorithm and return path and performance metrics."""
    start_time = time.perf_counter()

    dist = {source: 0.0}
    parent = {source: None}
    visited = set()
    pq = [(0.0, source)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if u == target:
            break

        if current_dist > dist.get(u, float("inf")):
            continue

        for v in G.neighbors(u):
            if v in visited:
                continue
            edge_weight = get_edge_weight(
                G.get_edge_data(u, v), weight_attr=weight_attr
            )
            new_dist = current_dist + edge_weight

            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                parent[v] = u
                heapq.heappush(pq, (new_dist, v))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    path = []
    if target in dist:
        curr = target
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    return {
        "reachable": target in dist,
        "path": path,
        "total_cost": dist.get(target, float("inf")),
        "visited_nodes": len(visited),
        "elapsed_ms": elapsed_ms,
        "total_graph_nodes": G.number_of_nodes(),
        "total_graph_edges": G.number_of_edges(),
    }
