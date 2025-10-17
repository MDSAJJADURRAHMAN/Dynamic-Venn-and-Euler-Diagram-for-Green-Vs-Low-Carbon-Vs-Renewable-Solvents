# streamlit_app.py — Final Version (with sidebar toggle and warning fixes)

import io
from typing import Tuple, List, Set
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# -------------------------
# App setup and sidebar toggle
# -------------------------
st.set_page_config(page_title="Dynamic Venn-Euler Visualizer", layout="centered")

# --- Sidebar toggle button (slide animation) ---
st.markdown("""
    <style>
        /* Floating sidebar button and animation */
        .sidebar-toggle-btn {
            position: fixed;
            top: 18px;
            left: 18px;
            z-index: 9999;
            background: #262730;
            color: #fff;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            font-size: 22px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.25);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .sidebar-toggle-btn:hover {
            background: #40414a;
        }
        [data-testid="stSidebar"] {
            transition: margin-left 0.4s cubic-bezier(.4,2,.6,1);
        }
        .sidebar-hidden [data-testid="stSidebar"] {
            margin-left: -350px !important;
        }
    </style>
    <script>
        function toggleSidebarBtn() {
            const root = parent.document.querySelector('.block-container');
            if (root.classList.contains('sidebar-hidden')) {
                root.classList.remove('sidebar-hidden');
            } else {
                root.classList.add('sidebar-hidden');
            }
        }
    </script>
""", unsafe_allow_html=True)

# Button for sidebar open/close (icon toggles)
st.markdown('''
    <button class="sidebar-toggle-btn" onclick="toggleSidebarBtn()" title="Show/hide controls">
        <span id="sidebar-icon">☰</span>
    </button>
''', unsafe_allow_html=True)

# -------------------------
# Constants
# -------------------------
TRUTHY = {"1", "true", "yes", "y", "x", "✓", "t"}


# -------------------------
# Function explanations (one-liners)
# -------------------------
# load_table_from_github_raw: Loads a CSV file from a GitHub raw URL into a DataFrame.
# load_table_from_upload: Loads a CSV/XLSX file uploaded by the user into a DataFrame.
# _to_bool_df_from_wide: Converts a wide-format DataFrame to boolean membership table.
# interpret_table: Detects table format and returns a boolean membership table.
# combine_two_tables: Combines two membership tables into one (union of categories).
# compute_sets: Gets the set of items for each selected category.
# draw_venn: Draws a Venn/Euler diagram for 3 selected categories using Plotly.

def load_table_from_github_raw(url: str) -> pd.DataFrame:
    """Loads a CSV file from a GitHub raw URL into a DataFrame."""
    url = url.strip()
    r = requests.get(url)
    r.raise_for_status()
    ct = r.headers.get("content-type", "").lower()
    if url.endswith(".csv") or "text/csv" in ct:
        try:
            df = pd.read_csv(io.StringIO(r.text), encoding='utf-8-sig', skip_blank_lines=True, on_bad_lines='skip')
            if df.empty or df.shape[1] < 1:
                raise ValueError("CSV appears empty or invalid format.")
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")
    else:
        raise ValueError("Only CSV files are supported for remote fetch.")

def load_table_from_upload(uploaded_file) -> pd.DataFrame:
    """Loads a CSV/XLSX file uploaded by the user into a DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith((".xls", ".xlsx")):
        return pd.read_excel(uploaded_file)
    else:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            raise ValueError("Unsupported file type") from e

def _to_bool_df_from_wide(df: pd.DataFrame) -> pd.DataFrame:
    """Converts a wide-format DataFrame to boolean membership table."""
    if df.shape[1] < 2:
        cols = list(df.columns)
        preview = df.head().to_dict()
        raise ValueError(f"Expected wide format with at least 2 columns (item + categories).\nDetected columns: {cols}\nPreview: {preview}")
    first_col = df.columns[0]
    rest = list(df.columns[1:])
    converted = df[rest].apply(lambda col: col.astype(str).str.strip().str.lower().isin(TRUTHY))
    converted[first_col] = df[first_col].astype(str)
    grouped = converted.groupby(first_col, as_index=True).any()
    return grouped.astype(bool)

def interpret_table(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Detects table format and returns a boolean membership table."""
    df = df.copy()
    if df.shape[1] == 2:
        item_col, cat_col = df.columns[0], df.columns[1]
        df = df[[item_col, cat_col]].dropna()
        df_wide = pd.crosstab(df[item_col].astype(str), df[cat_col].astype(str)).astype(bool)
        return df_wide.astype(bool), "long"
    else:
        membership = _to_bool_df_from_wide(df)
        return membership.astype(bool), "wide"

def combine_two_tables(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Combines two membership tables into one (union of categories)."""
    w1, _ = interpret_table(df1)
    w2, _ = interpret_table(df2)
    combined = pd.concat([w1, w2], axis=1)
    combined = combined.infer_objects(copy=False).fillna(False)
    combined = combined.T.groupby(level=0).any().T
    return combined.infer_objects(copy=False).astype(bool)

def compute_sets(membership_df: pd.DataFrame, selected_cats: List[str]) -> List[Set[str]]:
    """Gets the set of items for each selected category."""
    sets = []
    for c in selected_cats:
        if c not in membership_df.columns:
            sets.append(set())
        else:
            members = set(membership_df.index[membership_df[c] == True].tolist())
            sets.append(members)
    return sets

def draw_venn(selected_cats: List[str], sets: List[Set[str]]):
    """Draws a Venn/Euler diagram for 3 selected categories using Plotly."""
    n = len(sets)
    if n == 3:
        region_members = [
            sets[0] - sets[1] - sets[2],
            sets[1] - sets[0] - sets[2],
            sets[2] - sets[0] - sets[1],
            (sets[0] & sets[1]) - sets[2],
            (sets[0] & sets[2]) - sets[1],
            (sets[1] & sets[2]) - sets[0],
            sets[0] & sets[1] & sets[2]
        ]
        colors = ['rgba(0,200,0,0.3)', 'rgba(255,0,200,0.3)', 'rgba(0,0,255,0.3)']
        fig = go.Figure()
        fig.add_shape(type="circle", xref="x", yref="y", x0=0, y0=0, x1=2, y1=2, fillcolor=colors[0], line_color=colors[0])
        fig.add_shape(type="circle", xref="x", yref="y", x0=1, y0=0.7, x1=3, y1=2.7, fillcolor=colors[1], line_color=colors[1])
        fig.add_shape(type="circle", xref="x", yref="y", x0=0.5, y0=1.2, x1=2.5, y1=3.2, fillcolor=colors[2], line_color=colors[2])

        # Improved text placement: avoid overlap by spreading out text and limiting items per region
        region_coords = [(0.5,0.5), (2.5,2.2), (1.5,3), (1,1.2), (1.2,2.5), (2,1.5), (1.5,2)]
        region_names = [selected_cats[0], selected_cats[1], selected_cats[2],
                        f"{selected_cats[0]} & {selected_cats[1]}",
                        f"{selected_cats[0]} & {selected_cats[2]}",
                        f"{selected_cats[1]} & {selected_cats[2]}",
                        "All three"]
        for (x, y), members, name in zip(region_coords, region_members, region_names):
            if members:
                # Limit to 5 items per region to avoid overlap, show count if more
                sorted_members = sorted(members)
                if len(sorted_members) > 5:
                    text = '<br>'.join(sorted_members[:5]) + f'<br>...({len(sorted_members)} total)'
                else:
                    text = '<br>'.join(sorted_members)
                fig.add_trace(go.Scatter(x=[x], y=[y], text=[text], mode='text', textfont=dict(size=14),
                                         hovertext=[name + ':<br>' + ', '.join(sorted_members)], hoverinfo='text'))
        # Category labels
        fig.add_trace(go.Scatter(x=[0.2], y=[2.1], text=[selected_cats[0]], mode='text', textfont=dict(size=18, color='green')))
        fig.add_trace(go.Scatter(x=[2.8], y=[2.8], text=[selected_cats[1]], mode='text', textfont=dict(size=18, color='magenta')))
        fig.add_trace(go.Scatter(x=[1.5], y=[3.3], text=[selected_cats[2]], mode='text', textfont=dict(size=18, color='blue')))
        fig.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False),
                          margin=dict(l=0, r=0, t=40, b=0), height=600, width=600,
                          title=f"Venn/Euler Diagram: {', '.join(selected_cats)}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Plotly Venn is only implemented for 3 sets.")


# -------------------------
# Streamlit UI
# -------------------------

# --- Main Title and Description ---
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:0.5em">
    <span style="font-size:2.2em;font-weight:700;letter-spacing:-1px;">Dynamic Venn–Euler Visualizer</span>
    <span style="background:#e0e7ef;color:#1a1a1a;font-size:1.1em;padding:4px 12px;border-radius:8px;">Professional Edition</span>
</div>
<div style="font-size:1.1em;margin-bottom:1em;">
    <b>Visualize set/category overlaps from your data in seconds.</b><br>
    <ul style="margin:0 0 0 1.2em;padding:0;">
        <li>Supports <b>wide</b> (items × category columns) and <b>long</b> (item, category) formats</li>
        <li>Source: <b>upload files</b> or <b>GitHub Integration – Use raw URLs; auto-refresh every 10 seconds</b></li>
        <li>Interactive sidebar for category selection and export</li>
    </ul>
</div>
<hr style="margin:0.5em 0 1.2em 0;">
""", unsafe_allow_html=True)

# Data source selection

# --- Tab-style input source selection ---
st.markdown("""
<style>
.input-source-tabs {
    display: flex;
    gap: 0;
    margin-bottom: 1.5em;
    border-bottom: 2.5px solid #e0e7ef;
    width: fit-content;
}
.input-source-tab {
    background: #f5f7fa;
    color: #1a7f37;
    border: none;
    border-bottom: 2.5px solid transparent;
    border-radius: 10px 10px 0 0;
    padding: 0.7em 2.2em 0.7em 2.2em;
    font-size: 1.13em;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, color 0.2s, border 0.2s;
    outline: none;
    margin-right: 2px;
}
.input-source-tab.selected {
    background: #fff;
    color: #222;
    border-bottom: 2.5px solid #1a7f37;
    box-shadow: 0 -2px 8px 0 rgba(26,127,55,0.04);
    z-index: 2;
}
.input-source-tab:not(.selected):hover {
    background: #e0e7ef;
    color: #1a7f37;
}
</style>
""", unsafe_allow_html=True)


if 'input_source' not in st.session_state:
        st.session_state.input_source = 'Upload files'




# --- Tab-style input source selection with blue background for active tab ---
tab_css = """
<style>
.tab-btn {
  width: 100%;
  padding: 0.7em 0;
  font-size: 1.13em;
  font-weight: 600;
  border: none;
  border-radius: 10px 10px 0 0;
  margin-bottom: -2px;
  background: #f5f7fa;
  color: #1a1a1a;
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
}
.tab-btn.active {
  background: #2563eb !important;
  color: #fff !important;
  box-shadow: 0 -2px 8px 0 rgba(37,99,235,0.08);
}
</style>
"""
st.markdown(tab_css, unsafe_allow_html=True)
tab1, tab2 = st.columns(2)
with tab1:
    if st.button('Upload files', key='tab_upload'):
        st.session_state.input_source = 'Upload files'
    st.markdown(f'<button class="tab-btn{ " active" if st.session_state.input_source=="Upload files" else "" }">Upload files</button>', unsafe_allow_html=True)
with tab2:
    if st.button('Fetch from GitHub raw URL', key='tab_github'):
        st.session_state.input_source = 'Fetch from GitHub raw URL'
    st.markdown(f'<button class="tab-btn{ " active" if st.session_state.input_source=="Fetch from GitHub raw URL" else "" }">Fetch from GitHub raw URL</button>', unsafe_allow_html=True)



source_option = st.session_state.input_source
# Use session state to persist loaded data between tab switches
if 'df_main' not in st.session_state:
    st.session_state.df_main = None
if 'df_second' not in st.session_state:
    st.session_state.df_second = None
df_main = st.session_state.df_main
df_second = st.session_state.df_second

if source_option == "Upload files":
    st.info("Upload one or two files. If you upload two, they will be combined (union of categories).")
    uploaded1 = st.file_uploader("Upload table 1 (CSV / XLSX)", type=["csv", "xls", "xlsx"], key="u1")
    uploaded2 = st.file_uploader("Upload table 2 (CSV / XLSX) — optional", type=["csv", "xls", "xlsx"], key="u2")
    if uploaded1:
        try:
            df_main = load_table_from_upload(uploaded1)
            st.session_state.df_main = df_main
            st.success("Table 1 loaded — head:")
            st.dataframe(df_main.head())
        except Exception as e:
            st.error(f"Failed to load table 1: {e}")
    if uploaded2:
        try:
            df_second = load_table_from_upload(uploaded2)
            st.session_state.df_second = df_second
            st.success("Table 2 loaded — head:")
            st.dataframe(df_second.head())
        except Exception as e:
            st.error(f"Failed to load table 2: {e}")
elif source_option == "Fetch from GitHub raw URL":
    st.markdown("""
        <b>GitHub Integration</b>: Enter <b>raw.githubusercontent.com</b> links for your CSV files.<br>
        <span style='color:#1a7f37'>Auto-refresh</span> will check for updates every <b>10 seconds</b> if enabled.
    """, unsafe_allow_html=True)
    url1 = st.text_input("Raw URL for table 1 (required)")
    url2 = st.text_input("Raw URL for table 2 (optional)")
    auto_refresh = st.checkbox("Auto-refresh every 10 seconds (GitHub only)", value=False, key="autoref_checkbox")
    refresh_count = 0
    if auto_refresh:
        refresh_count = st_autorefresh(interval=10000, limit=None, key="autoref10s")
    st.write(f"<span style='color:#1a7f37'>Auto-refresh tick: {refresh_count}</span>", unsafe_allow_html=True)
    if st.button("Fetch from URL(s)", key='fetch_btn') or auto_refresh:
        try:
            if url1:
                with st.spinner("Fetching table 1..."):
                    df_main = load_table_from_github_raw(url1)
                    st.session_state.df_main = df_main
                    st.success("Table 1 loaded — head:")
                    st.dataframe(df_main.head())
            if url2:
                with st.spinner("Fetching table 2..."):
                    df_second = load_table_from_github_raw(url2)
                    st.session_state.df_second = df_second
                    st.success("Table 2 loaded — head:")
                    st.dataframe(df_second.head())
        except Exception as e:
            st.error(f"Failed to fetch: {e}")

# Interpret tables
membership_df = None
if df_main is not None:
    try:
        if df_second is not None:
            membership_df = combine_two_tables(df_main, df_second)
            st.write("Combined membership table (items × categories):")
            st.dataframe(membership_df.head())
        else:
            membership_df, fmt = interpret_table(df_main)
            st.write(f"Membership table (items × categories) — detected format: {fmt}")
            st.dataframe(membership_df.head())
    except Exception as e:
        st.error(f"Error interpreting tables: {e}")


# Sidebar and visualization

if membership_df is not None:
    st.sidebar.header("Visualization Controls")
    st.sidebar.markdown("<span style='font-size:1.1em;color:#1a7f37'><b>Step 1:</b></span> <b>Select categories</b>", unsafe_allow_html=True)
    cats = membership_df.columns.tolist()
    st.sidebar.markdown(f"<span style='color:#888'>{len(cats)} categories detected.</span>", unsafe_allow_html=True)
    chosen = st.sidebar.multiselect("Select 2 or 3 categories to visualize", options=cats, default=cats[:3])
    st.sidebar.markdown("<span style='font-size:1.1em;color:#1a7f37'><b>Step 2:</b></span> <b>Export or inspect</b>", unsafe_allow_html=True)
    if len(chosen) not in (2, 3):
        st.warning("Please select 2 or 3 categories (for venn2/venn3).")
    else:
        sets = compute_sets(membership_df, chosen)
        st.subheader(":bar_chart: Venn/Euler Diagram")
        draw_venn(chosen, sets)
        if st.checkbox("Show members for selected categories"):
            for cat, s in zip(chosen, sets):
                st.write(f"**{cat}** ({len(s)} items):")
                st.write(", ".join(sorted(s)) if s else "_No items_")
        st.markdown("### Export")


    try:
        table2 = pd.read_csv("data/sample_table2.csv", encoding='utf-8-sig', skip_blank_lines=True, on_bad_lines='skip')
        with st.expander("⚠️ Non-sustainable or conditional solvents", expanded=False):
            st.write("These solvents fail one or more criteria. Major concerns are listed below.")
            st.dataframe(table2)
    except Exception as e:
        st.warning(f"Could not load Table 2: {e}")

    st.markdown("---")
    st.header(":mag: Verification & Diagnostics")
    st.markdown(f"- <b>Detected categories</b>: {len(membership_df.columns)}", unsafe_allow_html=True)
    st.markdown(f"- <b>Detected items</b>: {len(membership_df.index)}", unsafe_allow_html=True)
    if len(membership_df.columns) > 0:
        counts = membership_df.sum(axis=0).sort_values(ascending=False)
        st.dataframe(counts.reset_index().rename(columns={"index": "category", 0: "count"}))
    st.markdown("<span style='color:#1a7f37'>Update the source files or use auto-refresh to verify diagram updates automatically.</span>", unsafe_allow_html=True)
else:
    st.info("Please load a table (upload or fetch) to continue.")
