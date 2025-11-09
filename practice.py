from sqlalchemy import create_engine
import pandas as pd

def get_engine(user: str, password: str, host: str, port: int, database: str):
    """Return a SQLAlchemy engine for the given MySQL connection parameters."""
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)

def fetch_items(engine):
    df=pd.read_csv("D:\Projects\data\TCS\tcs.csv")
    return df
   

def load_data(engine, df: pd.DataFrame):
    df.to_sql('items', con=engine, if_exists='append', index=False)
    return df

