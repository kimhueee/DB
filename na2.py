import pandas as pd
import streamlit as st
import time
import plotly.express as px
import plotly.graph_objects as go


        # FETCHING DATA FROM GOOGLE SHEETS: ===================================
@st.cache_data(ttl=3)
def fetch_data(sheet):
    sheet_id = "1Sd1HUFATS2FihSU3fDZTWp8SVGM14D3iTi2xBckaMr8"
    sheets = sheet
    timestamp = int(time.time())  # Force Google Sheets refresh
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheets}&t={timestamp}"    
    return pd.read_csv(sheet_url)

        # AUTO REFRESHING DATA: ===============================================
def auto_refresh(interval=3):
    time.sleep(interval)
    st.rerun()
    
        # VISUALIZATION: ======================================================
# 1. Col 1, sub- Col 1 and sub- Col 2 Total SKU + Total Missing SKU by SSO/ SFO:
def piebytab(piebytabdf, title):
    teamse = piebytabdf['dept'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=teamse.index,  # dept names
        values=teamse.values,  # counts
        hole=0.5,  # Donut-style
        textinfo='value',
        textfont_size=30,
        domain={'x': [0, 1], 'y': [0, 1]})])
    
    fig.update_layout(
        title_text=title,
        height=600,
        width=600,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        annotations=[dict(text=f"{len(piebytabdf.index)}", 
                          x=0.5, y=0.5, 
                          font=dict(size=70, color="black"), showarrow=False)])
        
    st.plotly_chart(fig)
    
# 2. Col 1, Total Missing SKU by Field by SSO/ SFO:
def barbytab(barbytabdf):
    
    barbytabdf = barbytabdf.reset_index()
    for col in ['SSO', 'SFO']:
        if col not in barbytabdf.columns:
            barbytabdf[col] = 0

    barbytabdf['Total'] = barbytabdf['SSO'] + barbytabdf['SFO']
    barbytabdf = barbytabdf[barbytabdf['Total'] > 0] # Filter missbyteam rows where both 'SSO' and 'SFO' are zero
    barbytabdf = barbytabdf.sort_values(by='Total', ascending=True) # Sort by 'Total' in descending order
    
    if not barbytabdf.empty:                
        fig = px.bar(barbytabdf, y='index', x=['SSO', 'SFO'],
        text_auto=True, barmode='stack', height=1030, labels={"index": "", "value": ""})
        
        fig.update_layout(
        title_text='Missing Field Break- down by Team',
        height=800,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=0),  # Reduce margins
        xaxis=dict(
            automargin=True, 
            fixedrange=True, 
            zeroline=False,
            showgrid=False),
        yaxis=dict(
            automargin=True, 
            showgrid=False,
            categoryorder="total ascending", tickfont=dict(color="black")),
        uniformtext_minsize=8, uniformtext_mode="hide")

        fig.update_traces(textfont_size=20, textfont_color="black")                 
        
        st.plotly_chart(fig)

# Function to draw pie chart of each department (Number of Sufficient vs Missing SKU):
def piebydept(dept, piebydeptdf):
    
    custom_colors = ['#c40202', '#1abd3b']
    
    fig = go.Figure(data=[go.Pie(
        labels=piebydeptdf[dept].drop('Total by Dept').index,  # dept names
        values=piebydeptdf[dept].drop('Total by Dept').values,  # counts
        hole=0.5,  # Donut-style
        textinfo='value',
        textfont_size=30,
        domain={'x': [0, 1], 'y': [0, 1]},
        marker=dict(colors=custom_colors))])
    
    fig.update_layout(
        title = 'Sufficient/ Missing SKU Break- down',
        height=600,
        width=600,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        annotations=[dict(text=f"{piebydeptdf[dept]['Total by Dept']}", 
                          x=0.5, y=0.5, 
                          font=dict(size=70, color="black"), showarrow=False)])
    st.plotly_chart(fig)

# Function to draw bar chart of each department (Number of Missing of Each field):
def barbydept(dept, barbydeptdf):
    if dept not in barbydeptdf['dept'].unique():
        # Nếu không có dữ liệu cho dept đó, tạo DataFrame trống với 1 dòng "No Data"
        missbyfield = pd.DataFrame({
            'index': ['No Missing Field'],
            dept: [0]
        })
    else:
        # Tính số lượng NA theo field với điều kiện dept
        missbyfield = barbydeptdf[barbydeptdf['dept'] == dept].isna().sum()
        missbyfield = missbyfield.to_frame(name=dept)
        missbyfield = missbyfield[missbyfield[dept] > 0].reset_index()
        missbyfield = missbyfield.sort_values(by=dept, ascending=True)
    
    fig = px.bar(missbyfield, y='index', x=dept,
    text_auto=True, height=650, width=500, labels={"index": "", "value": ""})    
    
    fig.update_traces(
    textfont_size=20,
    textfont_color="black",
    textposition="outside",  # Show text labels above bars
    marker=dict(
        color='#c40202',
        line=dict(width=1, color="#e62003"),  # Add border
        opacity=0.9,  # Slight transparency
        cornerradius=60),)
    fig.update_layout(title_text='Missing Field Break- down',
        xaxis=dict(range=[0, max(missbyfield[dept]) * 1.5]),
        yaxis=dict(tickfont=dict(color="black")))  # Adjust margins as needed

    st.plotly_chart(fig, use_container_width=True)

# Function to display dataframe of each department (group SKU by the same group of Missing Field)
def detailbysku(dept, detailbyskudf, key):    
    detailbyskudf.set_index(key, inplace=True)
    missing_patterns = detailbyskudf[detailbyskudf['dept'] == dept].isna().apply(lambda row: tuple(row[row].index), axis=1)
    def group_by_pic(df, missing_patterns):
        grouped_data = {}
        for (sku, missing_cols), pic in zip(missing_patterns.items(), detailbyskudf.loc[missing_patterns.index, 'PIC']):
            grouped_data.setdefault((pic, missing_cols), []).append(sku)
        return grouped_data
    grouped_skus = group_by_pic(detailbyskudf, missing_patterns)
    output_df = pd.DataFrame(
        [(pic, ', '.join(missing_cols), ', '.join(skus)) for (pic, missing_cols), skus in grouped_skus.items() if missing_cols],
        columns=["PIC", "Missing Columns", "SKUs"])
    output_df["Missing Count"] = output_df["Missing Columns"].apply(lambda x: len(x.split(", ")) if x else 0)
    output_df = output_df.sort_values(by=["PIC", "Missing Count"], ascending=[True, False]).drop(columns=["Missing Count"])
    output_df.set_index('PIC', inplace=True)    
    with st.expander("Group of Missing"):
        st.dataframe(output_df, use_container_width = True)

# Function to display dataframe of each department (group SKU by Missing Field and PIC)
def filterfield(dept, filferfielddf, filferfieldmask, key):
    st.subheader("Detail Missing Field by Team")
    outfildf = filferfielddf[filferfieldmask]
    selected_list = outfildf[outfildf['dept'] == dept].columns[outfildf.isna().any()].tolist()
    selected_column = st.selectbox("Select Field to view Missing SKU by PIC", selected_list, key=f"select_{dept}")
    filtered_df = outfildf[outfildf['dept'] == dept][['PIC', key, selected_column]]                     
    filtered_df[selected_column] = filtered_df[selected_column].isna()
    filtered_df = filtered_df[filtered_df[selected_column]]
    # Group by PIC and count blank SKUs and total SKUs
    summary_df = filtered_df.groupby("PIC").agg(
        MissingCount=(key, "count"),
        SKU=(key, lambda x: ", ".join(x))
    ).reset_index()
    summary_df = summary_df.sort_values(by='MissingCount', ascending=False)
    summary_df.set_index('PIC', inplace=True)
    st.dataframe(summary_df, use_container_width = True)

    # Streamlit UI
st.set_page_config(page_title="Missing Values", layout="wide")
st.toast("Auto-refresh enabled. Data updates every setting seconds.", icon="🔄")
placeholder = st.empty() # Create a placeholder for real-time updates

# while True:
picdept = fetch_data('dept')

datasku = fetch_data('propost')
datasku = datasku[~datasku['SKU'].isna()]

dataskusup = fetch_data('provenpost')
dataskusup = dataskusup[dataskusup['SKU'].notna() & (dataskusup['SKU_SupCode'] != "_")]

    # PRODUCT MASTER ==============================================================================================
mancol = ['SKU', 'PIC', 'Idea Code', 'Product Name', 'Product Net Weight - Drawing (kg)',
          'No# of IB - Drawing', 'IB Length - Drawing (cm)', 'IB Width - Drawing (cm)',
          'IB Height - Drawing (cm)', 'IB Gross Weight - Drawing (kg)',
          'No# of MB - Drawing','MB Length - Drawing (cm)','MB Width - Drawing (cm)','MB Height - Drawing (cm)',
          'MB Net Weight - Drawing (kg)','MB Gross Weight - Drawing (kg)',
          'Base Unit of Measure', 'Company', 'Knock-down', 'Assembly instruction', 'Techpack (Technical Pakage)',
          'Selling Type', 'Brand', 'REACH Result', 'Prop 65 Result', 'Valuation class']

mandf = datasku.set_index('SKU', drop=False)[mancol].merge(picdept[['PIC', 'dept']], on='PIC', how='left')
mask = (mandf[['PIC', 'Product Name', 'Base Unit of Measure', 'Company', 'Knock-down',
           'Techpack (Technical Pakage)', 'Selling Type', 'Brand', 'REACH Result',
           'Prop 65 Result', 'Valuation class']].isna().any(axis=1) |
    ((mandf['Knock-down'] == 'Yes') & mandf['Assembly instruction'].isna()) |
    ((mandf['Selling Type'] != 'Combo') & mandf[['Idea Code','Product Net Weight - Drawing (kg)',
                                                 'No# of IB - Drawing', 'IB Length - Drawing (cm)',
                                                 'IB Width - Drawing (cm)', 'IB Height - Drawing (cm)',
                                                 'IB Gross Weight - Drawing (kg)']].isna().any(axis=1)) |
    ((mandf['No# of MB - Drawing'] != 0) & mandf[['MB Length - Drawing (cm)','MB Width - Drawing (cm)','MB Height - Drawing (cm)',
          'MB Net Weight - Drawing (kg)','MB Gross Weight - Drawing (kg)']].isna().any(axis=1)))

    # PRODUCT DATA BY VENDOR ======================================================================================
mancolven = ['PIC', 'SKU','Supplier Code', 'Product Name', 'SKU_SupCode', 'MOQ', 'FOB Price','FCA Price'\
           'Port FOB', 'Production leadtime 1st Order', 'Production leadtime', \
           'Product Net Weight - Production (kg)', 'No# of IB - Production', 'IB Length - Production (cm)', 'IB Width - Production (cm)', 'IB Height - Production (cm)',\
           'IB Net Weight - Production (kg)', 'IB Gross Weight - Production (kg)', 'No# of MB - Production', 'MB Length- Production (cm)', 'MB Width - Production (cm)',\
           'MB Height - Production (cm)', 'MB Net Weight - Production (kg)', 'MB Gross Weight - Production (kg)', 'SOR Result', 'Purchasing status', 'Duty (%)', 'HTS Code']

mandfven = dataskusup.set_index('SKU_SupCode', drop=False).merge(picdept[['PIC','dept']], on='PIC', how='left')
maskven = (mandfven[['PIC', 'Product Name', 'MOQ', 'Production leadtime 1st Order', 'Production leadtime',
           'SOR Result', 'Purchasing status','Duty (%)','HTS Code','Port FOB']].isna().any(axis=1) |
        ((mandfven['FOB Price'].isna()) & (mandfven['FCA Price'].isna())) |
        ((mandfven['No# of MB - Production'] > 0) & mandfven[['MB Length- Production (cm)', 'MB Width - Production (cm)',\
           'MB Height - Production (cm)', 'MB Net Weight - Production (kg)', 'MB Gross Weight - Production (kg)']].isna().any(axis=1)))

mandfvenfilterfield = mandfven.copy()
mandfvenfilterfield['dept'] = mandfvenfilterfield['dept'].astype(str) + 'ven'

# COOK DATA =======================================================================================================
out_df = mandf[mask]
out_df['NaN_Count'] = out_df.isna().sum(axis=1)
out_df = out_df.sort_values(by='NaN_Count', ascending=True).drop(columns='NaN_Count')
out_df.set_index('SKU', inplace=True)

out_dfven = mandfven[maskven]
out_dfven['NaN_Count'] = out_dfven.isna().sum(axis=1)
out_dfven = out_dfven.sort_values(by='NaN_Count', ascending=True).drop(columns='NaN_Count')
out_dfven.set_index('SKU_SupCode', inplace=True)

    # PRODUCT MASTER ==============================================================================================
# Stacked Bar - Missing value by team:
missbyteam = mandf[mask]
missbyteam = missbyteam.groupby("dept")[list(missbyteam.columns)].apply(lambda x: x.isna().sum()).T

# Separatedly work on the AI:
aicheck = mandf[['Knock-down', 'Assembly instruction', 'dept']]
aicheck = aicheck[(aicheck['Knock-down'] == 'Yes') & aicheck['Assembly instruction'].isna()]
aicheck = aicheck.groupby("dept").apply(lambda x: x.isna().sum()).T
missbyteam.loc['Assembly instruction'] = aicheck.loc['Assembly instruction'] # Replace AI count by separated outcome value.
missbyteam = missbyteam.fillna(0)

# Pie Chart - Complete rate by department:
dept_df = pd.DataFrame({'Affect by Dept': out_df['dept'].value_counts(),
                        'Total by Dept': mandf['dept'].value_counts()}).T
dept_df.loc['Complete by Dept'] = dept_df.loc['Total by Dept'] - dept_df.loc['Affect by Dept']

    # PRODUCT DATA BY VENDOR ======================================================================================
# Stacked Bar - Missing value by team:
missbyteamven = mandfven[maskven]
missbyteamven = missbyteamven.groupby("dept")[list(missbyteamven.columns)].apply(lambda x: x.isna().sum()).T

# Pie Chart - Complete rate by department:
dept_dfven = pd.DataFrame({'Affect by Dept': out_dfven['dept'].value_counts(),
                           'Total by Dept': mandfven['dept'].value_counts()}).T
dept_dfven.loc['Complete by Dept'] = dept_dfven.loc['Total by Dept'] - dept_dfven.loc['Affect by Dept']    

# DASHBOARDING ====================================================================================================
st.markdown("""<style>div[data-testid="stTabs"] {margin-top: -60px;}</style>""", unsafe_allow_html=True)
# =================================================================================================================
pro_tab, proven_tab = st.tabs(["Product Master Data", "Product by Supplier"])
with pro_tab: # Product Master Data ===================================
    st.markdown("<h1 style='font-size: 20px;'>Overview</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        subcol1, subcol2 = st.columns([1,1])
        with subcol1:
            piebytab(mandf, 'Total SKU by Team')            
        with subcol2:                
            piebytab(mandf[mask], 'Total Missing SKU by Team')
        barbytab(missbyteam)
    with col2:
        st.markdown("""<style>div.stTabs:nth-of-type(2) div[role="tablist"]
            {margin-top: -14px;}</style>""",unsafe_allow_html=True)

        sub_tab1, sub_tab2 = st.tabs(["SSO", "SFO"])
        with sub_tab1: #SSO
            col1, col2 = st.columns(2)
            with col1:
                piebydept('SSO', dept_df)
            with col2:
                barbydept('SSO', out_df)            
            filterfield('SSO', mandf, mask, 'SKU')
            detailbysku('SSO', mandf[mask], 'SKU')
        with sub_tab2: #SFO
            col1, col2 = st.columns(2)
            with col1:
                piebydept('SFO', dept_df)       
            with col2:
                barbydept('SFO', out_df)
            filterfield('SFO', mandf, mask, 'SKU')
            detailbysku('SFO', mandf[mask], 'SKU')                

with proven_tab: # Product Data by Vendor =============================
    st.markdown("<h1 style='font-size: 20px;'>Overview</h1>", unsafe_allow_html=True)

    col3, col4 = st.columns([1,1])
    with col3:
        subcol3, subcol4 = st.columns([1,1])
        with subcol3:                
            piebytab(mandfven, 'Total SKU by Team')            
        with subcol4:                
            piebytab(mandfven[maskven], 'Total Missing SKU by Team')
        barbytab(missbyteamven)                
    with col4:            
        sub_tab1, sub_tab2 = st.tabs(["SSO", "SFO"])    
        with sub_tab1: #SSO
            col1, col2 = st.columns(2)
            with col1:
                piebydept('SSO', dept_dfven)
            with col2:
                barbydept('SSO', out_dfven)
            filterfield('SSOven', mandfven, maskven, 'SKU_SupCode')
            detailbysku('SSO', mandfven[maskven], 'SKU_SupCode')
        with sub_tab2: #SFO
            col1, col2 = st.columns(2)
            with col1:
                piebydept('SFO', dept_dfven)
            with col2:
                barbydept('SFO', out_dfven)
            filterfield('SFOven', mandfven, maskven, 'SKU_SupCode')
            detailbysku('SFO', mandfven[maskven], 'SKU_SupCode')
 
    # # Auto-refresh every setting seconds =======================================
    # auto_refresh(10)
