#!/usr/bin/env python3
"""
Script para processar dados de redes sociais de candidatos do TSE.
Uso: python scripts/processar_tse.py
Saída: data/redes_sociais.json
"""

import csv
import json
import os
import zipfile
import urllib.request
from io import TextIOWrapper

# ============================================================
# 1. Configuração: URL do pacote de dados do TSE
# ============================================================
# Obtenha o link real em: https://dadosabertos.tse.jus.br/dataset/candidatos-2026
# Procure "Redes sociais de candidatos", copie a URL do ZIP
TSE_ZIP_URL = "https://dadosabertos.tse.jus.br/dataset/xxxxx/resource/xxxxx/download/redes_sociais_candidatos.zip"
CSV_INTERNO = "rede_social_candidato_2026.csv"  # Nome do CSV dentro do ZIP

# ============================================================
# 2. Download e extração
# ============================================================
def baixar_e_extrair():
    """Baixa o ZIP do TSE para um diretório temporário e retorna o caminho do CSV"""
    print("Baixando dados do TSE...")
    zip_path = "/tmp/tse_redes.zip"
    urllib.request.urlretrieve(TSE_ZIP_URL, zip_path)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall("/tmp/tse_extraido")

    csv_path = os.path.join("/tmp/tse_extraido", CSV_INTERNO)
    print(f"CSV extraído: {csv_path}")
    return csv_path

# ============================================================
# 3. Processamento: CSV → JSON indexado por nome normalizado
# ============================================================
def normalizar_nome(nome):
    """Normaliza nome para matching (remove acentos, converte para maiúsculas)"""
    import unicodedata
    nome = nome.strip().upper()
    nome = unicodedata.normalize('NFKD', nome)
    return ''.join(c for c in nome if not unicodedata.combining(c))

def processar(csv_path):
    """
    O CSV do TSE geralmente contém colunas como:
    - sq_candidato (ID do candidato no TSE)
    - nm_candidato (nome completo)
    - ds_url (URL da rede social)
    - tipo_rede (tipo de rede: Instagram, Facebook, etc.)
    
    Objetivo: construir um dicionário:
    {
      "NOME NORMALIZADO": {
        "instagram": "@usuario",
        "facebook": "usuario",
        ...
      }
    }
    """
    redes = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Detectar delimitador (TSE geralmente usa ;)
        sample = f.read(1024)
        f.seek(0)
        delim = ';' if ';' in sample else ','
        reader = csv.DictReader(f, delimiter=delim)

        for row in reader:
            nome = row.get('nm_candidato', '').strip()
            url = row.get('ds_url', '').strip()
            tipo = row.get('tipo_rede', '').strip().lower()

            if not nome or not url:
                continue

            chave = normalizar_nome(nome)
            if chave not in redes:
                redes[chave] = {}

            # Extrair handle da URL conforme o tipo de rede
            if 'instagram' in tipo or 'instagram' in url:
                handle = extrair_handle(url, 'instagram.com')
                if handle: redes[chave]['instagram'] = handle
            elif 'facebook' in tipo or 'facebook' in url:
                handle = extrair_handle(url, 'facebook.com')
                if handle: redes[chave]['facebook'] = handle
            elif 'tiktok' in tipo or 'tiktok' in url:
                handle = extrair_handle(url, 'tiktok.com')
                if handle: redes[chave]['tiktok'] = handle
            # WhatsApp geralmente não está neste arquivo, mas se houver:
            elif 'whatsapp' in tipo or 'wa.me' in url:
                handle = extrair_handle(url, 'wa.me')
                if handle: redes[chave]['whatsapp'] = handle

    return redes

def extrair_handle(url, dominio):
    """Extrai o nome de usuário de uma URL de rede social"""
    try:
        if dominio in url:
            # Instagram/Facebook: https://instagram.com/fulano → fulano
            # TikTok: https://tiktok.com/@fulano → @fulano
            path = url.split(dominio)[-1].strip('/')
            # Remove parâmetros de query
            path = path.split('?')[0].split('#')[0]
            return path if path else None
    except:
        pass
    return None

# ============================================================
# 4. Salvar JSON
# ============================================================
def salvar_json(redes):
    os.makedirs('data', exist_ok=True)
    caminho = 'data/redes_sociais.json'
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(redes, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {caminho} ({len(redes)} nomes indexados)")

# ============================================================
# Execução principal
# ============================================================
if __name__ == '__main__':
    csv_path = baixar_e_extrair()
    redes = processar(csv_path)
    salvar_json(redes)
    print("Concluído. Atualize o site fazendo upload do novo JSON.")