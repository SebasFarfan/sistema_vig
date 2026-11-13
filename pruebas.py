import pandas as pd

v = pd.read_csv(
    "data/raw/Vigilantes.csv",
    dtype=str,
    sep=None,              # detecta si el separador es coma o punto y coma
    engine="python",
    encoding="utf-8-sig",  # si ves caracteres raros, probá encoding="cp1252"
)
v.columns = v.columns.str.strip().str.lower()
print(v.columns.tolist())  # así ves los nombres reales

v["dni"] = (
    v["dni"].str.strip()
    .str.replace(r"\.0$", "", regex=True)   # quita el ".0" de números leídos como decimales
    .str.replace(".", "", regex=False)      # quita puntos de miles (22.820.915)
)

dnis = ["22820915", "32347316", "21752704", "31817022", "29132689"]

print(v[v["dni"].isin(dnis)])                      # ¿aparecen en más de una empresa?
print("DNI repetidos:", v["dni"].duplicated(keep=False).sum())

print(v[v["dni"].isin(dnis)])