import matplotlib.pyplot as plt
import osmnx as ox
import streamlit as st
from shortest_path_project import load_road_graph, run_dijkstra

st.set_page_config(page_title="D3 - Dijkstra Shortest Path", layout="wide")
st.title("D3: Dijkstra Shortest Path Implementation & Interactive Test")


@st.cache_resource
def cached_graph(place_name: str, network_type: str):
    return load_road_graph(place_name, network_type=network_type)


with st.sidebar:
    st.header("Graph & Algorithm Settings")
    place_name = st.text_input("Location", "Sentrum, Oslo, Norway")
    network_type = st.selectbox("Network Type", ["drive", "walk", "bike"], index=0)
    weight_attr = st.selectbox(
        "Edge Weight Metric",
        ["length", "travel_time"],
        index=0,
    )

G = cached_graph(place_name, network_type)
nodes = list(G.nodes)

st.caption(
    f"Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} directed edges."
)

col_src, col_dst, col_btn = st.columns([2, 2, 1])
src_idx = col_src.selectbox("Source Node Index", range(len(nodes)), index=0)
dst_idx = col_dst.selectbox(
    "Target Node Index", range(len(nodes)), index=max(len(nodes) - 1, 0)
)
run_clicked = col_btn.button("Run Dijkstra", type="primary")

if run_clicked:
    source_node = nodes[src_idx]
    target_node = nodes[dst_idx]
    result = run_dijkstra(G, source_node, target_node, weight_attr=weight_attr)

    if not result["reachable"]:
        st.warning(
            "No directed path found between the selected source and target nodes."
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        unit_label = "m" if weight_attr == "length" else "s"
        m1.metric("Shortest Cost", f"{result['total_cost']:.2f} {unit_label}")
        m2.metric(
            "Visited Nodes",
            f"{result['visited_nodes']} / {result['total_graph_nodes']}",
        )
        m3.metric("Execution Time", f"{result['elapsed_ms']:.2f} ms")
        m4.metric("Path Hops (Nodes)", len(result["path"]))

        fig, ax = ox.plot_graph_route(
            G,
            result["path"],
            route_color="#e63946",
            route_linewidth=3,
            node_size=0,
            bgcolor="#111111",
            edge_color="#444444",
            show=False,
            close=False,
        )
        st.pyplot(fig, clear_figure=True)
