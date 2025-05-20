# Install required packages in Colab (uncomment if needed)
# !pip install pandas pydantic duckdb pyarrow fastparquet
import requests
import json
import pandas as pd
import sqlite3
import duckdb
from pydantic import BaseModel, ValidationError
from typing import List

# Step 1: Fetch JSON data
url = "https://jsonplaceholder.typicode.com/comments"
response = requests.get(url)
data = response.json()
print(data)

# Step 2: Define schema with Pydantic for validation
class Comment(BaseModel):
    postId: int
    id: int
    name: str
    email: str
    body: str

# Step 3: Validate data
validated_data = []
for item in data:
    try:
        #unpacking the item according to the parameter names of Comment
        validated_data.append(Comment(**item).model_dump()) 
    except ValidationError as e:
        print("Validation error:", e)

print(f"{len(validated_data)} records validated successfully.")

# Step 4: Save JSON
with open("comments.json", "w") as f:
    json.dump(validated_data, f, indent=2)

# Step 5: Save as SQLite data
df = pd.DataFrame(validated_data)
conn = sqlite3.connect("commentsdb.sqlite")
df.to_sql("comments", conn, if_exists="replace", index=False)
conn.close()

print("commentsdb.sqlite created.")

# Step 6: Save as duckdb data
import duckdb
import os

db_file = "commentsdb.duck"
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Deleted existing DuckDB file: {db_file}")

conn_duckdb = duckdb.connect(db_file)
conn_duckdb.execute("DROP TABLE IF EXISTS comments")
conn_duckdb.execute("CREATE TABLE comments AS SELECT * FROM df")

print("DuckDB table created.")

# Step 7: Save as Parquet data
df.to_parquet("comments.parquet", index=False)
print("comments.parquet created.")

# Step 8: Show summary
print("\nDataset Preview:")
print(df.head())
print("\nColumn Types:")
print(df.dtypes)
