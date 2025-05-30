import os

import streamlit as st
import streamlit.components.v1 as components
from evaluator import SpiceEvaluator
from scene_graph_visualizer import make_pyvis

st.set_page_config(page_title="SPICE Eval Dashboard", layout="wide")
st.title("🎯 SPICE & Scene-Graph Evaluation")

# Summary
st.markdown(
    """
This dashboard provides an interactive way to evaluate image captions through:

- **SPICE Evaluation**: Invokes the SPICE-1.0 Java jar to compute official precision, recall, and F₁.
- **Interactive Scene Graphs**: Visualizes the extracted tuples as force-directed graphs.
"""
)

# Sidebar Inputs
st.sidebar.header("Caption Inputs")
st.sidebar.markdown("Developed by [Gayanukaa](https://gayanukaa.github.io)")

raw_candidate = st.sidebar.text_area(
    "Candidate Caption", "a herd of giraffe standing next to each other"
)
raw_refs = st.sidebar.text_area(
    "Reference Captions (one per line)",
    "\n".join(
        [
            "a couple of giraffes that are walking around",
            "a herd of giraffe standing on top of a dirt field.",
            "Several smaller giraffes that are in an enclosure.",
            "The giraffes are walking in different directions outside.",
            "A giraffe standing next to three baby giraffes in a zoo exhibit.",
        ]
    ),
)

if not st.sidebar.button("Evaluate"):
    st.sidebar.info("Enter captions and click **Evaluate**.")
    st.stop()


def normalize_line(line: str) -> str:
    """
    Strip whitespace and surrounding quotes from a single line.
    """
    s = line.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        s = s[1:-1].strip()
    return s


# Normalize candidate
candidate = normalize_line(raw_candidate)
if not candidate:
    st.sidebar.error("Candidate caption is empty after normalization.")
    st.stop()

# Normalize references: split on newlines, normalize each, drop empty
refs = []
for line in raw_refs.splitlines():
    nl = normalize_line(line)
    if nl:
        refs.append(nl)
if not refs:
    st.sidebar.error("Please enter at least one reference caption.")
    st.stop()

log_expander = st.expander("🖥️ Logs", expanded=True)
log_container = log_expander.empty()
logs = []


def log_fn(msg: str):
    logs.append(msg)
    log_container.text_area(
        label="Logs",  # non-empty label
        value="\n".join(logs),
        height=200,
        disabled=True,
        label_visibility="collapsed",  # hide it from view
    )


evaluator = SpiceEvaluator()
out = evaluator.evaluate(candidate, refs, log_fn=log_fn)

st.subheader("📊 Evaluation Results")
c3, c1, c2 = st.columns(3)
c1.metric("Precision", f"{out['spice_precision']:.3f}")
c2.metric("Recall", f"{out['spice_recall']:.3f}")
c3.metric("F₁-Score", f"{out['spice_f1']:.3f}")

cand_exp = st.expander("View Extracted Tuples (Candidate)", expanded=False)
with cand_exp:
    cand_tup_str = "[" + ", ".join(str(tuple(t)) for t in out["test_tuples"]) + "]"
    st.code(cand_tup_str, language="python")

ref_exp = st.expander("View Extracted Tuples (References)", expanded=False)
with ref_exp:
    for i, ref in enumerate(refs, start=1):
        ref_tup_str = "[" + ", ".join(str(tuple(t)) for t in out["ref_tuples"]) + "]"
        st.markdown(f"**Reference {i}:** “{ref}”")
        st.code(ref_tup_str, language="python")

st.subheader("🌳 Interactive Scene-Graphs")
g1, g2 = st.columns(2)

with g1:
    st.markdown("**Candidate Caption Graph**")
    if out["test_tuples"]:
        html1 = make_pyvis(
            tuples=out["test_tuples"],
            node_color="lightblue",
            edge_color="blue",
            filename="candidate_graph.html",
            title="Candidate",
        )
        components.html(html1, height=500, scrolling=True)
    else:
        st.warning("No candidate tuples to visualize.")

with g2:
    st.markdown("**Reference Caption Graph**")
    if out["ref_tuples"]:
        html2 = make_pyvis(
            tuples=out["ref_tuples"],
            node_color="lightgreen",
            edge_color="green",
            filename="reference_graph.html",
            title="Reference",
        )
        components.html(html2, height=500, scrolling=True)
    else:
        st.warning("No reference tuples to visualize.")
