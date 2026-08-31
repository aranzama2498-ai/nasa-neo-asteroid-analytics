import sqlite3
import pandas as pd

df = pd.read_csv("data/processed/neo_clean.csv")
conn = sqlite3.connect("neo.db")          # creates a database file called neo.db if it doesn't exist
df.to_sql("neo_approaches", conn, if_exists="replace", index=False)
conn.close()
print("Data loaded into neo.db")