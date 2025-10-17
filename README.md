# ♻️ Dynamic Venn–Euler Visualizer for Solvent Classification

A professional, **auto-adjusting Streamlit app** to visualize category overlaps dynamically using **Venn/Euler diagrams** — optimized for datasets like *Green / Renewable / Low-Carbon solvents*.

---

## 🚀 Features
- **Upload one or two CSV files**
  - Automatically merges by the **first three letters** of solvent names.
  - Supports symbols: ✓, (✓), –, yes/no/true/false/1/0.
- **Auto-scaling visualization**
  - Circles and spacing scale dynamically with overlap ratios.
  - Font size adjusts automatically to fit solvent names neatly.
- **Supports 2- or 3-set diagrams**
  - Perfect for comparing “Green”, “Renewable”, and “Low-Carbon”.
- **Interactive**
  - Choose categories dynamically.
  - View counts, hover tooltips, and clean labels.
- **Works offline or online**
  - Upload CSVs or load prepackaged test datasets (`Test Set 2.csv`, `solvent_table2_testdata.csv`, `toxic_solvents_testset3.csv`, `toxic_solvents_testset3.csv` ).

---

## 🧠 What’s New
This version intelligently:
- Detects and merges new solvents by name prefix.
- Adapts circle geometry to data density.
- Auto-balances text font and label overlap.
- Includes robust encoding detection for mixed CSVs.

---

## ⚙️ How to Run Locally
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   streamlit run streamlit_app_2.py
   ```

3. **Upload or use default data**
   - Upload your CSV(s) directly in the browser, or
   - Let it auto-load the default solvent test files in the same directory.

---

## 🌍 Free Deployment Options
### 1️⃣ Streamlit Community Cloud (Recommended)
1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account.
3. Create a new app and select this repo.
4. Set:
   - **Main file path**: `streamlit_app_2.py`
   - **Branch**: `main`
   - **Requirements file**: `requirements.txt`
5. Click **Deploy** — your app will be live in seconds!

### 2️⃣ Alternatives
- [Render.com](https://render.com/) (free tier)
- [Deta Space](https://deta.space/) (free tier)

---

## 📘 Example Input Format

### Wide Format (Recommended)
| Solvent | Green | Renewable | Low-Carbon |
|----------|--------|------------|-------------|
| Water | ✓ | ✓ | ✓ |
| Ethanol | – | ✓ | ✓ |
| Acetone | (✓) | – | ✓ |
| Ethyl Lactate | ✓ | ✓ | ✓ |

✓ = meets criteria  
(✓) = conditional (depends on route/energy)  
– = does not meet criteria

---

## 🧩 Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/MDSAJJADURRAHMAN/Dynamic-Venn-and-Euler-Diagram-for-Green-Vs-Low-Carbon-Vs-Renewable-Solvents.git
   cd Dynamic-Venn-and-Euler-Diagram-for-Green-Vs-Low-Carbon-Vs-Renewable-Solvents
   ```
2. Create virtual environment and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app_1.py
   ```
4. Select 2 or 3 categories and visualize overlaps.

---

## 🧮 Output Example
- Auto-scaled Venn/Euler diagram with proportional overlaps.
- Tooltips showing solvent counts per region.
- Merged solvent table shown below the graph.

---

## 🪶 License
© 2025 Dr. Md Sajjadur Rahman — MIT License.  
Designed for educational and research use in **Green Analytical Chemistry and Sustainable Solvent Systems**.
