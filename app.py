import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fredapi import Fred
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import urllib.parse

# Load environment variables
load_dotenv()

# Initialize FRED API with environment variable
fred_api_key = os.getenv('FRED_API_KEY')
if not fred_api_key:
    st.error("""
        FRED API key not found. Please set the FRED_API_KEY environment variable.
        For local development, create a .env.local file with:
        FRED_API_KEY=your_api_key_here
    """)
    st.stop()

fred = Fred(api_key=fred_api_key)

# Define available CPI series
CPI_SERIES = {
    'All Items': 'CPIAUCSL',
    'All Items Less Food and Energy': 'CPILFESL',
    'Food and Beverages': 'CPIFABSL',
    'Housing': 'CPIHOSSL',
    'Transportation': 'CPITRNSL',
    'Medical Care': 'CPIMEDSL',
    'Recreation': 'CPIRECSL',
    'Education and Communication': 'CPIEDUSL',
    'Other Goods and Services': 'CPIOGSSL'
}

# Define a consistent color palette
COLOR_PALETTE = [
    '#1f77b4',  # blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22',  # yellow-green
]

def get_cpi_data(series_id, start_date, end_date):
    """Fetch CPI data from FRED"""
    try:
        df = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        return pd.DataFrame(df, columns=['value'])
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def calculate_yoy_change(df):
    """Calculate year-over-year percentage change"""
    return df['value'].pct_change(periods=12) * 100

def create_plot(df_dict, view_type):
    """Create interactive Plotly chart with multiple series"""
    fig = go.Figure()
    
    # Get color for each series
    series_colors = {series: COLOR_PALETTE[i % len(COLOR_PALETTE)] 
                    for i, series in enumerate(df_dict.keys())}
    
    if view_type in ['Index Values', 'Both']:
        # Add absolute values
        for series_name, df in df_dict.items():
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['value'],
                name=f'{series_name} (Index)',
                line=dict(
                    width=2,
                    color=series_colors[series_name],
                    dash='dot' if view_type == 'Both' else 'solid'
                )
            ))
    
    if view_type in ['Year-over-Year Changes', 'Both']:
        # Add year-over-year change
        for series_name, df in df_dict.items():
            yoy = calculate_yoy_change(df)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=yoy,
                name=f'{series_name} (YoY %)',
                line=dict(
                    dash='solid',
                    width=2,
                    color=series_colors[series_name]
                ),
                yaxis='y2' if view_type == 'Both' else 'y'
            ))
    
    if view_type == 'Both':
        # Update layout for dual y-axes
        fig.update_layout(
            yaxis=dict(
                title='Index Value'
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                title='Year-over-Year Change (%)'
            )
        )
    else:
        fig.update_layout(
            yaxis_title='Index Value' if view_type == 'Index Values' else 'Year-over-Year Change (%)'
        )
    
    fig.update_layout(
        title='CPI Data',
        xaxis_title='Date',
        hovermode='x unified',
        height=600
    )
    
    return fig

def get_url_params():
    """Get parameters from URL"""
    try:
        # Get parameters directly from Streamlit
        start_date_str = st.query_params.get('start_date', None)
        end_date_str = st.query_params.get('end_date', None)
        series = st.query_params.get('series', [])
        view_type = st.query_params.get('view_type', 'Index Values')
        
        # Parse dates if they exist
        start_date = None
        end_date = None
        if start_date_str and isinstance(start_date_str, str) and len(start_date_str) > 5:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                st.warning(f"Invalid start date format: {start_date_str}")
        
        if end_date_str and isinstance(end_date_str, str) and len(end_date_str) > 5:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                st.warning(f"Invalid end date format: {end_date_str}")
            
        # Decode URL-encoded series names and validate
        valid_series = []
        
        # Get all series parameters
        all_series = st.query_params.get_all('series')
        for s in all_series:
            if isinstance(s, str):
                decoded_series = s.replace('+', ' ')
                if decoded_series in CPI_SERIES:
                    valid_series.append(decoded_series)
        
        # If no valid series found, use defaults
        if not valid_series:
            valid_series = ['All Items', 'All Items Less Food and Energy']
            
        # Validate view type
        if not isinstance(view_type, str) or view_type not in ['Index Values', 'Year-over-Year Changes', 'Both']:
            view_type = 'Index Values'
            
        return {
            'start_date': start_date,
            'end_date': end_date,
            'series': valid_series,
            'view_type': view_type
        }
    except Exception as e:
        st.warning(f"Error parsing URL parameters: {str(e)}")
        return {
            'start_date': None,
            'end_date': None,
            'series': ['All Items', 'All Items Less Food and Energy'],
            'view_type': 'Index Values'
        }

def generate_share_url(start_date, end_date, selected_series, view_type):
    """Generate a shareable URL with current state"""
    # Get the base URL from the current URL
    current_url = st.query_params.get('_url', '')
    
    # Remove any existing query parameters from the base URL
    base_url = current_url.split('?')[0] if current_url else ''
    
    # Prepare parameters
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'series': selected_series,
        'view_type': view_type
    }
    
    # Generate the full URL
    return f"{base_url}?{urllib.parse.urlencode(params, doseq=True)}"

# Streamlit UI
st.set_page_config(
    page_title="FRED CPI Data Visualization",
    page_icon="📈",
    layout="wide"
)

st.title('FRED CPI Data Visualization')

# Get URL parameters
url_params = get_url_params()

# Time period selection
col1, col2 = st.columns(2)
with col1:
    default_start = url_params['start_date'] if url_params['start_date'] else datetime.now() - timedelta(days=365*5)
    start_date = st.date_input(
        "Start Date",
        default_start,
        min_value=datetime(1947, 1, 1)  # FRED CPI data starts from 1947
    )
with col2:
    default_end = url_params['end_date'] if url_params['end_date'] else datetime.now()
    end_date = st.date_input(
        "End Date",
        default_end,
        min_value=start_date
    )

# Series selection
default_series = url_params['series'] if url_params['series'] else ['All Items', 'All Items Less Food and Energy']
selected_series = st.multiselect(
    'Select CPI Series',
    list(CPI_SERIES.keys()),
    default=default_series
)

# View type selection
default_view = url_params['view_type']
view_type = st.radio(
    'Select View Type',
    ['Index Values', 'Year-over-Year Changes', 'Both'],
    index=['Index Values', 'Year-over-Year Changes', 'Both'].index(default_view)
)

# Share button
if st.button('Share Current View'):
    share_url = generate_share_url(start_date, end_date, selected_series, view_type)
    st.markdown(f"Share this view: [Copy Link]({share_url})")
    st.code(share_url)

# Fetch and display data
if selected_series:
    df_dict = {}
    for series_name in selected_series:
        series_id = CPI_SERIES[series_name]
        df = get_cpi_data(series_id, start_date, end_date)
        if df is not None:
            df_dict[series_name] = df
    
    if df_dict:
        fig = create_plot(df_dict, view_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display raw data
        if st.checkbox('Show Raw Data'):
            # Combine all dataframes
            combined_df = pd.concat([df for df in df_dict.values()], axis=1)
            combined_df.columns = [name for name in df_dict.keys()]
            
            # Add YoY changes if requested
            if view_type in ['Year-over-Year Changes', 'Both']:
                yoy_df = pd.DataFrame()
                for series_name, df in df_dict.items():
                    yoy_df[f'{series_name} (YoY %)'] = calculate_yoy_change(df)
                combined_df = pd.concat([combined_df, yoy_df], axis=1)
            
            st.dataframe(combined_df) 