#%%
# Import necessary libraries
from sqlalchemy import create_engine,text
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the tcs  dataset


st.set_page_config(page_title='tcs data analysis', layout='wide')


# Database connection parameters
if st.secrets.env == 'LOCAL':

    server = st.secrets.SERVER["HOST"]
    username = st.secrets.SERVER["USER"]
    password = st.secrets.SERVER["PWD"]
    database = st.secrets.SERVER["DATABASE"]
else:
    server = st.secrets.LOCAL["HOST"]
    username = st.secrets.LOCAL["USER"]
    password = st.secrets.LOCAL["PWD"]
    database = st.secrets.LOCAL["DATABASE"]


conn_string = f"""mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"""

conn_engine=create_engine(conn_string)


#%%
with conn_engine.begin() as conn:
    query = st.text_input("Write your query", value="select * from dbo.tcs")
    if st.button("Read Data"):
        df = pd.read_sql(text(query), conn)

    # Set the title of the Streamlit app
        st.title('tcs_data Analysis')

    # Show a preview of the dataset
        st.write('Dataset Preview:')
        st.dataframe(df)

    #to calculate yearly returns and excess returns

        df["asofmonth"]=pd.to_datetime(df["asofmonth"])
        df["year"] = df["asofmonth"].dt.year
        df["Month"] =df["asofmonth"].dt.to_period('M')
        df["QTR"] = df["asofmonth"].dt.to_period('Q')

     
        

        df1 = df.groupby(["year"])[["tcs", "nifty50"]].apply(lambda x: (1 + x).prod() - 1)
        df2= df.groupby(["Month"])[["tcs", "nifty50"]].apply(lambda x: (1 + x).prod() - 1)
        df3= df.groupby(["QTR"])[["tcs", "nifty50"]].apply(lambda x: (1 + x).prod() - 1)

    


        st.write(df1)
        st.write(df2)
        st.write(df3)
     