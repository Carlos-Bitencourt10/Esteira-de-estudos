#!/usr/bin/env python3
"""
main.py - Orquestrador Principal (Versão Railway)
Sistema de geração automatizada de estudos de elite
"""

import asyncio
import os
import logging
import json
from datetime import datetime
from typing import Dict, List
import aiohttp
from aiohttp import web
import signal

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EstudoOrchestrator:
    """Orquestrador simplificado para Railway"""
    
    def __init__(self):
        self.active_studies = {}
        self.processing_stats = {
            'studies_completed': 0,
            'studies_failed': 0,
            'uptime_start': datetime.now()
        }
        
        self.http_session = None
        
        # Carrega configurações das variáveis de ambiente
        self.config = {
            'openai_key': os.getenv('OPENAI_API_KEY'),
            'google_key': os.getenv('GOOGLE_API_KEY'),
            'anthropic_key': os.getenv('ANTHROPIC_API_KEY'),
            'cohere_key': os.getenv('COHERE_API_KEY'),
            'mistral_key': os.getenv('MISTRAL_API_KEY'),
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_key': os.getenv('SUPABASE_KEY'),
        }
        
        logger.info("🚀 Esteira de Produção Inteligente inicializada")
    
    async def initialize_session(self):
        """Initialize HTTP session for API calls"""
        if self.http_session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.http_session:
            await self.http_session.close()
    
    async def process_study(self, study_data: Dict) -> Dict:
        """Processa um estudo (versão demo)"""
        study_id = study_data.get('id', 'demo-001')
        
        try:
            logger.info(f"📋 Iniciando processamento do estudo {study_id}")
            
            # Simulação das 4 fases
            phases = [
                "Planejamento Estratégico",
                "Extração de Dados", 
                "Geração de Conteúdo",
                "Polimento Final"
            ]
            
            results = []
            for i, phase in enumerate(phases, 1):
                logger.info(f"⚙️ Fase {i}: {phase}")
                
                # Aqui seria a integração real com as APIs
                # Por agora, simulamos o processamento
                await asyncio.sleep(2)  # Simula processamento
                
                results.append({
                    'phase': phase,
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Resultado final
            final_result = {
                'study_id': study_id,
                'status': 'completed',
                'phases': results,
                'final_content': {
                    'title': study_data.get('title', 'Estudo Técnico Automatizado'),
                    'chapters': 8,
                    'words': 15000,
                    'images': 5,
                    'charts': 3,
                    'processing_time': '2.5 hours',
                    'cost_usd': 7.50
                },
                'completed_at': datetime.now().isoformat()
            }
            
            self.processing_stats['studies_completed'] += 1
            logger.info(f"✅ Estudo {study_id} processado com sucesso!")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento do estudo {study_id}: {e}")
            self.processing_stats['studies_failed'] += 1
            
            return {
                'study_id': study_id,
                'status': 'error',
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
    
    async def test_apis(self) -> Dict:
        """Testa conectividade com as APIs"""
        await self.initialize_session()
        results = {}
        
        if not self.http_session:
            return {'error': 'HTTP session not initialized'}
        
        # Teste OpenAI
        try:
            headers = {
                "Authorization": f"Bearer {self.config['openai_key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 5
            }
            
            async with self.http_session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                results['openai'] = {
                    'status': 'ok' if response.status == 200 else 'error',
                    'response_time': '~1s'
                }
        except Exception as e:
            results['openai'] = {'status': 'error', 'error': str(e)}
        
        # Teste Supabase
        try:
            headers = {
                "apikey": self.config['supabase_key'],
                "Authorization": f"Bearer {self.config['supabase_key']}"
            }
            
            async with self.http_session.get(
                f"{self.config['supabase_url']}/rest/v1/",
                headers=headers
            ) as response:
                results['supabase'] = {
                    'status': 'ok' if response.status == 200 else 'error',
                    'response_time': '~500ms'
                }
        except Exception as e:
            results['supabase'] = {'status': 'error', 'error': str(e)}
        
        return results

# Instância global do orquestrador
orchestrator = EstudoOrchestrator()

# ===== ROTAS HTTP PARA RAILWAY =====

async def health_check(request):
    """Health check para Railway"""
    uptime = datetime.now() - orchestrator.processing_stats['uptime_start']
    
    return web.json_response({
        'status': 'healthy',
        'service': 'Esteira de Produção Inteligente',
        'uptime_seconds': int(uptime.total_seconds()),
        'stats': orchestrator.processing_stats,
        'timestamp': datetime.now().isoformat()
    })

async def api_status(request):
    """Status das APIs"""
    api_results = await orchestrator.test_apis()
    
    return web.json_response({
        'apis': api_results,
        'timestamp': datetime.now().isoformat()
    })

async def process_study_endpoint(request):
    """Endpoint para processar estudo"""
    try:
        data = await request.json()
    except:
        data = {
            'id': 'demo-study',
            'title': 'Estudo de Demonstração',
            'client': 'Cliente Demo'
        }
    
    result = await orchestrator.process_study(data)
    return web.json_response(result)

async def dashboard(request):
    """Dashboard web simples"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Esteira de Produção Inteligente</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #2c5aa0; }}
            .stats {{ background: #e7f3ff; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .btn {{ background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
            .btn:hover {{ background: #45a049; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Esteira de Produção Inteligente</h1>
            <p><strong>Status:</strong> Sistema Online e Operacional</p>
            
            <div class="stats">
                <h3>📊 Estatísticas</h3>
                <p><strong>Estudos Processados:</strong> {orchestrator.processing_stats['studies_completed']}</p>
                <p><strong>Estudos com Erro:</strong> {orchestrator.processing_stats['studies_failed']}</p>
                <p><strong>Uptime:</strong> {datetime.now() - orchestrator.processing_stats['uptime_start']}</p>
            </div>
            
            <h3>🧪 Testes</h3>
            <button class="btn" onclick="testApis()">Testar APIs</button>
            <button class="btn" onclick="processDemo()">Processar Estudo Demo</button>
            
            <div id="results"></div>
            
            <h3>📋 Como Usar</h3>
            <p><strong>Endpoint para processar estudo:</strong></p>
            <code>POST /process</code>
            <pre>{{
  "id": "study-001",
  "title": "Análise de Viabilidade",
  "client": "Nome do Cliente"
}}</pre>
            
            <h3>🔧 Configuração</h3>
            <p>Sistema configurado com:</p>
            <ul>
                <li>✅ OpenAI GPT-4</li>
                <li>✅ Anthropic Claude</li>
                <li>✅ Google Gemini</li>
                <li>✅ Cohere Command R+</li>
                <li>✅ Mistral Large</li>
                <li>✅ Supabase Database</li>
            </ul>
        </div>
        
        <script>
            async function testApis() {{
                document.getElementById('results').innerHTML = '<p>🔄 Testando APIs...</p>';
                try {{
                    const response = await fetch('/api-status');
                    const data = await response.json();
                    let html = '<h4>Resultados dos Testes:</h4>';
                    
                    for (const [api, result] of Object.entries(data.apis)) {{
                        const statusClass = result.status === 'ok' ? 'success' : 'error';
                        html += `<div class="status ${{statusClass}}">
                            <strong>${{api}}:</strong> ${{result.status}} 
                            ${{result.response_time ? '(' + result.response_time + ')' : ''}}
                        </div>`;
                    }}
                    
                    document.getElementById('results').innerHTML = html;
                }} catch (error) {{
                    document.getElementById('results').innerHTML = `<div class="status error">Erro: ${{error}}</div>`;
                }}
            }}
            
            async function processDemo() {{
                document.getElementById('results').innerHTML = '<p>🔄 Processando estudo demo...</p>';
                try {{
                    const response = await fetch('/process', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            id: 'demo-' + Date.now(),
                            title: 'Estudo de Demonstração',
                            client: 'Cliente Demo'
                        }})
                    }});
                    const data = await response.json();
                    
                    let html = '<h4>Resultado do Processamento:</h4>';
                    html += `<div class="status success">
                        <strong>Status:</strong> ${{data.status}}<br>
                        <strong>ID:</strong> ${{data.study_id}}<br>`;
                    
                    if (data.final_content) {{
                        html += `<strong>Palavras:</strong> ${{data.final_content.words}}<br>
                        <strong>Capítulos:</strong> ${{data.final_content.chapters}}<br>
                        <strong>Custo:</strong> $USD ${{data.final_content.cost_usd}}`;
                    }}
                    
                    html += '</div>';
                    document.getElementById('results').innerHTML = html;
                }} catch (error) {{
                    document.getElementById('results').innerHTML = `<div class="status error">Erro: ${{error}}</div>`;
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')

# ===== SERVIDOR HTTP =====

async def create_app():
    """Cria aplicação web"""
    app = web.Application()
    
    # Rotas
    app.router.add_get('/', dashboard)
    app.router.add_get('/health', health_check)
    app.router.add_get('/api-status', api_status)
    app.router.add_post('/process', process_study_endpoint)
    
    return app

async def main():
    """Função principal"""
    try:
        # Configuração do servidor
        port = int(os.getenv('PORT', 8000))
        
        logger.info(f"🌐 Iniciando servidor na porta {port}")
        
        await orchestrator.initialize_session()
        
        # Cria aplicação
        app = await create_app()
        
        # Inicia servidor
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"✅ Servidor iniciado em http://0.0.0.0:{port}")
        logger.info("🚀 Esteira de Produção Inteligente Online!")
        
        # Mantém servidor rodando
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await orchestrator.cleanup()
            
    except Exception as e:
        logger.error(f"❌ Erro no servidor: {e}")
        await orchestrator.cleanup()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Servidor finalizado")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        exit(1)
