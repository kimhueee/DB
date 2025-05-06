#!/usr/bin/env python
# coding: utf-8

# In[14]:


import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# In[15]:


SPREADSHEET_ID = "1qsGHOEEQRlFAitOsQ3i-P9E5_sLpyi1nERMyySi5l7U"
SHEET_NAME = "Data"
CREDENTIALS_FILE = "famous-analyzer-458803-n6-b91983525854.json"

def load_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


# In[16]:


st.title("📊 Dashboard từ Google Sheet")

try:
    df = load_data()
    st.success("✅ Dữ liệu đã tải thành công.")
    st.dataframe(df)

    if "PublishedDate" in df.columns and "Id" in df.columns:
        # Chuyển cột ngày sang dạng datetime
        df["PublishedDate"] = pd.to_datetime(df["PublishedDate"])

        # Đếm số lượng Id theo ngày
        df_count = df.groupby(df["PublishedDate"].dt.date)["Id"].count().reset_index()
        df_count.columns = ["Ngày", "Số lượng"]

        # Vẽ biểu đồ
        st.line_chart(df_count.set_index("Ngày")["Số lượng"])
    else:
        st.warning("Không có cột 'Published date' hoặc 'Id' để hiển thị biểu đồ.")

except Exception as e:
    st.error(f"❌ Lỗi khi tải dữ liệu: {e}")


# In[ ]:




