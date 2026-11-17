import httpx
import xmltodict

BASE_URL = "https://legis.senado.leg.br/dadosabertos"

async def buscar_todos_senadores():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/senador/lista/atual", timeout=30)
        data = xmltodict.parse(resp.text)
        # Navega na estrutura aninhada do XML
        parlamentares = data['ListaParlamentarEmExercicio']['Parlamentares']['Parlamentar']
        return parlamentares if isinstance(parlamentares, list) else [parlamentares]

async def buscar_detalhes_lote(lista_basica):
    async with httpx.AsyncClient() as client:
        async def fetch_one(p):
            ident = p['IdentificacaoParlamentar']
            id_senador = ident['CodigoParlamentar']
            try:
                # Busca detalhes para telefone
                r = await client.get(f"{BASE_URL}/senador/{id_senador}", timeout=15)
                det = xmltodict.parse(r.text)
                tel = det['DetalheParlamentar']['Parlamentar'].get('TelefoneParlamentar', '')
            except:
                tel = ""
            
            return {
                "id": id_senador,
                "nome": ident['NomeParlamentar'],
                "partido": ident.get('SiglaPartidoParlamentar', ''),
                "estado": ident.get('UfParlamentar', ''),
                "foto": ident.get('UrlFotoParlamentar', ''),
                "siteOficial": f"https://www25.senado.leg.br/web/senadores/senador/-/perfil/{id_senador}",
                "telefone": tel,
                "email": ident.get('EmailParlamentar', ''),
                "instagram": "", "facebook": "", "tiktok": "", "whatsapp": "", "site": "",
                "mandato2026": True, "suplente": False
            }
        
        # Senado tem menos registros, pode ser sequencial ou em lotes pequenos
        resultados = []
        for p in lista_basica:
            resultados.append(await fetch_one(p))
        return resultados