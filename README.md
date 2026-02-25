# 💰 Borrow Smart AI

Borrow Smart AI is an intelligent, budget-aware loan analysis and decision-support application built with **Python + Streamlit**.

It helps users evaluate loan affordability, understand repayment risk, compare tenure scenarios, and simulate interest rate shocks using explainable financial logic.

⚠️ Educational tool only — not financial advice.

---

## 🚀 Features

✅ **EMI Calculator**  
Accurate EMI, total interest, and total payment computation.

✅ **Affordability Analysis**  
Evaluates EMI-to-income ratio and disposable income impact.

✅ **Risk Classification**  
Simple, explainable rules: Safe / Moderate / Risky.

✅ **Scenario Comparison**  
Compare multiple tenures to optimize EMI vs interest tradeoff.

✅ **Stress Testing**  
Simulate rate increases (+1%, +2%) to assess sensitivity.

✅ **Explainable Insights (XAI)**  
Transparent breakdown of financial decision logic.

✅ **AI Explanation Layer** *(optional)*  
LLM-powered natural language reasoning over tool outputs.

---

## 🧠 What Problem It Solves

Most loan calculators only show EMI.

Borrow Smart AI answers deeper questions:

- Can I truly afford this loan?
- How risky is this repayment?
- Which tenure is financially smarter?
- What if interest rates rise?
- How much buffer will I retain monthly?

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Optional LLM**: Groq API

---

## 📦 Project Structure


BorrowSmartAI/
│
├── borrowsmart.py # Streamlit UI
├── agent.py # Orchestration & logic routing
├── llm.py # Optional AI explanation layer
├── requirements.txt
├── .env # API keys (ignored)
│
└── tools/
├── emi.py
├── affordability.py
├── simulator.py
└── stress_test.py


---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/abimanyu2597/borrowsmart_ai.git
cd borrowsmart_ai
2️⃣ Create Virtual Environment

Mac / Linux

python3 -m venv .venv
source .venv/bin/activate

Windows

py -m venv .venv
.venv\Scripts\Activate.ps1
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run Application
streamlit run borrowsmart.py

App opens at:

http://localhost:8501
🔐 Environment Variables (Optional AI Mode)

Create .env file:

GROQ_API_KEY=your_api_key_here

Without API key → App still works using deterministic logic.

📊 Financial Logic Model
EMI Formula

Monthly rate:

r = annual_rate / (12 × 100)

EMI:

EMI = P × r × (1 + r)^n / ((1 + r)^n − 1)

Where:

P = Principal

r = Monthly interest rate

n = Number of months

Risk Classification Rules
EMI / Salary Ratio	Risk Level
< 30%	Safe
30% – 50%	Moderate
> 50%	Risky
⚡ Stress Testing Logic

Simulates rate shocks:

+1% Interest Rate

+2% Interest Rate

Measures EMI sensitivity and risk migration.

🎯 Intended Use Cases

✔ Personal loan planning
✔ Home / Car loan comparison
✔ Pre-loan decision analysis
✔ Budget risk evaluation
✔ Financial education / demos
✔ AI / FinTech portfolio projects

⚠️ Disclaimer

Borrow Smart AI is a decision-support simulator.

It does not replace professional financial advice, credit underwriting, or regulatory calculations.

Always validate critical financial decisions with qualified advisors.

👨‍💻 Author

Built by Raja Abimanyu
Data Scientist | AI Engineer | Applied ML & Decision Systems

⭐ Future Enhancements (Planned)

Down payment optimizer

Prepayment simulator

Inflation-adjusted income modeling

Multi-loan portfolio view

Real bank product comparison

Advanced risk modeling
