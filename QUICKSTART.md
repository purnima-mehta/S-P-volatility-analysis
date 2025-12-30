# 🚀 Quick Start Guide

Get up and running with SPY Volatility Analysis in 5 minutes!

## Option 1: Automated Setup (Recommended)

### macOS / Linux:
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python spy_volatility_analysis.py
```

### Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python spy_volatility_analysis.py
```

## Option 2: Manual Setup

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn
```

### 2. Prepare Your Data
Place your CSV file with SPY data in the project directory. The CSV should have these columns:
- `time` (date in YYYY-MM-DD format)
- `open` (opening price)
- `high` (daily high)
- `low` (daily low)
- `close` (closing price)

### 3. Update File Path (if needed)
Edit `spy_volatility_analysis.py` line 210:
```python
df = load_data('your_file_name.csv')  # Change this to your CSV file name
```

### 4. Run the Analysis
```bash
python spy_volatility_analysis.py
```

## What You'll Get

After running the script, you'll see:

1. **Console Output**: 
   - Summary statistics table
   - Key findings and metrics
   
2. **Generated Files**:
   - `spy_volatility_analysis.png` - Beautiful 6-panel dashboard
   - `spy_volatility_summary.csv` - Year-by-year statistics

## Customization Examples

### Change Date Range
```python
# Analyze only 2020-2025
df = df[(df.index.year >= 2020) & (df.index.year <= 2025)]
```

### Adjust Rolling Window
```python
# Use 60-day rolling window instead of 30-day
df['rolling_vol'] = df['returns'].rolling(window=60).std() * np.sqrt(252)
```

### Different Ticker
```python
# Analyze QQQ instead of SPY
df = load_data('QQQ_data.csv')
```

### Save with Different Name
```python
fig.savefig('my_custom_analysis.png', dpi=300, bbox_inches='tight')
```

## Understanding the Output

### 📊 Panel 1: Year-by-Year Volatility
Compares three different volatility measures across years:
- **Realized Vol**: Standard close-to-close volatility
- **Parkinson Vol**: Uses high-low range (more efficient)
- **Garman-Klass Vol**: Uses OHLC data (most efficient)

### 📈 Panel 2: Volatility Trend
Shows how volatility has evolved over time with a filled area chart.

### 🎢 Panel 3: Rolling Volatility
30-day rolling window showing short-term volatility changes. Spikes indicate periods of market stress.

### 📏 Panel 4: Average Daily Range
Shows how much SPY typically moves within a single day for each year.

### 💰 Panel 5: Risk-Return Profile
Scatter plot showing the relationship between volatility (risk) and returns. Each point is a year.

### 📊 Panel 6: Return Distribution
Histogram showing the distribution of daily returns for the last 5 years.

## Common Issues

### ImportError: No module named 'pandas'
**Solution**: Install dependencies with `pip install -r requirements.txt`

### FileNotFoundError
**Solution**: Make sure your CSV file is in the correct location and update the file path in the script.

### Empty Plot or No Data
**Solution**: Check that your CSV has the correct column names and date format.

## Next Steps

- ⭐ Star the repository if you find it useful
- 🐛 Report bugs in the Issues section
- 💡 Suggest new features
- 🤝 Contribute improvements (see CONTRIBUTING.md)

## Getting Help

- 📖 Read the full README.md for detailed information
- 🔍 Check existing Issues for similar problems
- ❓ Open a new Issue if you need help

Happy analyzing! 📊🚀
