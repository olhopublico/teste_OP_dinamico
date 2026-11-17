from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import camara, senado, tse

app = FastAPI(title="API Congresso Nacional")

# ============================================================
# CORS: permite o GitHub Pages e testes locais
# Substitua pela URL real do seu GitHub Pages
# ============================================================
origins = [
    "https://seu-usuario.github.io",   # ← troque pelo seu usuário
    "http://localhost:5500",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CACHE EM MEMÓRIA
# ============================================================
_cache_deputados = None
_cache_senadores = None
_redes_tse = {}

# ============================================================
# STARTUP: carrega TSE
# ============================================================
@app.on_event("startup")
async def startup_event():
    global _redes_tse
    _redes_tse = tse.carregar_dados_tse()
    print(f"TSE carregado: {len(_redes_tse)} registros.")

# ============================================================
# ROTAS
# ============================================================
@app.get("/api/deputados")
async def get_deputados():
    global _cache_deputados
    if _cache_deputados is None:
        try:
            lista_basica = await camara.buscar_todos_deputados()
            detalhes = await camara.buscar_detalhes_lote(lista_basica)
            _cache_deputados = [tse.mesclar_redes(d, _redes_tse) for d in detalhes]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar Câmara: {str(e)}")
    return _cache_deputados

@app.get("/api/senadores")
async def get_senadores():
    global _cache_senadores
    if _cache_senadores is None:
        try:
            lista_basica = await senado.buscar_todos_senadores()
            detalhes = await senado.buscar_detalhes_lote(lista_basica)
            _cache_senadores = [tse.mesclar_redes(d, _redes_tse) for d in detalhes]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar Senado: {str(e)}")
    return _cache_senadores