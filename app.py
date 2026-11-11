import pandas as pd
import sqlite3
from pathlib import Path

# Caminhos dos arquivos
diretorio_projeto = Path(__file__).resolve().parent
diretorio_microdados = diretorio_projeto / 'microdados_censo_escolar_2025_' / 'microdados_censo_escolar_2025_v2' / 'dados'
caminho_escola = diretorio_microdados / 'Tabela_Escola_2025_V2.csv'
caminho_matricula = diretorio_microdados / 'Tabela_Matricula_2025_V2.csv'

# Caminho onde o banco SQLite será salvo
caminho_db = diretorio_projeto / 'dados' / 'escolas_nordeste_sudeste.db'

# Colunas da tabela de escolas
colunas_escola = [
    'NO_ENTIDADE', 'CO_ENTIDADE', 'NO_UF', 'SG_UF', 'CO_UF', 
    'NO_MUNICIPIO', 'CO_MUNICIPIO', 'NU_ANO_CENSO'
]

# Colunas da tabela de matrículas
colunas_matricula = [
    'CO_ENTIDADE', 'QT_MAT_BAS', 'QT_MAT_INF', 'QT_MAT_FUND', 
    'QT_MAT_MED', 'QT_MAT_PROF', 'QT_MAT_EJA', 'QT_MAT_ESP'
]

# Estados das regiões Nordeste e Sudeste
estados_nordeste_sudeste = [
    'AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE', # Nordeste
    'ES', 'MG', 'RJ', 'SP'                               # Sudeste
]

print("A carregar dados de matrícula...")
df_matricula = pd.read_csv(caminho_matricula, encoding='latin1', sep=';', usecols=colunas_matricula, low_memory=False)

# Tratar colunas numéricas de matrícula
cols_num = ['QT_MAT_BAS', 'QT_MAT_INF', 'QT_MAT_FUND', 'QT_MAT_MED', 'QT_MAT_PROF', 'QT_MAT_EJA', 'QT_MAT_ESP']
for col in cols_num:
    if col in df_matricula.columns:
        df_matricula[col] = pd.to_numeric(df_matricula[col], errors='coerce').fillna(0)

# Garantir que o diretório do banco de dados existe
caminho_db.parent.mkdir(parents=True, exist_ok=True)

# Conexão com o SQLite
conexao_sqlite = sqlite3.connect(caminho_db)

print("A processar escolas em blocos (chunksize = 100) e a salvar no SQLite...")
chunk_size = 100
total_registros = 0
primeiro_lote = True

# Leitura paginada do arquivo de escolas
for chunk_escola in pd.read_csv(caminho_escola, encoding='latin1', sep=';', usecols=colunas_escola, chunksize=chunk_size, low_memory=False):
    
    # Filtrar apenas os estados do Nordeste e Sudeste
    chunk_filtrado = chunk_escola[chunk_escola['SG_UF'].isin(estados_nordeste_sudeste)].copy()
    
    if chunk_filtrado.empty:
        continue
        
    # Unir com os dados de matrícula correspondentes aos IDs deste bloco
    df_merged = pd.merge(chunk_filtrado, df_matricula, on='CO_ENTIDADE', how='inner')
    
    if df_merged.empty:
        continue
        
    # Converter os nomes das colunas para minúsculas (conforme padrão exigido)
    df_merged.columns = df_merged.columns.str.lower()
    
    # Inserir no SQLite em lotes (append)
    # No primeiro lote criamos a tabela (if_exists='replace'), nos seguintes apenas adicionamos (if_exists='append')
    modo = 'replace' if primeiro_lote else 'append'
    df_merged.to_sql('escolas_nordeste_sudeste', conexao_sqlite, if_exists=modo, index=False)
    
    total_registros += len(df_merged)
    primeiro_lote = False

# Fechar conexão com o banco
conexao_sqlite.close()

print(f"Processamento concluído com sucesso! Total de {total_registros} registros inseridos no SQLite.")
print(f"Banco de dados gerado em: {caminho_db}")