import pandas as pd

dfs = pd.read_html("http://academica.psi.uba.ar/Psi/Ver154_.php?catedra=34")

for df in dfs:
    print(df)