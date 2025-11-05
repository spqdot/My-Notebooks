#%%
# Import necessary libraries
from sqlalchemy import create_engine,text
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

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
# Add date pickers for start and end date
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=pd.to_datetime("2024-08-31"))
with col2:
    end_date = st.date_input("End Date", value=pd.to_datetime("2018-01-31"))

st.write(f"Selected period: {start_date} to {end_date}")
with conn_engine.begin() as conn:
    query = st.text_input("Write your query", value="select * from dbo.tcs")
    if st.button("Read Data"):
        df = pd.read_sql(text(query), conn)

    # Set the title of the Streamlit app
        st.title('tcs_data Analysis')


  

    #to calculate yearly returns and excess returns
        df["asofmonth"]=pd.to_datetime(df["asofmonth"])
        df["Period"] = df["asofmonth"].dt.year
        df = df.sort_values("asofmonth")
        present_month = df["asofmonth"].max()
        
       
        three_months_ago = present_month - pd.DateOffset(months=2)
        six_months_ago = present_month- pd.DateOffset(months=5)
        quarter_start = present_month.to_period("Q").start_time
        one_year_ago = present_month - pd.DateOffset(months=11)
        three_years_ago = present_month- pd.DateOffset(years=2, months=11)
        five_years_ago = present_month- pd.DateOffset(years=4, months=11)
        ytd_start = present_month.replace(day=1).replace(month=1)

        df_mtd= df[df["asofmonth"] >= present_month.replace(day=1)]
        df_3m = df[df["asofmonth"] >= three_months_ago]
        df_6m = df[df["asofmonth"] >= six_months_ago]
        df_QTD=df[df["asofmonth"] >= quarter_start]
        df_ytd = df[df["asofmonth"] >= ytd_start]
        df_1y = df[df["asofmonth"] >= one_year_ago]
        df_3y = df[df["asofmonth"] >= three_years_ago]
        df_5y = df[df["asofmonth"] >= five_years_ago]
        df_SI =df[df["asofmonth"] >= df["asofmonth"].min()]


        MTD = (1 + df_mtd[["tcs", "nifty50"]]).prod() - 1
        three_month = (1+ df_3m[["tcs", "nifty50"]]).prod() - 1
        six_month = (1 + df_6m[["tcs", "nifty50"]]).prod() - 1
        QTD = (1 + df_QTD[["tcs", "nifty50"]]).prod() - 1

        YTD = (1 + df_ytd[["tcs", "nifty50"]]).prod() - 1
        one_year = (1 + df_1y[["tcs", "nifty50"]]).prod() - 1
        three_year = (1 + df_3y[["tcs", "nifty50"]]).prod() - 1
        five_year = (1 + df_5y[["tcs", "nifty50"]]).prod() - 1
        Since_inception = (1 + df_SI[["tcs", "nifty50"]]).prod() - 1
        
        # Convert to percentage
        MTD = MTD * 100
        three_month = three_month * 100
        six_month = six_month * 100
        QTD = QTD * 100
        YTD = YTD * 100
        one_year = one_year * 100
        three_year = three_year * 100
        five_year = five_year * 100
        Since_inception = Since_inception * 100
        # Create a list to hold all the data
        all_data = []
        all_data.append(["MTD", MTD["tcs"], MTD["nifty50"]])
        all_data.append(["3M", three_month["tcs"], three_month["nifty50"]])
        all_data.append(["6M", six_month["tcs"], six_month["nifty50"]])
        all_data.append(["QTD", QTD["tcs"], QTD["nifty50"]])
        all_data.append(["YTD", YTD["tcs"], YTD["nifty50"]])
        all_data.append(["1Y", one_year["tcs"], one_year["nifty50"]])
        all_data.append(["3Y", three_year["tcs"], three_year["nifty50"]])
        all_data.append(["5Y", five_year["tcs"], five_year["nifty50"]])
        all_data.append(["SI", Since_inception["tcs"], Since_inception["nifty50"]])
        
        
        df1 = df.groupby(["Period"])[["tcs", "nifty50"]].apply(lambda x: (1 + x).prod() - 1)
    
        df1=df1*100

       
        df1.columns = [ "Fund return(%)", "Benchmark return(%)"]
        df1["Excess return(%)"] = df1["Fund return(%)"] - df1["Benchmark return(%)"]
      
        df1 = df1.sort_index(ascending=False)
          
        df1 = df1.reset_index()
        
        
        Period = ["MTD", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "SI"]

        all_data = pd.DataFrame(all_data, columns=["Period", "Fund return(%)", "Benchmark return(%)"])
        all_data["Excess return(%)"] = all_data["Fund return(%)"] - all_data["Benchmark return(%)"]

        df=pd.concat([all_data, df1], ignore_index=True)
       

      
        # df2 =df1.T
        # df2.columns = pd.to_numeric(df2.iloc[0])
        # df2 = df2.drop(df2.index[0])
        
        st.write(df)


        # Filter dataframes for different periods
        # Create cumulative return columns
        df_SI = df_SI.copy()
        df_SI["Cumulative Fund Return"] = (1 + df_SI["tcs"]).cumprod() - 1
        df_SI["Cumulative Benchmark Return"] = (1 + df_SI["nifty50"]).cumprod() - 1

        # Create annualized return columns (CAGR)
        total_months = (df_SI["asofmonth"].max().to_period('M') - df_SI["asofmonth"].min().to_period('M')).n + 1
        years = total_months / 12
        fund_total_return = (1 + df_SI["tcs"]).prod()
        benchmark_total_return = (1 + df_SI["nifty50"]).prod()

        annualized_fund_return = fund_total_return**(1/years) - 1
        annualized_benchmark_return = benchmark_total_return**(1/years) - 1

        filtered_df2_SI_ann = pd.DataFrame({"Period": ["Since Inception"],"Fund return(%)": [annualized_fund_return * 100],"Benchmark return(%)": [annualized_benchmark_return * 100]})
        filtered_df2_SI_com = df_SI[["asofmonth", "Cumulative Fund Return", "Cumulative Benchmark Return"]].rename(columns={"asofmonth": "Period"})
        filtered_df2_SI_com["Fund return(%)"] = filtered_df2_SI_com["Cumulative Fund Return"] * 100
        filtered_df2_SI_com["Benchmark return(%)"] = filtered_df2_SI_com["Cumulative Benchmark Return"] * 100
        filtered_df2_SI_com = filtered_df2_SI_com[["Period", "Fund return(%)", "Benchmark return(%)"]]
        
        # Filter dataframes for 3 years
        df_3y = df_3y.copy()
        df_3y["Cumulative Fund Return"] = (1 + df_3y["tcs"]).cumprod() - 1
        df_3y["Cumulative Benchmark Return"] = (1 + df_3y["nifty50"]).cumprod() - 1
        total_months_3y = (df_3y["asofmonth"].max().to_period('M') - df_3y["asofmonth"].min().to_period('M')).n + 1
        years_3y = total_months_3y / 12
        fund_total_return_3y = (1 + df_3y["tcs"]).prod()
        benchmark_total_return_3y = (1 + df_3y["nifty50"]).prod()
        annualized_fund_return_3y = fund_total_return_3y**(1/years_3y) - 1
        annualized_benchmark_return_3y = benchmark_total_return_3y**(1/years_3y) - 1
        filtered_df2_3y_ann = pd.DataFrame({"Period": ["3 Years"],"Fund return(%)": [annualized_fund_return_3y * 100],"Benchmark return(%)": [annualized_benchmark_return_3y * 100]})
        filtered_df2_3y_com = df_3y[["asofmonth", "Cumulative Fund Return", "Cumulative Benchmark Return"]].rename(columns={"asofmonth": "Period"})
        filtered_df2_3y_com["Fund return(%)"] = filtered_df2_3y_com["Cumulative Fund Return"] * 100
        filtered_df2_3y_com["Benchmark return(%)"] = filtered_df2_3y_com["Cumulative Benchmark Return"] * 100
        filtered_df2_3y_com = filtered_df2_3y_com[["Period", "Fund return(%)", "Benchmark return(%)"]]

        # Filter dataframes for 5 years
        df_5y = df_5y.copy()
        df_5y["Cumulative Fund Return"] = (1 + df_5y["tcs"]).cumprod() - 1

        df_5y["Cumulative Benchmark Return"] = (1 + df_5y["nifty50"]).cumprod() - 1
        total_months_5y = (df_5y["asofmonth"].max().to_period('M') - df_5y["asofmonth"].min().to_period('M')).n + 1
        years_5y = total_months_5y / 12
        fund_total_return_5y = (1 + df_5y["tcs"]).prod()
        benchmark_total_return_5y = (1 + df_5y["nifty50"]).prod()
        annualized_fund_return_5y = fund_total_return_5y**(1/years_5y) - 1
        annualized_benchmark_return_5y = benchmark_total_return_5y**(1/years_5y) - 1
        filtered_df2_5y_ann = pd.DataFrame({"Period": ["5 Years"],"Fund return(%)": [annualized_fund_return_5y * 100],"Benchmark return(%)": [annualized_benchmark_return_5y * 100]})
        filtered_df2_5y_com = df_5y[["asofmonth", "Cumulative Fund Return", "Cumulative Benchmark Return"]].rename(columns={"asofmonth": "Period"})
        filtered_df2_5y_com["Fund return(%)"] = filtered_df2_5y_com["Cumulative Fund Return"] * 100
        filtered_df2_5y_com["Benchmark return(%)"] = filtered_df2_5y_com["Cumulative Benchmark Return"] * 100
        filtered_df2_5y_com = filtered_df2_5y_com[["Period", "Fund return(%)", "Benchmark return(%)"]]


        # --- Plotly Charts ---
        # Cummulative Returns Since Inception (Line Chart)
        fig_cum_si = go.Figure()
        fig_cum_si.add_trace(go.Scatter(x=filtered_df2_SI_com["Period"], y=filtered_df2_SI_com["Fund return(%)"], mode='lines+markers', name='Fund return(%)'))
        fig_cum_si.add_trace(go.Scatter(x=filtered_df2_SI_com["Period"], y=filtered_df2_SI_com["Benchmark return(%)"], mode='lines+markers', name='Benchmark return(%)'))
        fig_cum_si.update_layout(title="Cummulative Returns Since Inception", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_cum_si, use_container_width=True)

        # Annualized Returns Since Inception (Bar Chart)
        fig_ann_si = go.Figure()
        fig_ann_si.add_trace(go.Bar(x=filtered_df2_SI_ann["Period"], y=filtered_df2_SI_ann["Fund return(%)"], name='Fund return(%)'))
        fig_ann_si.add_trace(go.Bar(x=filtered_df2_SI_ann["Period"], y=filtered_df2_SI_ann["Benchmark return(%)"], name='Benchmark return(%)'))
        fig_ann_si.update_layout(barmode='group', title="Annualized Returns Since Inception", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_ann_si, use_container_width=True)

        # Cummulative Returns 3 Years (Line Chart)
        fig_cum_3y = go.Figure()
        fig_cum_3y.add_trace(go.Scatter(x=filtered_df2_3y_com["Period"], y=filtered_df2_3y_com["Fund return(%)"], mode='lines+markers', name='Fund return(%)'))
        fig_cum_3y.add_trace(go.Scatter(x=filtered_df2_3y_com["Period"], y=filtered_df2_3y_com["Benchmark return(%)"], mode='lines+markers', name='Benchmark return(%)'))
        fig_cum_3y.update_layout(title="Cummulative Returns 3 Years", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_cum_3y, use_container_width=True)

        # Annualized Returns 3 Years (Bar Chart)
        fig_ann_3y = go.Figure()
        fig_ann_3y.add_trace(go.Bar(x=filtered_df2_3y_ann["Period"], y=filtered_df2_3y_ann["Fund return(%)"], name='Fund return(%)'))
        fig_ann_3y.add_trace(go.Bar(x=filtered_df2_3y_ann["Period"], y=filtered_df2_3y_ann["Benchmark return(%)"], name='Benchmark return(%)'))
        fig_ann_3y.update_layout(barmode='group', title="Annualized Returns 3 Years", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_ann_3y, use_container_width=True)

        # Cummulative Returns 5 Years (Line Chart)
        fig_cum_5y = go.Figure()
        fig_cum_5y.add_trace(go.Scatter(x=filtered_df2_5y_com["Period"], y=filtered_df2_5y_com["Fund return(%)"], mode='lines+markers', name='Fund return(%)'))
        fig_cum_5y.add_trace(go.Scatter(x=filtered_df2_5y_com["Period"], y=filtered_df2_5y_com["Benchmark return(%)"], mode='lines+markers', name='Benchmark return(%)'))
        fig_cum_5y.update_layout(title="Cummulative Returns 5 Years", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_cum_5y, use_container_width=True)

        # Annualized Returns 5 Years (Bar Chart)
        fig_ann_5y = go.Figure()
        fig_ann_5y.add_trace(go.Bar(x=filtered_df2_5y_ann["Period"], y=filtered_df2_5y_ann["Fund return(%)"], name='Fund return(%)'))
        fig_ann_5y.add_trace(go.Bar(x=filtered_df2_5y_ann["Period"], y=filtered_df2_5y_ann["Benchmark return(%)"], name='Benchmark return(%)'))
        fig_ann_5y.update_layout(barmode='group', title="Annualized Returns 5 Years", xaxis_title="Period", yaxis_title="Returns (%)")
        st.plotly_chart(fig_ann_5y, use_container_width=True)

        # --- Time Series Charts for Various Frequencies ---
        st.subheader("Time Series Charts for Various Frequencies")
        # MTD, 3M, 6M, YTD, 1Y, 3Y, 5Y, SI
        freq_dict = {
            'MTD': df_mtd,
            '3M': df_3m,
            '6M': df_6m,
            'QTD': df_QTD,
            'YTD': df_ytd,
            '1Y': df_1y,
            '3Y': df_3y,
            '5Y': df_5y,
            'SI': df_SI
        }
        for freq, dff in freq_dict.items():
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dff["asofmonth"], y=dff["tcs"], mode='lines+markers', name='TCS'))
            fig.add_trace(go.Scatter(x=dff["asofmonth"], y=dff["nifty50"], mode='lines+markers', name='Nifty50'))
            fig.update_layout(title=f"Time Series: {freq}", xaxis_title="Date", yaxis_title="Returns")
            st.plotly_chart(fig, use_container_width=True)






