# FRED CPI Data Visualization

A Streamlit application for visualizing Consumer Price Index (CPI) data from the Federal Reserve Economic Data (FRED) database.

## Features

- Interactive visualization of multiple CPI series
- Support for viewing index values and year-over-year changes
- Shareable URLs that preserve the current view state
- Modern, responsive UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fred-cpi-visualization.git
cd fred-cpi-visualization
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your FRED API key:
```
FRED_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Configuration

The app supports the following URL parameters:
- `start_date`: Start date for the data (YYYY-MM-DD)
- `end_date`: End date for the data (YYYY-MM-DD)
- `series`: One or more CPI series to display
- `view_type`: Type of view ('Index Values', 'Year-over-Year Changes', or 'Both')

Example URL:
```
http://localhost:8501/?start_date=2020-01-01&end_date=2023-12-31&series=All+Items&series=All+Items+Less+Food+and+Energy&view_type=Both
```

## Available CPI Series

- All Items
- All Items Less Food and Energy
- Food and Beverages
- Housing
- Transportation
- Medical Care
- Recreation
- Education and Communication
- Other Goods and Services

## Deployment

This app can be deployed to Posit Connect. See the `manifest.json` file for deployment configuration.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 