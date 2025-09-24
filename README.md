# FinanceAutomationTool 💵

FinanceAutomationTool is a personal finance dashboard built with [Streamlit](https://streamlit.io/) that empowers you to analyze, categorize, and visualize your bank transactions with full control and transparency. Unlike generic banking summaries, this tool lets you define your own categories and keyword rules, ensuring accurate and meaningful insights into your spending and income. This was built when I realised DBS AI categorization leaves close to 80% of my transactions completely uncategorized. 

---

## Features

- **Custom Categorization:**  
  Define your own categories and associate them with specific keywords or phrases. Transactions are automatically categorized based on matches in their reference fields.

- **Interactive Editing:**  
  Easily review, edit, and re-categorize transactions directly in the web UI. Add new categories or keywords on the fly.

- **Keyword Management:**  
  When you change a transaction's category, you can specify a keyword or phrase to associate with that category for future auto-categorization.

- **Visual Analytics:**  
  Instantly view your expenses and income with interactive pie and bar charts, as well as summary tables.

- **Data Privacy:**  
  All processing is done locally in your browser and on your machine. Your financial data never leaves your computer.

---

## How It Works

1. **Upload CSV:**  
   Upload your bank transaction CSV file (supports DBS format and similar).

2. **Automatic Cleaning:**  
   The tool cleans and parses your file, handling common formatting issues.

3. **Categorization:**  
   Transactions are categorized based on your defined rules (keywords/phrases in Ref1, Ref2, or Ref3).

4. **Review & Edit:**  
   Use the interactive editor to review, correct, and further categorize your transactions.

5. **Visualize:**  
   Explore your spending and income with summary tables and charts.

---

## Getting Started

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/FinanceAutomationTool.git
   cd FinanceAutomationTool
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

### Running the App

```sh
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Usage

1. **Upload your transaction CSV file** using the file uploader.
2. **Review and edit categories** in the "Expenses (Debits)" tab.
3. **Add new categories** or associate new keywords/phrases as needed. This is done by directly retagging the expense in the UI boxes, and optionally providing a matching keyword in the dialogue box below for saving. 
4. **View summaries and charts** for both expenses and income.
5. **Categories and keywords** are saved in `categories.json` locally for all future sessions.

---

## File Structure

- `main.py` — Main Streamlit application and ETL data pipeline
- `categories.json` — Stores your custom categories and keywords (auto-generated).
- `requirements.txt` — Python dependencies.
- `README.md` — Project documentation.
- `.gitignore`, `.gitattributes`, `LICENSE` — Project configuration and license.

---

## Limitations & Notes

- **Keyword Matching:**  
  Use specific keywords or phrases to avoid misclassification. Only transactions containing the exact keyword/phrase in Ref1, Ref2, or Ref3 will be auto-categorized.
- **Manual Cleanup:**  
  Removing keywords from categories must be done manually in `categories.json`.
- **UI-Driven Workflow:**  
  For best results, use the UI to categorize uncategorized transactions. Manual edits to categorized transactions require manual keyword management.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/), [Pandas](https://pandas.pydata.org/), and [Plotly](https://plotly.com/python/).
- Inspired by the need for more transparent and customizable personal finance tracking.

---

## Contact

For questions, suggestions, or feedback, please open an issue or contact [caleblyk12](https://github.com/caleblyk12).



