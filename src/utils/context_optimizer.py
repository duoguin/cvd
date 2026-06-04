"""
context_optimizer.py
====================
Tối ưu context truyền vào LLM mỗi lượt bằng cách:
  1. Chỉ lấy phần flowchart lân cận nút hiện tại (local subgraph)
  2. Chỉ giữ N turns hội thoại gần nhất

Cách dùng (trong bot._gen_prompt):
    from utils.context_optimizer import get_local_flowchart, get_recent_history

    local_flow  = get_local_flowchart(self.workflow.workflow, current_node, depth=2)
    recent_hist = get_recent_history(self.conv, k_turns=6)

    prompt = jinja_render(
        self.bot_template_fn,
        workflow=local_flow,
        history_conversation=recent_hist,
        ...
    )
"""

from __future__ import annotations

import re
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# 1. Mermaid Flowchart Parser
# ---------------------------------------------------------------------------

@dataclass
class FlowNode:
    id: str
    label: str          # text bên trong node
    shape: str          # "round"=(), "rect"=[], "stadium"=([])…
    raw: str            # raw mermaid snippet của node này


@dataclass
class FlowEdge:
    src: str
    dst: str
    label: str          # text trên cạnh "--label-->"
    raw: str            # raw mermaid snippet của cạnh này


@dataclass
class FlowGraph:
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    edges: List[FlowEdge]      = field(default_factory=list)
    # adjacency (forward + backward)
    fwd: Dict[str, List[FlowEdge]] = field(default_factory=lambda: defaultdict(list))
    bwd: Dict[str, List[FlowEdge]] = field(default_factory=lambda: defaultdict(list))


# --- regex patterns ---
# node definitions embedded in edges, e.g.: SK001[some text]  SK000(Start)
_NODE_INLINE = re.compile(
    r'(?P<id>[A-Za-z][A-Za-z0-9_]*)(?P<open>[\[\(\{])(?P<label>[^\]\)\}]*)(?P<close>[\]\)\}])'
)
# "multi-source" edges: SK007 & SK008 -- label --> SK009
_MULTI_SRC = re.compile(r'([A-Za-z][A-Za-z0-9_]*(?:\s*&\s*[A-Za-z][A-Za-z0-9_]*)+)')
# edge pattern: src -- label --> dst  (label optional)
_EDGE = re.compile(
    r'(?P<srcs>[A-Za-z][A-Za-z0-9_]*(?:\s*&\s*[A-Za-z][A-Za-z0-9_]*)*)'
    r'\s*(?:--(?P<lbl>[^->]*)--?>|-->)\s*'
    r'(?P<dst>[A-Za-z][A-Za-z0-9_]*)(?P<dst_node>.*)?'
)
_BARE_NODE = re.compile(r'^(?P<id>[A-Za-z][A-Za-z0-9_]*)(?P<open>[\[\(\{])(?P<label>[^\]\)\}]*)(?P<close>[\]\)\}])$')


def _parse_node_snippet(nid: str, snippet: str) -> FlowNode:
    """Tạo FlowNode từ id và raw snippet (vd 'SK001[Ask user name]')."""
    m = _NODE_INLINE.search(snippet)
    if m:
        shape = {"[": "rect", "(": "round", "{": "diamond"}.get(m.group("open"), "rect")
        return FlowNode(id=nid, label=m.group("label").strip(), shape=shape, raw=snippet.strip())
    return FlowNode(id=nid, label=nid, shape="rect", raw=nid)


def parse_mermaid_flowchart(mermaid_text: str) -> FlowGraph:
    """
    Parse chuỗi Mermaid flowchart thành FlowGraph.
    Hỗ trợ:
      - SK001[text], SK000(Start), SK000([text])
      - edges: A --> B, A -- label --> B, A & B -- label --> C
      - inline node definitions trong edge lines
    """
    graph = FlowGraph()

    def register_node(nid: str, snippet: str = ""):
        if nid not in graph.nodes:
            graph.nodes[nid] = _parse_node_snippet(nid, snippet or nid)

    lines = mermaid_text.strip().splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        # bỏ qua header / subgraph / direction lines
        if not line or line.startswith("flowchart") or line.startswith("graph") \
                or line.startswith("subgraph") or line == "end":
            continue

        # Thử match edge pattern
        m_edge = _EDGE.match(line)
        if m_edge:
            srcs_raw = m_edge.group("srcs")
            lbl      = (m_edge.group("lbl") or "").strip()
            dst_id   = m_edge.group("dst")
            dst_rest = (m_edge.group("dst_node") or "").strip()

            # parse tất cả src ids (có thể "A & B")
            src_ids = [s.strip() for s in re.split(r'&', srcs_raw)]

            # Register inline node definitions cho srcs
            for sid in src_ids:
                # tìm inline def của src trong line (trước edge arrow)
                before_arrow = line.split("-->")[0].split("--")[0]
                m_src_node = _NODE_INLINE.search(before_arrow + " ")
                if m_src_node and m_src_node.group("id") == sid:
                    register_node(sid, before_arrow)
                else:
                    register_node(sid)

            # Register dst node (có inline def sau mũi tên)
            dst_full = dst_id + dst_rest
            m_dst = _NODE_INLINE.match(dst_full)
            if m_dst and m_dst.group("id") == dst_id:
                register_node(dst_id, dst_full)
            else:
                register_node(dst_id)

            # Thêm edges
            for sid in src_ids:
                edge = FlowEdge(src=sid, dst=dst_id, label=lbl, raw=line)
                graph.edges.append(edge)
                graph.fwd[sid].append(edge)
                graph.bwd[dst_id].append(edge)
        else:
            # standalone node definition (không phải edge)
            m_bare = _BARE_NODE.match(line)
            if m_bare:
                nid = m_bare.group("id")
                register_node(nid, line)

    return graph


# ---------------------------------------------------------------------------
# 2. Local Subgraph Extractor
# ---------------------------------------------------------------------------

def extract_local_subgraph(
    graph: FlowGraph,
    current_node: str,
    depth_fwd: int = 2,
    depth_bwd: int = 1,
) -> FlowGraph:
    """
    BFS từ current_node theo cả hai hướng:
      - depth_fwd bước về phía trước (các node sắp tới)
      - depth_bwd bước về phía sau  (context đã qua)
    Trả về FlowGraph con chỉ chứa các node/edge liên quan.
    """
    if current_node not in graph.nodes:
        # fallback: trả về toàn bộ
        return graph

    included_nodes: Set[str] = set()

    def bfs(start: str, adj: Dict[str, List[FlowEdge]], max_depth: int):
        q = deque([(start, 0)])
        visited = {start}
        while q:
            nid, d = q.popleft()
            included_nodes.add(nid)
            if d >= max_depth:
                continue
            for edge in adj.get(nid, []):
                neighbor = edge.dst if adj is graph.fwd else edge.src
                if neighbor not in visited:
                    visited.add(neighbor)
                    q.append((neighbor, d + 1))

    bfs(current_node, graph.fwd, depth_fwd)
    bfs(current_node, graph.bwd, depth_bwd)

    # Build sub-graph
    sub = FlowGraph()
    for nid in included_nodes:
        sub.nodes[nid] = graph.nodes[nid]
    for edge in graph.edges:
        if edge.src in included_nodes and edge.dst in included_nodes:
            sub.edges.append(edge)
            sub.fwd[edge.src].append(edge)
            sub.bwd[edge.dst].append(edge)
    return sub


def subgraph_to_mermaid(sub: FlowGraph, current_node: str = "") -> str:
    """
    Chuyển FlowGraph con về lại chuỗi Mermaid.
    Node hiện tại được đánh dấu bằng comment %% CURRENT.
    """
    lines = ["flowchart TD"]
    seen_edges: Set[Tuple] = set()

    for edge in sub.edges:
        key = (edge.src, edge.dst, edge.label)
        if key in seen_edges:
            continue
        seen_edges.add(key)

        src_node = sub.nodes.get(edge.src)
        dst_node = sub.nodes.get(edge.dst)

        def node_str(n: FlowNode) -> str:
            if n is None:
                return n.id
            marker = " %% ← CURRENT NODE" if n.id == current_node else ""
            if n.shape == "round":
                return f"{n.id}({n.label}){marker}"
            elif n.shape == "diamond":
                return f"{n.id}{{{{{n.label}}}}}{marker}"
            else:
                return f"{n.id}[{n.label}]{marker}"

        src_str = node_str(src_node) if src_node else edge.src
        dst_str = node_str(dst_node) if dst_node else edge.dst

        if edge.label:
            lines.append(f"    {src_str} -- {edge.label} --> {dst_str}")
        else:
            lines.append(f"    {src_str} --> {dst_str}")

    # Thêm các isolated nodes (nếu có, hiếm gặp)
    nodes_in_edges = {e.src for e in sub.edges} | {e.dst for e in sub.edges}
    for nid, node in sub.nodes.items():
        if nid not in nodes_in_edges:
            marker = " %% ← CURRENT NODE" if nid == current_node else ""
            if node.shape == "round":
                lines.append(f"    {nid}({node.label}){marker}")
            else:
                lines.append(f"    {nid}[{node.label}]{marker}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. High-level API: get_local_flowchart
# ---------------------------------------------------------------------------

def get_local_flowchart(
    full_flowchart: str,
    current_node: str,
    depth_fwd: int = 2,
    depth_bwd: int = 1,
) -> str:
    """
    Từ toàn bộ Mermaid flowchart string và node hiện tại,
    trả về Mermaid string chỉ chứa phần lân cận.

    Args:
        full_flowchart: nội dung file .md (Mermaid syntax)
        current_node:   ID node hiện tại, vd "SK004"
        depth_fwd:      số bước BFS về phía trước (default=2)
        depth_bwd:      số bước BFS về phía sau  (default=1)

    Returns:
        Mermaid string của subgraph, hoặc full_flowchart nếu parse thất bại.
    """
    try:
        graph = parse_mermaid_flowchart(full_flowchart)
        if not graph.nodes:
            return full_flowchart
        if current_node not in graph.nodes:
            # node chưa xác định → trả toàn bộ
            return full_flowchart
        sub = extract_local_subgraph(graph, current_node, depth_fwd, depth_bwd)
        result = subgraph_to_mermaid(sub, current_node)
        # Thêm chú thích để LLM biết đây là trích đoạn
        total = len(graph.nodes)
        shown = len(sub.nodes)
        header = (
            f"%% [Local view: showing {shown}/{total} nodes around {current_node}]\n"
            f"%% depth_back={depth_bwd}, depth_forward={depth_fwd}\n"
        )
        return header + result
    except Exception:
        # an toàn: fallback về full flowchart
        return full_flowchart


# ---------------------------------------------------------------------------
# 4. Conversation History Trimmer
# ---------------------------------------------------------------------------

def get_recent_history(conv, k_turns: int = 6) -> str:
    """
    Chỉ lấy k_turns lượt hội thoại gần nhất (1 lượt = 1 cặp user+bot).

    Args:
        conv:    đối tượng Conversation (có thuộc tính .msgs: List[Message])
        k_turns: số lượt user-bot cần giữ lại (default=6)

    Returns:
        Chuỗi history đã được trim.
    """
    from flowagent.data.base_data import Role  # import lazy để tránh circular

    msgs = conv.msgs
    if not msgs:
        return ""

    # Đếm ngược: mỗi message của USER bắt đầu 1 "turn"
    kept: List = []
    turns_counted = 0
    for msg in reversed(msgs):
        kept.append(msg)
        if msg.role == Role.USER:
            turns_counted += 1
            if turns_counted >= k_turns:
                break

    kept.reverse()

    # Thêm chú thích nếu bị trim
    total_msgs = len(msgs)
    shown_msgs = len(kept)
    prefix = ""
    if shown_msgs < total_msgs:
        prefix = f"[... {total_msgs - shown_msgs} earlier messages omitted ...]\n"

    return prefix + "\n".join(msg.to_str() for msg in kept)


# ---------------------------------------------------------------------------
# 5. Infer current node từ bot output / state string
# ---------------------------------------------------------------------------

_NODE_ID_RE = re.compile(r'\b(SK[0-9]{3})\b')  # noqa: W605


def infer_current_node(state_str: str, flowchart: str) -> Optional[str]:
    """
    Cố gắng tìm node ID (vd "SK004") từ chuỗi state mà LLM tự sinh.

    Ưu tiên:
      1. Match trực tiếp "SK[0-9]{3}" trong state_str
      2. Tìm node có label gần với nội dung state_str nhất (fuzzy, dự phòng)

    Returns:
        Node ID nếu tìm được, None nếu không.
    """
    # 1. Trực tiếp
    m = _NODE_ID_RE.search(state_str or "")
    if m:
        return m.group(1)

    # 2. Fuzzy: tìm node label chứa nhiều từ nhất từ state_str
    try:
        graph = parse_mermaid_flowchart(flowchart)
        state_words = set(re.findall(r'\w+', (state_str or "").lower()))
        best_node, best_score = None, 0
        for nid, node in graph.nodes.items():
            label_words = set(re.findall(r'\w+', node.label.lower()))
            score = len(state_words & label_words)
            if score > best_score:
                best_score, best_node = score, nid
        if best_score >= 2:     # cần match ít nhất 2 từ để tránh false positive
            return best_node
    except Exception:
        pass

    return None