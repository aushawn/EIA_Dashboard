# ⚡ EIA Electricity Dashboard

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Live U.S. residential electricity data dashboard** pulling real-time metrics from the EIA API. Perfect for energy analysts tracking sales, pricing, revenue, and customer trends with up-to-date energy-relevant data.

Summary statistics include total MWh sold, average $/kWh price, revenue generated, and residential customer counts—updated monthly via public EIA API.

---

## 🌟 Key Features
*   **Live EIA Data**: Real-time residential electricity sales, price, revenue, customers from U.S. Energy Information Administration API
*   **Key Metrics Display**: Clean summary stats with formatted numbers (MWh, $/kWh, $M, customers)
*   **Secure API Handling**: EIA API key stored in Streamlit secrets (local `.streamlit/secrets.toml` or HF Spaces secrets)
*   **Fast Deployment**: Ultra-lightweight (2 deps only) - deploys in 45 seconds on HF Spaces/Streamlit Cloud

## 📸 Demo
See the app deployed on HuggingFaces :hugs: 

[![Open in Spaces](https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-md.svg?download=true)](https://huggingface.co/spaces/ShawnAu/eia-electricity-dashboard)

---

## ⚙️ Installation & Local Setup

To run this project locally, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/shawn-au/eia-electricity-dashboard.git
cd eia-electricity-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
`requirements.txt` contains:
```
pandas==2.2.2
requests==2.32.3
```

### 3. Get EIA API Key
- Go to [EIA Open Data Registration](https://www.eia.gov/opendata/register.php)
- Fill in your name and email
- Check your inbox for the API key (arrives instantly)
- Copy the key — it looks like: `abc123def456...`

### 4. Add API Key Locally
Create a `.streamlit` folder and `secrets.toml` file:

**Mac/Linux (Terminal)**:
```bash
mkdir .streamlit
echo 'EIA_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml
```

**Windows (PowerShell)**:
```powershell
mkdir .streamlit
echo 'EIA_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml
```

**Or manually** (any OS):
1. Create folder `.streamlit` in your project root
2. Create file `secrets.toml` inside it
3. Paste: `EIA_API_KEY = "your_api_key_here"`
4. Save

### 5. Run locally
```bash
streamlit run app.py
```
App opens automatically at `http://localhost:8501`

> ⚠️ **Never commit `.streamlit/secrets.toml` to GitHub.** Add it to `.gitignore`:
> ```
> .streamlit/secrets.toml
> ```

---

## 🚀 Hugging Face Spaces Deployment

1. Create [New Space](https://huggingface.co/new-space)
2. Select **Streamlit** SDK + **CPU basic (free)**
3. Upload `app.py` + `requirements.txt` + `README.md`
4. **Settings** → **Repository secrets** → Add `EIA_API_KEY` = your key
5. **Commit** → Live in 45 seconds!

---

## 📁 Repo Structure
```
├── app.py                 # Main Streamlit app
├── requirements.txt       # 2 lightweight deps only
├── README.md              # This file
└── .streamlit/
    └── secrets.toml       # Local EIA API key (gitignored)
```

## 🔧 Tech Stack
```
-  Streamlit  - Web app framework + native charts
-  Pandas     - Data processing + summary stats
-  Requests   - EIA API calls
-  EIA v2 API - Live energy data
```

## 📊 Data Source
**U.S. Energy Information Administration (EIA)** - Residential electricity retail sales:
- **Metrics**: Sales (MWh), Price ($/kWh), Revenue ($M), Customers
- **API**: `https://api.eia.gov/v2/electricity/retail-sales`
- **Frequency**: Monthly updates
- **License**: Public domain

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- [U.S. Energy Information Administration](https://www.eia.gov/opendata/) - Public energy data
- [Streamlit](https://streamlit.io) - Web app framework

---

**⭐ Star this repo if it helps your energy data portfolio!**

*Built for data engineers showcasing ETL + API skills in the energy sector.*
