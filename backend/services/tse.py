import pandas as pd
import unicodedata
import json
import os

def normalizar(nome):
    """Remove acentos e converte para maiúsculas para o matching."""
    if not nome: return ""
    return unicodedata.normalize('NFKD', nome.upper()).encode('ASCII', 'ignore').decode('utf-8').strip()

def carregar_dados_tse():
    """Lê o CSV do TSE e constrói um dicionário {NOME: {redes}}."""
    caminho_csv = "data/redes_sociais_tse.csv"  # Você baixa e coloca aqui
    if not os.path.exists(caminho_csv):
        print("Arquivo do TSE não encontrado. O matching será ignorado.")
        return {}
    
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')
    # Supondo colunas: nm_candidato, ds_url, tipo_rede (verifique o layout real do TSE)
    redes = {}
    for _, row in df.iterrows():
        nome_norm = normalizar(row['nm_candidato'])
        if not nome_norm: continue
        
        if nome_norm not in redes:
            redes[nome_norm] = {}
            
        url = str(row['ds_url'])
        tipo = str(row['tipo_rede']).lower()
        
        if 'instagram' in tipo or 'instagram' in url:
            redes[nome_norm]['instagram'] = extrair_handle(url, 'instagram')
        elif 'facebook' in tipo or 'facebook' in url:
            redes[nome_norm]['facebook'] = extrair_handle(url, 'facebook')
        # ... adicione tiktok, etc.
    
    return redes

def extrair_handle(url, rede):
    if not url or url == 'nan': return ""
    try:
        path = url.split(rede)[-1].strip('/').split('?')[0]
        return path if path.startswith('@') else '@' + path
    except:
        return ""

def mesclar_redes(parlamentar, base_tse):
    """Mescla as redes do TSE no objeto do parlamentar."""
    chave = normalizar(parlamentar['nome'])
    dados_tse = base_tse.get(chave)
    if dados_tse:
        # Preenche apenas se o dado legislativo estiver vazio
        for rede in ['instagram', 'facebook', 'tiktok', 'whatsapp']:
            if not parlamentar.get(rede) and dados_tse.get(rede):
                parlamentar[rede] = dados_tse[rede]
    return parlamentar