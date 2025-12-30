"""
SPY Volatility Analysis (2015-2025)
====================================
Analyzes historical volatility of SPY ETF using daily OHLC data.

Metrics calculated:
- Annualized realized volatility (close-to-close)
- Parkinson volatility (high-low range based)
- Garman-Klass volatility (OHLC based)
- Average True Range (ATR)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

def load_data(filepath):
    """Load SPY OHLC data from CSV."""
    df = pd.read_csv(filepath)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    return df

def calculate_returns(df):
    """Calculate daily log returns."""
    df['returns'] = np.log(df['close'] / df['close'].shift(1))
    return df

def calculate_realized_volatility(returns, annualize=True):
    """
    Calculate realized volatility (standard deviation of returns).
    
    Parameters:
    -----------
    returns : pd.Series
        Daily returns
    annualize : bool
        If True, annualize using sqrt(252)
    """
    vol = returns.std()
    if annualize:
        vol *= np.sqrt(252)
    return vol

def calculate_parkinson_volatility(df, annualize=True):
    """
    Parkinson volatility uses high-low range.
    More efficient estimator than close-to-close.
    
    Formula: sqrt(1/(4*ln(2)) * mean((ln(high/low))^2))
    """
    hl_ratio = np.log(df['high'] / df['low'])
    vol = np.sqrt((1 / (4 * np.log(2))) * (hl_ratio ** 2).mean())
    if annualize:
        vol *= np.sqrt(252)
    return vol

def calculate_garman_klass_volatility(df, annualize=True):
    """
    Garman-Klass volatility estimator uses OHLC data.
    More efficient than Parkinson, accounts for opening jumps.
    
    Formula combines high-low and close-open ranges.
    """
    hl = np.log(df['high'] / df['low']) ** 2
    co = np.log(df['close'] / df['open']) ** 2
    vol = np.sqrt(0.5 * hl.mean() - (2 * np.log(2) - 1) * co.mean())
    if annualize:
        vol *= np.sqrt(252)
    return vol

def calculate_atr(df, period=14):
    """
    Calculate Average True Range.
    Measures market volatility.
    """
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr.mean()

def analyze_volatility_by_year(df):
    """
    Calculate various volatility metrics for each year.
    """
    df['year'] = df.index.year
    
    results = []
    
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year].copy()
        
        if len(year_data) < 10:  # Skip if insufficient data
            continue
        
        metrics = {
            'Year': year,
            'Trading Days': len(year_data),
            'Realized Volatility (%)': calculate_realized_volatility(year_data['returns']) * 100,
            'Parkinson Volatility (%)': calculate_parkinson_volatility(year_data) * 100,
            'Garman-Klass Volatility (%)': calculate_garman_klass_volatility(year_data) * 100,
            'Avg Daily Range (%)': ((year_data['high'] - year_data['low']) / year_data['close'] * 100).mean(),
            'Max Daily Return (%)': (year_data['returns'].max() * 100),
            'Min Daily Return (%)': (year_data['returns'].min() * 100),
            'Avg ATR': calculate_atr(year_data),
            'Annual Return (%)': ((year_data['close'].iloc[-1] / year_data['close'].iloc[0] - 1) * 100)
        }
        
        results.append(metrics)
    
    return pd.DataFrame(results)

def create_visualizations(df, summary_df):
    """
    Create comprehensive volatility visualization dashboard.
    """
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Year-by-Year Volatility Comparison (Bar Chart)
    ax1 = plt.subplot(3, 2, 1)
    x_pos = np.arange(len(summary_df))
    width = 0.25
    
    ax1.bar(x_pos - width, summary_df['Realized Volatility (%)'], width, 
            label='Realized Vol', alpha=0.8, color='#2E86AB')
    ax1.bar(x_pos, summary_df['Parkinson Volatility (%)'], width, 
            label='Parkinson Vol', alpha=0.8, color='#A23B72')
    ax1.bar(x_pos + width, summary_df['Garman-Klass Volatility (%)'], width, 
            label='Garman-Klass Vol', alpha=0.8, color='#F18F01')
    
    ax1.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Annualized Volatility (%)', fontsize=11, fontweight='bold')
    ax1.set_title('SPY Volatility by Year (2015-2025)', fontsize=13, fontweight='bold', pad=15)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(summary_df['Year'].astype(int), rotation=45)
    ax1.legend(loc='upper left', frameon=True)
    ax1.grid(True, alpha=0.3)
    
    # 2. Volatility Trend Over Time
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(summary_df['Year'], summary_df['Realized Volatility (%)'], 
             marker='o', linewidth=2.5, markersize=8, color='#2E86AB', label='Realized Vol')
    ax2.plot(summary_df['Year'], summary_df['Parkinson Volatility (%)'], 
             marker='s', linewidth=2.5, markersize=8, color='#A23B72', label='Parkinson Vol')
    ax2.fill_between(summary_df['Year'], summary_df['Realized Volatility (%)'], 
                      alpha=0.2, color='#2E86AB')
    ax2.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Volatility (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Volatility Trend Over Time', fontsize=13, fontweight='bold', pad=15)
    ax2.legend(loc='upper left', frameon=True)
    ax2.grid(True, alpha=0.3)
    
    # 3. Rolling 30-Day Volatility
    ax3 = plt.subplot(3, 2, 3)
    df['rolling_vol'] = df['returns'].rolling(window=30).std() * np.sqrt(252) * 100
    ax3.plot(df.index, df['rolling_vol'], linewidth=1, color='#2E86AB', alpha=0.8)
    ax3.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax3.set_ylabel('30-Day Rolling Volatility (%)', fontsize=11, fontweight='bold')
    ax3.set_title('30-Day Rolling Realized Volatility', fontsize=13, fontweight='bold', pad=15)
    ax3.axhline(y=df['rolling_vol'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {df["rolling_vol"].mean():.1f}%')
    ax3.legend(loc='upper left', frameon=True)
    ax3.grid(True, alpha=0.3)
    
    # 4. Average Daily Range by Year
    ax4 = plt.subplot(3, 2, 4)
    bars = ax4.bar(summary_df['Year'], summary_df['Avg Daily Range (%)'], 
                   color='#F18F01', alpha=0.8, edgecolor='black')
    ax4.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Average Daily Range (%)', fontsize=11, fontweight='bold')
    ax4.set_title('Average Daily Price Range by Year', fontsize=13, fontweight='bold', pad=15)
    ax4.set_xticklabels(summary_df['Year'].astype(int), rotation=45)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Annual Returns vs Volatility
    ax5 = plt.subplot(3, 2, 5)
    scatter = ax5.scatter(summary_df['Realized Volatility (%)'], 
                         summary_df['Annual Return (%)'],
                         s=200, alpha=0.6, c=summary_df['Year'], 
                         cmap='viridis', edgecolors='black', linewidth=1.5)
    
    for idx, row in summary_df.iterrows():
        ax5.annotate(str(int(row['Year'])), 
                    (row['Realized Volatility (%)'], row['Annual Return (%)']),
                    fontsize=9, ha='center', va='center', fontweight='bold')
    
    ax5.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax5.set_xlabel('Realized Volatility (%)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Annual Return (%)', fontsize=11, fontweight='bold')
    ax5.set_title('Risk-Return Profile by Year', fontsize=13, fontweight='bold', pad=15)
    ax5.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax5, label='Year')
    
    # 6. Distribution of Daily Returns by Year
    ax6 = plt.subplot(3, 2, 6)
    recent_years = summary_df['Year'].tail(5).values
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    
    for i, year in enumerate(recent_years):
        year_returns = df[df['year'] == year]['returns'].dropna() * 100
        ax6.hist(year_returns, bins=50, alpha=0.5, label=str(int(year)), 
                color=colors[i], edgecolor='black', linewidth=0.5)
    
    ax6.set_xlabel('Daily Returns (%)', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax6.set_title('Distribution of Daily Returns (Last 5 Years)', fontsize=13, fontweight='bold', pad=15)
    ax6.legend(loc='upper left', frameon=True)
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def print_summary_statistics(summary_df):
    """Print formatted summary statistics."""
    print("\n" + "="*80)
    print("SPY VOLATILITY ANALYSIS SUMMARY (2015-2025)")
    print("="*80)
    print("\n📊 YEAR-BY-YEAR VOLATILITY METRICS\n")
    print(summary_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("📈 OVERALL STATISTICS")
    print("="*80)
    print(f"Average Realized Volatility:      {summary_df['Realized Volatility (%)'].mean():.2f}%")
    print(f"Highest Volatility Year:          {summary_df.loc[summary_df['Realized Volatility (%)'].idxmax(), 'Year']:.0f} "
          f"({summary_df['Realized Volatility (%)'].max():.2f}%)")
    print(f"Lowest Volatility Year:           {summary_df.loc[summary_df['Realized Volatility (%)'].idxmin(), 'Year']:.0f} "
          f"({summary_df['Realized Volatility (%)'].min():.2f}%)")
    print(f"Average Annual Return:            {summary_df['Annual Return (%)'].mean():.2f}%")
    print(f"Best Performing Year:             {summary_df.loc[summary_df['Annual Return (%)'].idxmax(), 'Year']:.0f} "
          f"({summary_df['Annual Return (%)'].max():.2f}%)")
    print("="*80 + "\n")

def main():
    """Main execution function."""
    # Load data
    print("Loading SPY data...")
    df = load_data('/mnt/user-data/uploads/BATS_SPY__1D_17f90.csv')
    
    # Filter for 2015-2025
    df = df[(df.index.year >= 2015) & (df.index.year <= 2025)]
    
    print(f"Data loaded: {len(df)} trading days from {df.index.min().date()} to {df.index.max().date()}")
    
    # Calculate returns
    df = calculate_returns(df)
    
    # Analyze volatility by year
    print("\nCalculating volatility metrics...")
    summary_df = analyze_volatility_by_year(df)
    
    # Print summary
    print_summary_statistics(summary_df)
    
    # Create visualizations
    print("Creating visualizations...")
    fig = create_visualizations(df, summary_df)
    
    # Save outputs
    output_chart = '/mnt/user-data/outputs/spy_volatility_analysis.png'
    output_csv = '/mnt/user-data/outputs/spy_volatility_summary.csv'
    
    fig.savefig(output_chart, dpi=300, bbox_inches='tight')
    summary_df.to_csv(output_csv, index=False)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Chart saved: spy_volatility_analysis.png")
    print(f"📄 Data saved: spy_volatility_summary.csv")
    
    return summary_df, fig

if __name__ == "__main__":
    summary_df, fig = main()
    plt.show()
