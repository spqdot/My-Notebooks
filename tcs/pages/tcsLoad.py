from sqlalchemy import create_engine,text
import pandas as pd
import streamlit as st



st.set_page_config(layout="wide")
st.title("tcs_data - Upload & Merge to SQL Server")


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
# File uploader to upload CSV file
uploaded_file = st.file_uploader("Upload tcs_data CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    df["asofmonth"] = pd.to_datetime(df["asofmonth"], format="%d/%m/%Y")
    df["mgr_return"] = (1+ df["tcs"]).cumprod()-1
    df["bm_return"] = (1+df["nifty50"]).cumprod()-1
    # Calculate excess return
    df["excess_return"] = df["mgr_return"] - df["bm_return"]

    st.write("Preview of uploaded data:", df.head())
    st.write(f"Total records: {len(df)}")

    with conn_engine.begin() as conn:
        df.to_sql(name='tcs_temp', con=conn, if_exists='replace', index=False)
        

        # Create main table if it doesn't exist
        create_table_sql = """
        IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'tcs' AND TABLE_SCHEMA = 'dbo'
        )
        BEGIN
            CREATE TABLE dbo.tcs(
                [asofmonth] [date] PRIMARY KEY,
                [month] [varchar](20),
                [tcs] [float],
                [nifty50] [float],
                [mgr_return] [float],
                [bm_return] [float],
                [excess_return] [float]
            )
        END
            """
           
        

            # Merge data from temp to main
        merge_sql = """
        MERGE dbo.tcs AS target
        USING tcs_temp AS source
        ON target.asofmonth = source.asofmonth
        WHEN MATCHED THEN 
            UPDATE SET 
                target.month = source.month,
                target.tcs = source.tcs,
                target.nifty50 = source.nifty50,
                target.mgr_return = source.mgr_return,
                target.bm_return = source.bm_return,
                target.excess_return = source.excess_return
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (asofmonth, month, tcs, nifty50, mgr_return, bm_return, excess_return)
            VALUES (source.asofmonth, source.month, source.tcs, source.nifty50, source.mgr_return, source.bm_return, source.excess_return);
            """
        conn.execute(text(create_table_sql))
        conn.execute(text(merge_sql))
        st.success("Data uploaded and merged successfully into the dbo.tcs table.")
        st.write("Drop the temporary table after merging.")

else:
    st.info("Please upload a CSV file to proceed.")