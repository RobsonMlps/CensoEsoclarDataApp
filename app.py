import pandas as pd


caminho_escola = '/mnt/91310fa6-7d6e-4614-bee7-fdbc148a8414/ProjetosDev/web I/pweb_20261/censoescolarweb/censo_escolar/microdados_censo_escolar_2025/dados/Tabela_Escola_2025.csv'
caminho_matricula = '/mnt/91310fa6-7d6e-4614-bee7-fdbc148a8414/ProjetosDev/web I/pweb_20261/censoescolarweb/censo_escolar/microdados_censo_escolar_2025/dados/Tabela_Matricula_2025.csv' 
caminho_json = '/mnt/91310fa6-7d6e-4614-bee7-fdbc148a8414/ProjetosDev/web I/pweb_20261/censoescolarweb/src/datasets/escolaspb.json'

colunas_escola = [
    'NO_ENTIDADE', 'CO_ENTIDADE', 'NO_UF', 'SG_UF', 'CO_UF', 
    'NO_MUNICIPIO', 'CO_MUNICIPIO', 'NO_MESORREGIAO', 'CO_MESORREGIAO', 
    'NO_MICRORREGIAO', 'CO_MICRORREGIAO', 'NU_ANO_CENSO', 'NO_REGIAO', 'CO_REGIAO'
]
df_escola = pd.read_csv(caminho_escola, encoding='latin1', sep=';', usecols=colunas_escola)

df_escola_pb = df_escola[df_escola['SG_UF'] == 'PB'].copy()

colunas_matricula = [
    'CO_ENTIDADE', 'QT_MAT_BAS', 'QT_MAT_INF', 'QT_MAT_FUND', 
    'QT_MAT_MED', 'QT_MAT_PROF', 'QT_MAT_EJA', 'QT_MAT_ESP'
]
df_matricula = pd.read_csv(caminho_matricula, encoding='latin1', sep=';', usecols=colunas_matricula)

df_final = pd.merge(df_escola_pb, df_matricula, on='CO_ENTIDADE', how='inner')

df_final['QT_MAT_BAS'] = pd.to_numeric(df_final['QT_MAT_BAS'], errors='coerce').fillna(0)

df_top30 = df_final.sort_values(by='QT_MAT_BAS', ascending=False).head(30)

df_top30.columns = df_top30.columns.str.lower()

df_top30.to_json(caminho_json, orient='records', force_ascii=False, indent=4)

print("Arquivo escolas_pb.json gerado com sucesso!")