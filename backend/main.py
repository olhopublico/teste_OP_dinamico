from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import camara, senado, tse
import asyncio

app = FastAPI(title="API Congresso Nacional")

# Configuração de CORS para permitir que seu index.html acesse o backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque pelo domínio do seu site
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache em memória para evitar bater nas APIs a cada requisição
_cache_deputados = None
_cache_senadores = None
_redes_tse = {}

@app.on_event("startup")
async def startup_event():
    """Carrega os dados do TSE na inicialização para estar pronto para o matching."""
    global _redes_tse
    _redes_tse = tse.carregar_dados_tse()
    print(f"TSE carregado: {len(_redes_tse)} registros.")

@app.get("/api/deputados")
async def get_deputados():
    """Retorna a lista completa de deputados enriquecida com dados do TSE."""
    global _cache_deputados
    if _cache_deputados is None:
        try:
            # Busca todos (com paginação) e depois os detalhes
            lista_basica = await camara.buscar_todos_deputados()
            detalhes = await camara.buscar_detalhes_lote(lista_basica)
            
            # Mescla com dados do TSE
            _cache_deputados = [tse.mesclar_redes(d, _redes_tse) for d in detalhes]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar Câmara: {str(e)}")
    return _cache_deputados

@app.get("/api/senadores")
async def get_senadores():
    """Retorna a lista de senadores enriquecida com dados do TSE."""
    global _cache_senadores
    if _cache_senadores is None:
        try:
            lista_basica = await senado.buscar_todos_senadores()
            detalhes = await senado.buscar_detalhes_lote(lista_basica)
            _cache_senadores = [tse.mesclar_redes(d, _redes_tse) for d in detalhes]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar Senado: {str(e)}")
    return _cache_senadores
    
    
    
    from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Lista de origens permitidas
origins = [
    "https://teste_OP_dinamico.github.io",  # ← SUBSTITUA pelo seu link do GitHub Pages
    "http://localhost:5500",           # Para testes locais (opcional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Permite as origens listadas
    allow_credentials=True,
    allow_methods=["*"],         # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],         # Permite todos os cabeçalhos
)