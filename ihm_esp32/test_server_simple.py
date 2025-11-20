#!/usr/bin/env python3
"""
Servidor HTTP simples para testar se o problema é do aiohttp
"""
import asyncio
from aiohttp import web
from pathlib import Path

async def index_handler(request):
    """Serve index.html"""
    html_path = Path(__file__).parent / 'static' / 'index.html'

    print(f"📨 Requisição recebida de: {request.remote}")
    print(f"📂 Servindo: {html_path}")
    print(f"📊 Arquivo existe: {html_path.exists()}")

    if html_path.exists():
        return web.FileResponse(html_path)
    else:
        return web.Response(text=f"404: {html_path} não encontrado", status=404)

async def test_handler(request):
    """Handler de teste"""
    return web.Response(text="OK - Servidor funcionando!", content_type='text/plain')

async def main():
    app = web.Application()
    app.router.add_get('/', index_handler)
    app.router.add_get('/test', test_handler)
    app.router.add_static('/static', Path(__file__).parent / 'static')

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)  # Porta 8081 para não conflitar
    await site.start()

    print("=" * 60)
    print("SERVIDOR HTTP SIMPLES INICIADO")
    print("=" * 60)
    print(f"Porta: 8081")
    print(f"Acesse: http://localhost:8081")
    print(f"Teste: http://localhost:8081/test")
    print("=" * 60)

    # Mantém rodando
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✓ Servidor parado")
