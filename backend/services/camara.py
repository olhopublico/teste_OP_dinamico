import httpx

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

async def buscar_todos_deputados():
    """Busca todos os deputados seguindo a paginação da API."""
    todos = []
    url = f"{BASE_URL}/deputados?itens=100&ordem=ASC&ordenarPor=nome"
    
    async with httpx.AsyncClient() as client:
        while url:
            resp = await client.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            todos.extend(data.get('dados', []))
            
            # Procura o link da próxima página
            next_link = next((link for link in data.get('links', []) if link['rel'] == 'next'), None)
            url = next_link['href'] if next_link else None
            
    return todos

async def buscar_detalhes_lote(lista_basica):
    """Busca detalhes (email, telefone, redes) para cada deputado."""
    async with httpx.AsyncClient() as client:
        async def fetch_one(dep):
            try:
                r = await client.get(f"{BASE_URL}/deputados/{dep['id']}", timeout=15)
                info = r.json().get('dados', {})
                gab = info.get('gabinete', {})
                return {
                    "id": dep['id'],
                    "nome": dep['nome'],
                    "partido": dep['siglaPartido'],
                    "estado": dep['siglaUf'],
                    "foto": dep.get('urlFoto', ''),
                    "siteOficial": f"https://www.camara.leg.br/deputados/{dep['id']}",
                    "telefone": gab.get('telefone', ''),
                    "email": info.get('email', ''),
                    "instagram": extrair_rede(info.get('rede_social', []), 'instagram'),
                    "facebook": extrair_rede(info.get('rede_social', []), 'facebook'),
                    "tiktok": extrair_rede(info.get('rede_social', []), 'tiktok'),
                    "whatsapp": "", "site": "",
                    "mandato2026": True, "suplente": False
                }
            except:
                # Fallback se o detalhe falhar
                return {**dep, "email": "", "telefone": "", "instagram": "", "facebook": "", "tiktok": "", "whatsapp": "", "site": ""}
        
        # Executa em lotes para não sobrecarregar a API
        resultados = []
        for i in range(0, len(lista_basica), 20):
            lote = lista_basica[i:i+20]
            resultados.extend(await asyncio.gather(*[fetch_one(d) for d in lote]))
        return resultados

def extrair_rede(redes, tipo):
    """Extrai o @handle de uma URL de rede social."""
    for url in redes:
        if tipo in url:
            parts = url.strip('/').split('/')
            return '@' + parts[-1].replace('@', '')
    return ""