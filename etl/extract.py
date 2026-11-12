import pandas as pd

# Extract vigilantes
def extraer_vigilantes(path):
    df = pd.read_csv(path, encoding='latin-1', delimiter=';')
    return df

# Extract Empresas Seguridad
def extraer_emp_seg(path):
    df = pd.read_csv(path, encoding='latin-1', delimiter=';')
    return df


# Extract Objetivos
def extraer_objetivos(path):
    df = pd.read_csv(path, encoding='latin-1', delimiter=';')
    return df

# Extract obj_vig
def extraer_obj_vig(path):
    df = pd.read_csv(path, encoding='latin-1', delimiter=';')
    return df

# Extract salida
def extraer_salida(path):
    df = pd.read_csv(path, encoding='utf8')
    return df

