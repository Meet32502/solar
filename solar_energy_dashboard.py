import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# Set page config
st.set_page_config(
    page_title="Solar Energy Production Analysis",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #FF6B35;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.sub-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: #2E86AB;
    margin-bottom: 1rem;
    border-bottom: 2px solid #FF6B35;
    padding-bottom: 0.5rem;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}

.info-box {
    background-color: #f8f9fa;
    border-left: 4px solid #FF6B35;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 5px;
}

.stMetric {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stMetric > div {
    color: #000000 !important;
}

.stMetric > div > div {
    color: #000000 !important;
}

.stMetric label {
    color: #000000 !important;
}

.stMetric [data-testid="metric-container"] {
    color: #000000 !important;
}

.stMetric [data-testid="metric-container"] > div {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)

# Solar Energy Data Generation Code
@st.cache_data
def load_solar_data():
    # Feature ranges for all seasons
    feature_ranges = {
        'summer': {
            'irradiance': (600, 1000),
            'humidity': (10, 50),
            'wind_speed': (0, 5),
            'ambient_temperature': (30, 45),
            'tilt_angle': (10, 40),
        },
        'winter': {
            'irradiance': (300, 700),
            'humidity': (30, 70),
            'wind_speed': (1, 6),
            'ambient_temperature': (5, 20),
            'tilt_angle': (10, 40),
        },
        'monsoon': {
            'irradiance': (100, 600),
            'humidity': (70, 100),
            'wind_speed': (2, 8),
            'ambient_temperature': (20, 35),
            'tilt_angle': (10, 40),
        }
    }

    # All 12 months with exact days (365 days total)
    months_days = {
        'January': 31, 'February': 28, 'March': 31, 'April': 30,
        'May': 31, 'June': 30, 'July': 31, 'August': 31,
        'September': 30, 'October': 31, 'November': 30, 'December': 31
    }

    # Month to season mapping
    month_to_season = {
        'January': 'winter', 'February': 'winter', 'March': 'summer', 'April': 'summer',
        'May': 'summer', 'June': 'summer', 'July': 'monsoon', 'August': 'monsoon',
        'September': 'monsoon', 'October': 'monsoon', 'November': 'winter', 'December': 'winter'
    }

    # kWh calculation functions
    def calc_kwh_summer(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
        return (0.25 * irradiance - 0.05 * humidity + 0.02 * wind_speed + 0.1 * ambient_temp - 0.03 * abs(tilt_angle - 30))

    def calc_kwh_winter(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
        return (0.18 * irradiance - 0.03 * humidity + 0.015 * wind_speed + 0.08 * ambient_temp - 0.02 * abs(tilt_angle - 30))

    def calc_kwh_monsoon(irradiance, humidity, wind_speed, ambient_temp, tilt_angle):
        return (0.15 * irradiance - 0.1 * humidity + 0.01 * wind_speed + 0.05 * ambient_temp - 0.04 * abs(tilt_angle - 30))

    def get_kwh_calculator(season):
        if season == 'summer':
            return calc_kwh_summer
        elif season == 'winter':
            return calc_kwh_winter
        elif season == 'monsoon':
            return calc_kwh_monsoon

    # Generate complete 365-day dataset
    def generate_complete_year_data():
        data = []
        day_counter = 1
        for month, days in months_days.items():
            season = month_to_season[month]
            calc_kwh_func = get_kwh_calculator(season)
            
            for day in range(days):
                irr = np.random.uniform(*feature_ranges[season]['irradiance'])
                hum = np.random.uniform(*feature_ranges[season]['humidity'])
                wind = np.random.uniform(*feature_ranges[season]['wind_speed'])
                temp = np.random.uniform(*feature_ranges[season]['ambient_temperature'])
                tilt = np.random.uniform(*feature_ranges[season]['tilt_angle'])

                kwh = calc_kwh_func(irr, hum, wind, temp, tilt)

                data.append({
                    'day': day_counter,
                    'irradiance': round(irr, 2),
                    'humidity': round(hum, 2),
                    'wind_speed': round(wind, 2),
                    'ambient_temperature': round(temp, 2),
                    'tilt_angle': round(tilt, 2),
                    'kwh': round(kwh, 2),
                    'season': season,
                    'month': month
                })
                day_counter += 1
        return pd.DataFrame(data)

    return generate_complete_year_data()

# Load data
df = load_solar_data()

# Main Dashboard
st.markdown('<h1 class="main-header">☀️ Solar Energy Production Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Filters
selected_seasons = st.sidebar.multiselect(
    "🌦️ Select Seasons",
    options=df['season'].unique(),
    default=df['season'].unique()
)

selected_months = st.sidebar.multiselect(
    "📅 Select Months",
    options=df['month'].unique(),
    default=df['month'].unique()
)

# Filter data
filtered_df = df[
    (df['season'].isin(selected_seasons)) & 
    (df['month'].isin(selected_months))
]

# Key Metrics Row
st.markdown('<h2 class="sub-header">📊 Key Performance Metrics</h2>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🔋 Total Energy (kWh)",
        value=f"{filtered_df['kwh'].sum():,.0f}",
        delta=f"{filtered_df['kwh'].sum() - df['kwh'].mean() * len(filtered_df):,.0f}"
    )

with col2:
    st.metric(
        label="⚡ Average Daily Output",
        value=f"{filtered_df['kwh'].mean():.1f} kWh",
        delta=f"{filtered_df['kwh'].mean() - df['kwh'].mean():.1f}"
    )

with col3:
    st.metric(
        label="🌞 Peak Performance",
        value=f"{filtered_df['kwh'].max():.1f} kWh",
        delta=f"{filtered_df['kwh'].max() - filtered_df['kwh'].min():.1f}"
    )

with col4:
    st.metric(
        label="☀️ Avg Irradiance",
        value=f"{filtered_df['irradiance'].mean():.0f} W/m²",
        delta=f"{filtered_df['irradiance'].mean() - df['irradiance'].mean():.0f}"
    )

with col5:
    st.metric(
        label="🌡️ Avg Temperature",
        value=f"{filtered_df['ambient_temperature'].mean():.1f}°C",
        delta=f"{filtered_df['ambient_temperature'].mean() - df['ambient_temperature'].mean():.1f}"
    )

# Main Charts Row
st.markdown('<h2 class="sub-header">📈 Energy Production Analysis</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Daily Energy Production Timeline
    fig_timeline = px.line(
        filtered_df, 
        x='day', 
        y='kwh',
        color='season',
        title='Daily Energy Production Timeline',
        labels={'kwh': 'Energy Output (kWh)', 'day': 'Day of Year'},
        color_discrete_map={'summer': '#FF6B35', 'winter': '#2E86AB', 'monsoon': '#A23B72'}
    )
    fig_timeline.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    # Seasonal Performance Comparison
    seasonal_avg = filtered_df.groupby('season')['kwh'].mean().reset_index()
    fig_seasonal = px.bar(
        seasonal_avg,
        x='season',
        y='kwh',
        title='Average Energy Production by Season',
        labels={'kwh': 'Average Energy (kWh)', 'season': 'Season'},
        color='season',
        color_discrete_map={'summer': '#FF6B35', 'winter': '#2E86AB', 'monsoon': '#A23B72'}
    )
    fig_seasonal.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)

# Environmental Factors Analysis
st.markdown('<h2 class="sub-header">🌡️ Environmental Factors Impact</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Irradiance vs Energy Output
    fig_irr = px.scatter(
        filtered_df,
        x='irradiance',
        y='kwh',
        color='season',
        title='Irradiance vs Energy Output',
        labels={'irradiance': 'Irradiance (W/m²)', 'kwh': 'Energy Output (kWh)'},
        color_discrete_map={'summer': '#FF6B35', 'winter': '#2E86AB', 'monsoon': '#A23B72'},
        opacity=0.6
    )
    fig_irr.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig_irr, use_container_width=True)

with col2:
    # Temperature vs Energy Output
    fig_temp = px.scatter(
        filtered_df,
        x='ambient_temperature',
        y='kwh',
        color='season',
        title='Temperature vs Energy Output',
        labels={'ambient_temperature': 'Temperature (°C)', 'kwh': 'Energy Output (kWh)'},
        color_discrete_map={'summer': '#FF6B35', 'winter': '#2E86AB', 'monsoon': '#A23B72'},
        opacity=0.6
    )
    fig_temp.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig_temp, use_container_width=True)

# Monthly Analysis
st.markdown('<h2 class="sub-header">📅 Monthly Performance Analysis</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Monthly Average Energy Production
    monthly_avg = filtered_df.groupby('month')['kwh'].mean().reset_index()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_avg['month'] = pd.Categorical(monthly_avg['month'], categories=month_order, ordered=True)
    monthly_avg = monthly_avg.sort_values('month')
    
    fig_monthly = px.bar(
        monthly_avg,
        x='month',
        y='kwh',
        title='Average Monthly Energy Production',
        labels={'kwh': 'Average Energy (kWh)', 'month': 'Month'},
        color='kwh',
        color_continuous_scale='RdYlBu_r'
    )
    fig_monthly.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

with col2:
    # Energy Production Distribution
    fig_dist = px.histogram(
        filtered_df,
        x='kwh',
        nbins=30,
        title='Energy Production Distribution',
        labels={'kwh': 'Energy Output (kWh)', 'count': 'Frequency'},
        color_discrete_sequence=['#FF6B35']
    )
    fig_dist.update_layout(
        title_font_size=16,
        title_font_color='#2E86AB',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# Correlation Analysis
st.markdown('<h2 class="sub-header">🔗 Environmental Factors Correlation</h2>', unsafe_allow_html=True)

# Calculate correlation matrix
corr_cols = ['irradiance', 'humidity', 'wind_speed', 'ambient_temperature', 'tilt_angle', 'kwh']
corr_matrix = filtered_df[corr_cols].corr()

# Create heatmap
fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    aspect="auto",
    title="Correlation Matrix of Environmental Factors",
    color_continuous_scale='RdBu_r',
    labels=dict(color="Correlation")
)
fig_corr.update_layout(
    title_font_size=16,
    title_font_color='#2E86AB',
    height=500
)
st.plotly_chart(fig_corr, use_container_width=True)

# Summary Statistics
st.markdown('<h2 class="sub-header">📋 Statistical Summary</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Descriptive Statistics")
    st.dataframe(
        filtered_df.describe().round(2),
        use_container_width=True
    )

with col2:
    st.markdown("### 🎯 Seasonal Performance Summary")
    seasonal_summary = filtered_df.groupby('season').agg({
        'kwh': ['mean', 'std', 'min', 'max'],
        'irradiance': 'mean',
        'humidity': 'mean',
        'ambient_temperature': 'mean'
    }).round(2)
    st.dataframe(seasonal_summary, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        <p>🌟 Solar Energy Production Analysis Dashboard | Built with Streamlit & Plotly</p>
        <p>📧 For technical support or questions, contact your system administrator</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Info sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About This Dashboard")
st.sidebar.info(
    """
    This dashboard analyzes solar energy production patterns across different seasons:
    
    🌞 **Summer**: High irradiance, optimal performance
    
    ❄️ **Winter**: Moderate irradiance, steady output
    
    🌧️ **Monsoon**: Variable conditions, humidity impact
    
    Use the filters above to explore specific time periods and seasonal patterns.
    """
)

st.sidebar.markdown("### 🔧 Technical Details")
st.sidebar.markdown(
    """
    - **Dataset**: 365 days of synthetic solar data
    - **Factors**: Irradiance, humidity, wind, temperature, tilt
    - **Seasons**: Summer, Winter, Monsoon
    - **Update**: Real-time filtering and analysis
    """
)
