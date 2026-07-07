import pandas as pd
import os

for file in os.listdir("data"):
    if file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join("data", file))
        print(f"\n{file}")
        print(df.columns.tolist())