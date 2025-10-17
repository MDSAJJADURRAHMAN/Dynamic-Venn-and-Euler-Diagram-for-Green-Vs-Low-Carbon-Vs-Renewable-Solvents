A Dynamic Venn–Euler Visualizer

A professional, interactive Streamlit app to visualize set/category overlaps from your data using Venn/Euler diagrams.

## Features
- Upload CSV/XLSX files or fetch data from GitHub raw URLs
- Auto-refresh for GitHub data (every 10 seconds)
- Supports wide (items × category columns) and long (item, category) formats
- Interactive sidebar for category selection and export
- Modern, user-friendly interface with sidebar toggle

## How to Run Locally
1. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
2. Start the app:
    ```bash
    streamlit run streamlit_app.py
    ```

## Free Deployment Options
- **Streamlit Community Cloud** (Recommended):
   1. Go to https://streamlit.io/cloud
   2. Sign in with GitHub and create a new app from your repo (or upload your code)
   3. Add your `requirements.txt` and `streamlit_app.py`
   4. Click Deploy. Your app will be live for free!

- **Alternatives:**
   - [Render.com](https://render.com/) (free tier)
   - [Deta Space](https://deta.space/) (free tier)

## Notes
- GitHub raw URLs may take 20–30 seconds to update after a commit due to GitHub CDN caching. This is not a bug in the app.
- For instant updates, use file upload mode.

---

© 2025 Your Name. MIT License.

A beginner-friendly Streamlit app to create Venn/Euler diagrams from one or two tables (CSV/XLSX).
Supports:
- Wide format (items × category columns)
- Long format (two columns: item, category)
- Upload or fetch from GitHub raw URLs
- 2- or 3-set Venn diagrams (matplotlib-venn)
- Export as PNG / SVG
- Optional auto-refresh (when fetching from URLs)

## Quick start

1. Clone this repo.
2. Create virtualenv and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3. Run:
   streamlit run streamlit_app.py
4. Upload CSV/XLSX files or paste GitHub raw URLs and click "Fetch".
5. Select 2 or 3 categories from the sidebar to visualize.

## Input formats

### Wide format:
First column = item name (string), subsequent columns = category flags (1/0, yes/no, x, true/false).
Example:
#   m y - s o l v e n t - d a t a - 
 
 
