# streamlit_app_2.py
# Dynamic Venn–Euler Visualizer with conditional solvent highlighting

import io
import math
from typing import List, Set, Tuple
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Dynamic Venn–Euler (Conditional Highlighting)", layout="centered")
st.markdown(
        """
        <style>
        /* 3D card effect for main container */
        .main .block-container {background: #f7fafc; border-radius: 18px; box-shadow: 0 8px 32px 0 rgba(31,38,135,0.18); padding: 2rem 2.5rem;}
        /* 3D effect for expanders */
        .stExpander {box-shadow: 0 4px 16px 0 rgba(31,38,135,0.10); border-radius: 12px;}
        /* Smooth transitions */
        .stExpander, .main .block-container {transition: box-shadow 0.3s, background 0.3s;}
        /* Dropdown hover */
        .stExpander:hover {box-shadow: 0 8px 32px 0 rgba(31,38,135,0.18);}
        /* Table and text */
        .stDataFrame, .stTable {background: #fff; border-radius: 10px; box-shadow: 0 2px 8px 0 rgba(31,38,135,0.08);}
        /* Headings */
        h1, h2, h3, h4 {text-shadow: 0 2px 8px rgba(31,38,135,0.08);}
        </style>
        """,
        unsafe_allow_html=True,
)
st.title("♻️ Dynamic Venn–Euler for Green Vs Renewable Vs Low-Carbon Solvent Classification (3D UI)")
st.markdown("""
<div style='font-size:1.1rem; color:#333; margin-bottom:1.2em;'>
Upload one or two CSV files with columns like <b>Solvent, Green, Renewable, Low-Carbon</b>.<br>
<ul>
<li>Recognizes three symbols: ✓ (confirmed or meets criterion), (✓) (conditionally meets criterion), – (fails to meet criterion)</li>
<li>Conditional solvents are drawn with dashed outlines and lighter shade.</li>
<li>Modern 3D-style interface with dropdowns for each classification.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def normalize_symbol(v):
    s = str(v).strip().lower()
    if s in {"✓", "yes", "true", "y", "1", "x", "t"}:
        return "yes"
    if s in {"(✓)", "(yes)", "(true)", "(y)", "(t)"}:
        return "conditional"
    if s in {"–", "-", "no", "false", "n", "0", ""}:
        return "no"
    return "no"

def read_csv_forgiving(file_or_bytes) -> pd.DataFrame:
    for enc in ("utf-8-sig", "cp1252", "latin1"):
        try:
            if isinstance(file_or_bytes, (bytes, bytearray)):
                return pd.read_csv(io.BytesIO(file_or_bytes), encoding=enc)
            return pd.read_csv(file_or_bytes, encoding=enc)
        except Exception:
            continue
    if isinstance(file_or_bytes, (bytes, bytearray)):
        return pd.read_csv(io.BytesIO(file_or_bytes), encoding="utf-8", errors="replace")
    return pd.read_csv(file_or_bytes, encoding="utf-8", errors="replace")

def to_membership(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols = df.columns.tolist()
    item_col = None
    for c in cols:
        if c.strip().lower() == "solvent":
            item_col = c
            break
    if item_col is None:
        item_col = cols[0]
    cat_cols = [c for c in cols if c != item_col and c.strip().lower() not in ("short rationale","rationale")]
    for c in cat_cols:
        df[c] = df[c].apply(normalize_symbol)
    df[item_col] = df[item_col].astype(str)
    df = df[[item_col] + cat_cols].fillna("no")
    df = df.groupby(item_col, as_index=True).agg(lambda x: "yes" if "yes" in x.values else ("conditional" if "conditional" in x.values else "no"))
    return df

def merge_by_first3(base: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    base = base.copy()
    new = new.copy()
    # Always ensure index is string for slicing
    base = base.reset_index()
    new = new.reset_index()
    base["__k"] = base[base.columns[0]].astype(str).str.slice(0,3).str.lower()
    new["__k"] = new[new.columns[0]].astype(str).str.slice(0,3).str.lower()
    # Ensure '__k' is always present in columns for reindex
    cols = sorted(set(base.columns.tolist() + new.columns.tolist()))
    if "__k" not in cols:
        cols.append("__k")
    base = base.reindex(columns=cols, fill_value="no")
    new = new.reindex(columns=cols, fill_value="no")
    merged_rows = {}
    for _, row in base.set_index("__k").iterrows():
        merged_rows[row.name] = row
    for _, row in new.set_index("__k").iterrows():
        merged_rows[row.name] = row
    merged = pd.DataFrame(merged_rows.values())
    # Use the original solvent name as index if available
    idx_col = base.columns[0]
    merged.index = [r[idx_col] if idx_col in r else str(i) for i, r in merged.iterrows()]
    merged = merged.drop(columns=["index","__k"], errors="ignore")
    merged = merged.fillna("no")
    return merged

def compute_sets(df: pd.DataFrame, cats: List[str]) -> Tuple[List[Set[str]], List[Set[str]]]:
    yes_sets = []
    cond_sets = []
    for c in cats:
        yes_sets.append(set(df.index[df[c] == "yes"]))
        cond_sets.append(set(df.index[df[c] == "conditional"]))
    return yes_sets, cond_sets

def safe_font(total_labels: int) -> int:
    size = 18 - max(0, total_labels - 10) * 0.7
    return int(max(11, min(20, size)))

def venn_params_from_sizes(sets: List[Set[str]]) -> Tuple[List[float], List[Tuple[float,float]]]:
    n = len(sets)
    sizes = [len(s) for s in sets]
    max_n = max(1, max(sizes))
    radii = [0.8 + 0.9*math.sqrt(sz/max_n) for sz in sizes]
    def jacc(a: Set[str], b: Set[str]) -> float:
        if not a and not b: return 0.0
        u = len(a|b)
        if u==0: return 0.0
        return len(a&b)/u
    if n == 2:
        j01 = jacc(sets[0], sets[1])
        d01 = (radii[0] + radii[1]) * (1 - 0.7*j01)
        centers = [(0,0), (d01, 0)]
        return radii, centers
    j01 = jacc(sets[0], sets[1])
    j02 = jacc(sets[0], sets[2])
    j12 = jacc(sets[1], sets[2])
    d01 = (radii[0] + radii[1]) * (1 - 0.7*j01)
    d02 = (radii[0] + radii[2]) * (1 - 0.7*j02)
    d12 = (radii[1] + radii[2]) * (1 - 0.7*j12)
    x0,y0 = 0.0, 0.0
    x1,y1 = d01, 0.0
    x2 = (d02**2 - d12**2 + d01**2) / (2*d01 + 1e-6)
    y2_sq = max(0.0, d02**2 - x2**2)
    y2 = math.sqrt(y2_sq)
    centers = [(x0,y0),(x1,y1),(x2,y2)]
    return radii, centers

def draw_dynamic_venn(selected: List[str], yes_sets: List[Set[str]], cond_sets: List[Set[str]]):
    n = len(yes_sets)
    fig = go.Figure()
    radii, centers = venn_params_from_sizes(yes_sets)
    # 3D-style colors and shadows - mapped by category name
    color_map = {
        "Green": ("rgba(26,150,65,0.45)", "rgba(26,150,65,0.10)"),      # Green
        "Renewable": ("rgba(255,182,193,0.45)", "rgba(255,182,193,0.10)"),    # Pink/Rose
        "Low-Carbon": ("rgba(192,192,192,0.45)", "rgba(192,192,192,0.10)")     # Gray
    }
    # Assign colors based on actual category names
    colors = []
    shadow_colors = []
    for cat in selected:
        # Match category name (case-insensitive and flexible)
        cat_lower = cat.strip().lower()
        if "green" in cat_lower:
            c, s = color_map["Green"]
        elif "renewable" in cat_lower:
            c, s = color_map["Renewable"]
        elif "low" in cat_lower and "carbon" in cat_lower:
            c, s = color_map["Low-Carbon"]
        else:
            # Default fallback colors if category doesn't match
            c, s = "rgba(100,100,200,0.45)", "rgba(100,100,200,0.10)"
        colors.append(c)
        shadow_colors.append(s)
    # Draw shadow for 3D effect
    for i in range(n):
        cx, cy = centers[i]
        r = radii[i]
        fig.add_shape(type="circle", xref="x", yref="y",
                      x0=cx - r-0.12, y0=cy - r-0.12, x1=cx + r+0.12, y1=cy + r+0.12,
                      fillcolor=shadow_colors[i], line=dict(color=shadow_colors[i], width=0))
    # Draw main circles
    for i in range(n):
        cx, cy = centers[i]
        r = radii[i]
        fig.add_shape(type="circle", xref="x", yref="y",
                      x0=cx - r, y0=cy - r, x1=cx + r, y1=cy + r,
                      fillcolor=colors[i], line=dict(color=colors[i].replace("0.45","0.85"), width=3))
        if cond_sets[i]:
            fig.add_shape(type="circle", xref="x", yref="y",
                          x0=cx - r*0.95, y0=cy - r*0.95, x1=cx + r*0.95, y1=cy + r*0.95,
                          line=dict(color=colors[i].replace("0.45","0.85"), dash="dash", width=2),
                          fillcolor="rgba(0,0,0,0)")
    total_labels = sum(len(s) for s in yes_sets)
    fsize = safe_font(total_labels)
    # Place main category labels OUTSIDE the circles
    label_offsets = []
    window_pad = 2.5  # Padding from window border for label visibility
    if n == 2:
        # Place left label far left, right label far right
        xs = [c[0] for c in centers]
        lx_left = xs[0] - radii[0] - window_pad
        lx_right = xs[1] + radii[1] + window_pad
        label_offsets = [(lx_left - xs[0], 0), (lx_right - xs[1], 0)]
    elif n == 3:
        xs = [c[0] for c in centers]
        ys = [c[1] for c in centers]
        # Top label above top circle, left label far left, right label far right
        lx_top = xs[0]
        ly_top = ys[0] + radii[0] + window_pad
        lx_left = xs[1] - radii[1] - window_pad
        ly_left = ys[1]
        lx_right = xs[2] + radii[2] + window_pad
        ly_right = ys[2]
        label_offsets = [
            (lx_top - xs[0], ly_top - ys[0]),
            (lx_left - xs[1], ly_left - ys[1]),
            (lx_right - xs[2], ly_right - ys[2])
        ]
    else:
        label_offsets = [(0, radii[0]+window_pad)] * n
    for i, cat in enumerate(selected):
        text_items = sorted(yes_sets[i] | cond_sets[i])
        display_text = "<br>".join(text_items[:5])
        if len(text_items) > 5:
            display_text += f"<br>...({len(text_items)} total)"
        cx, cy = centers[i]
        # Solvent names inside
        fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="text", text=[display_text],
                                 hovertext=f"{cat}: {len(yes_sets[i])} ✓ + {len(cond_sets[i])} (✓)",
                                 hoverinfo="text", textfont=dict(size=fsize, color="#222")))
        # (Removed) main outside label - we'll render a top legend instead so labels don't overlap the circles
    xs = [c[0] for c in centers]
    ys = [c[1] for c in centers]
    span = max([r for r in radii]+[1])
    pad = 1.2*span
    x_min, x_max = min(xs)-pad, max(xs)+pad
    y_min, y_max = min(ys)-pad, max(ys)+pad
    fig.update_layout(
        title=f"Venn/Euler Diagram: {', '.join(selected)} (✓ solid, (✓) dashed)",
        xaxis=dict(visible=False, range=[x_min, x_max]),
        yaxis=dict(visible=False, range=[y_min, y_max]),
        showlegend=False, width=850, height=700, margin=dict(l=10,r=10,t=60,b=10),
        paper_bgcolor="#f7fafc",
        plot_bgcolor="#f7fafc",
        font=dict(family="Segoe UI,Arial", color="#222"),
        hoverlabel=dict(bgcolor="#fff", font_size=16, font_family="Segoe UI,Arial"),
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    # Render a compact legend at the top showing which color maps to which category
    legend_items = []
    for i, cat in enumerate(selected):
        outline = colors[i].replace("0.45", "0.85") if i < len(colors) else "rgba(100,100,200,0.85)"
        # colored pill + label
        pill = f"<span style='display:inline-block;width:14px;height:12px;background:{outline};border-radius:3px;margin-right:8px;vertical-align:middle;box-shadow:0 1px 2px rgba(0,0,0,0.08);'></span>"
        label_html = f"<span style='margin-right:18px;color:{outline};font-weight:600;vertical-align:middle;'>{cat}</span>"
        legend_items.append(pill + label_html)
    legend_html = "<div style='text-align:center;margin-bottom:10px;'>" + "".join(legend_items) + "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Inputs
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    f1 = st.file_uploader("Upload Table 1 (CSV)", type=["csv"], key="t1")
with col2:
    f2 = st.file_uploader("Upload Table 2 (CSV) — optional", type=["csv"], key="t2")

df1 = None
df2 = None
if f1 is not None:
    df1 = read_csv_forgiving(f1)
if f2 is not None:
    df2 = read_csv_forgiving(f2)

if df1 is None:
    st.warning("Please upload at least one CSV to proceed.")
    st.stop()

st.subheader("Data Preview")
st.dataframe(df1.head())
if df2 is not None:
    st.dataframe(df2.head())

m1 = to_membership(df1)
if df2 is not None:
    m2 = to_membership(df2)
    membership = merge_by_first3(m1, m2)
else:
    membership = m1


# --- Dropdown/collapsible lists for each classification ---
st.markdown("### ✅ Normalized membership (✓ = confirmed, (✓) = conditional, – = no)")
st.dataframe(membership)

cats = [c for c in membership.columns if c.strip().lower() not in ("solvent","short rationale","rationale")]
for cat in cats:
    with st.expander(f"{cat} solvents ({(membership[cat]=='yes').sum()} ✓, {(membership[cat]=='conditional').sum()} (✓))", expanded=False):
        yes_list = membership.index[membership[cat]=="yes"].tolist()
        cond_list = membership.index[membership[cat]=="conditional"].tolist()
        st.markdown(f"<b>✓ Confirmed:</b> {', '.join(yes_list) if yes_list else '<i>None</i>'}", unsafe_allow_html=True)
        st.markdown(f"<b>(✓) Conditional:</b> {', '.join(cond_list) if cond_list else '<i>None</i>'}", unsafe_allow_html=True)

cats = [c for c in membership.columns if c.strip().lower() not in ("solvent","short rationale","rationale")]
default_sel = cats[:3] if len(cats)>=3 else cats
selected = st.multiselect("Select 2 or 3 categories", cats, default=default_sel)

if len(selected) not in (2,3):
    st.info("Select exactly 2 or 3 categories to draw Venn/Euler.")
else:
    yes_sets, cond_sets = compute_sets(membership, selected)
    draw_dynamic_venn(selected, yes_sets, cond_sets)
    st.markdown("#### Category counts")
    counts = pd.DataFrame({
        "✓ confirmed": [len(s) for s in yes_sets],
        "(✓) conditional": [len(s) for s in cond_sets]
    }, index=selected)
    st.table(counts)




