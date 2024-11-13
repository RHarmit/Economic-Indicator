import pandas as pd
import matplotlib.pyplot as plt
import requests

# Function to fetch data from the World Bank API
def fetch_world_bank_data(indicator, country_code, start_year, end_year):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?date={start_year}:{end_year}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 1 and 'value' in data[1][0]:
            df = pd.DataFrame(data[1])
            df = df[['date', 'value']].dropna()
            df.columns = ['Year', indicator]
            df['Year'] = pd.to_datetime(df['Year'], format='%Y')
            df.set_index('Year', inplace=True)
            return df
    return pd.DataFrame()

# User inputs for dynamic analysis
country_code = input("Enter the country code (e.g., 'IN' for India): ").upper()
start_year = input("Enter the start year (e.g., 2010): ")
end_year = input("Enter the end year (e.g., 2023): ")

# Economic indicators to analyze
indicators = {
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth (%)',
    'FP.CPI.TOTL.ZG': 'Inflation Rate (%)',
    'NE.CON.GOVT.ZS': 'Govt Expenditure (% of GDP)'
}

# Fetch and merge data
data_frames = [fetch_world_bank_data(indicator, country_code, start_year, end_year).rename(columns={indicator: name})
               for indicator, name in indicators.items()]
df_merged = pd.concat(data_frames, axis=1).dropna() if data_frames else pd.DataFrame()

if not df_merged.empty:
    # Calculate key statistics (mean, median, standard deviation, CAGR)
    stats = {
        column: {
            "Mean": df_merged[column].mean(),
            "Median": df_merged[column].median(),
            "Std Dev": df_merged[column].std(),
            "CAGR (%)": ((df_merged[column].iloc[-1] / df_merged[column].iloc[0]) ** (1 / (df_merged.index[-1].year - df_merged.index[0].year)) - 1) * 100
        }
        for column in df_merged.columns
    }

    # Display statistics
    print("\nMacroeconomic Statistics:")
    for indicator, values in stats.items():
        print(f"\n{indicator}:")
        for stat, value in values.items():
            print(f"  {stat}: {value:.2f}")

    # Plotting data with enhanced visuals
    plt.figure(figsize=(12, 8))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Distinct colors for each indicator

    for i, column in enumerate(df_merged.columns):
        plt.plot(df_merged.index, df_merged[column], marker='o', color=colors[i], label=column, linewidth=2)

    # Beautify plot
    plt.title(f'Macroeconomic Indicators for {country_code} ({start_year} - {end_year})', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Percentage (%)', fontsize=14)
    plt.legend(loc='best', fontsize=12)
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    plt.show()

else:
    print("No data available for the specified parameters.")
