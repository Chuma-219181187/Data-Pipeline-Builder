# 📊 E-Commerce Analytics Dashboard

Interactive Streamlit dashboard for US E-commerce data analysis and monitoring.

## 🌟 Features

### 📈 **Main Dashboard**
- **Real-time KPIs:** Revenue, Orders, Customers, AOV
- **Interactive Charts:** Revenue trends, state analysis, product categories
- **Dynamic Filters:** Date range, order status, geographic filters
- **Export Functionality:** Download reports as CSV

### 💰 **Sales Performance Page**
- Monthly sales trend analysis
- Seller performance metrics
- Geographic revenue distribution
- Growth rate calculations
- Top performer identification

### 👥 **Customer Analysis Page**
- **RFM Segmentation:** Recency, Frequency, Monetary analysis
- **Customer Lifetime Value:** Distribution and metrics
- **Geographic Analysis:** Customer distribution by state/city
- **Behavioral Insights:** Purchase patterns and segments

### 🔍 **Data Quality Dashboard**
- **Pipeline Health:** Success rates, data freshness, runtime metrics
- **Quality Scoring:** Completeness and uniqueness metrics
- **Missing Data Analysis:** Null value detection and visualization
- **Column Profiling:** Detailed data type and distribution analysis
- **Automated Alerts:** Quality threshold monitoring

## 🚀 Quick Start

### Option 1: Use the Launcher Script
```bash
python run_dashboard.py
```

### Option 2: Direct Streamlit Command
```bash
cd dashboard
streamlit run app.py
```

### Option 3: From Project Root
```bash
streamlit run dashboard/app.py
```

## 📱 Dashboard Navigation

The dashboard uses Streamlit's multi-page architecture:

1. **Main Dashboard** (`app.py`) - Overview and KPIs
2. **Sales Performance** (`1_Sales_Performance.py`) - Revenue analysis
3. **Customer Analysis** (`2_Customer_Analysis.py`) - Customer insights
4. **Data Quality** (`3_Data_Quality.py`) - Pipeline monitoring

## 🎛️ Interactive Features

### Filters & Controls
- **Date Range Picker:** Filter data by time period
- **Status Filter:** Filter by order status
- **Geographic Filter:** Select specific states or cities
- **Search Functionality:** Find specific records
- **Export Options:** Download filtered results

### Real-time Updates
- **Auto-refresh:** Data updates when source changes
- **Session State:** Maintains filters across pages
- **Caching:** Optimized performance with data caching

## 📊 Key Metrics Tracked

### Business KPIs
- Total Revenue & Growth
- Order Count & Trends
- Customer Acquisition
- Average Order Value
- Delivery Performance
- Customer Satisfaction (Review Scores)

### Operational Metrics
- Data Pipeline Success Rate
- Data Freshness & Quality
- Processing Time & Performance
- Error Rates & Alerts

## 🎨 Visualization Types

- **Line Charts:** Trend analysis and time series
- **Bar Charts:** Comparative analysis and rankings
- **Pie Charts:** Distribution and composition
- **Scatter Plots:** Correlation and clustering
- **Heatmaps:** Correlation matrices and patterns
- **Geographic Maps:** Spatial distribution analysis
- **Histograms:** Distribution analysis
- **Gauge Charts:** KPI performance indicators

## 🛠️ Technical Architecture

### Data Flow
```
Raw Data → ETL Pipeline → Validated Data → Dashboard Cache → Interactive Visualizations
```

### Components
- **Data Layer:** Integration with ETL extraction module
- **Processing Layer:** Pandas for data manipulation
- **Visualization Layer:** Plotly for interactive charts
- **UI Layer:** Streamlit for web interface
- **Caching Layer:** Streamlit caching for performance

### Dependencies
```python
streamlit>=1.28.0    # Web framework
plotly>=5.14.0       # Interactive charts
pandas>=2.0.0        # Data manipulation
numpy>=1.24.0        # Numerical computing
```

## 🎯 Business Use Cases

### For Executives
- **Revenue Dashboard:** Monitor business performance
- **Geographic Expansion:** Identify growth opportunities
- **Customer Insights:** Understand customer behavior
- **Performance Tracking:** Track KPIs and trends

### For Operations Team
- **Data Quality Monitoring:** Ensure data reliability
- **Pipeline Health:** Monitor ETL performance
- **Alert Management:** Respond to quality issues
- **Process Optimization:** Improve data workflows

### For Marketing Team
- **Customer Segmentation:** Target specific customer groups
- **Campaign Analysis:** Measure marketing effectiveness
- **Geographic Targeting:** Focus on high-value regions
- **Customer Journey:** Analyze purchase patterns

### For Sales Team
- **Performance Tracking:** Monitor sales metrics
- **Seller Analysis:** Identify top performers
- **Territory Management:** Optimize geographic coverage
- **Opportunity Identification:** Find growth areas

## 🔧 Customization Options

### Adding New Pages
```python
# Create new file: pages/4_New_Analysis.py
import streamlit as st

st.title("New Analysis")
# Add your analysis here
```

### Custom Visualizations
```python
import plotly.express as px

def create_custom_chart(data):
    fig = px.custom_chart(data)
    return fig

st.plotly_chart(create_custom_chart(data))
```

### New Metrics
```python
def calculate_new_metric(data):
    # Your calculation logic
    return metric_value

st.metric("New Metric", calculate_new_metric(data))
```

## 📱 Mobile Responsiveness

The dashboard is optimized for:
- **Desktop:** Full feature set with multi-column layouts
- **Tablet:** Responsive column stacking
- **Mobile:** Single column layout with touch-friendly controls

## 🔒 Security Features

- **No Data Storage:** Dashboard operates on cached data only
- **Session Isolation:** Each user session is independent
- **Input Validation:** All user inputs are validated
- **Error Handling:** Graceful error recovery

## 🚀 Performance Optimization

- **Data Caching:** Expensive operations are cached
- **Lazy Loading:** Charts load on demand
- **Efficient Queries:** Optimized data processing
- **Memory Management:** Automatic cleanup of large datasets

## 🐛 Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check if Streamlit is installed
pip install streamlit

# Run from correct directory
cd data-pipeline-project
python run_dashboard.py
```

**Data not loading:**
- Ensure sample data exists in `data/sample/` directory
- Check logs in `logs/` directory for errors
- Verify ETL pipeline completed successfully

**Charts not displaying:**
```bash
# Install required visualization libraries
pip install plotly>=5.14.0
```

**Performance issues:**
- Clear Streamlit cache: Press 'C' in the running dashboard
- Reduce data size with date range filters
- Close unused browser tabs

## 📈 Future Enhancements

### Planned Features
- **Real-time Data Streaming:** Live data updates
- **Advanced Analytics:** Machine learning insights
- **Custom Dashboards:** User-configurable layouts
- **API Integration:** External data sources
- **Automated Reporting:** Scheduled report generation

### Integration Opportunities
- **Database Connectivity:** Direct database queries
- **Cloud Deployment:** AWS/Azure hosting
- **Authentication:** User login and permissions
- **Notifications:** Alert system integration

---

## 📞 Support

For dashboard issues or feature requests:
- Check the main project README
- Review error logs in `logs/` directory
- Verify data pipeline status
- Contact the development team

**Built with ❤️ using Streamlit and Plotly**