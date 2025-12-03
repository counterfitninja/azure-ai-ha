#!/usr/bin/env python3
"""
Azure Foundry AI Home Assistant Add-on
Provides TTS, STT, and Chat services using Azure AI Foundry
"""
import json
import asyncio
import logging
from aiohttp import web, ClientSession
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPTIONS_FILE = '/data/options.json'

class AzureFoundryService:
    def __init__(self):
        self.options = {}
        self.load_options()
    
    def load_options(self):
        """Load configuration from Home Assistant options"""
        try:
            with open(OPTIONS_FILE, 'r') as f:
                self.options = json.load(f)
            logger.info("Configuration loaded successfully")
        except FileNotFoundError:
            logger.error(f"Options file not found: {OPTIONS_FILE}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in options file: {e}")
            sys.exit(1)
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "azure-foundry-ai"})
    
    async def text_to_speech(self, request):
        """Convert text to speech using Azure Foundry"""
        try:
            data = await request.json()
            text = data.get('message', '')
            
            if not text:
                return web.json_response({"error": "No text provided"}, status=400)
            
            # Prepare request to Azure
            azure_url = f"{self.options['azure_endpoint']}/openai/deployments/{self.options['deployment_name']}/audio/speech"
            headers = {
                'api-key': self.options['api_key'],
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'tts-1',
                'input': text,
                'voice': self.options.get('tts_voice', 'alloy'),
                'response_format': 'mp3'
            }
            
            async with ClientSession() as session:
                async with session.post(azure_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        audio_data = await resp.read()
                        return web.Response(
                            body=audio_data,
                            content_type='audio/mpeg',
                            headers={'Content-Disposition': 'attachment; filename="speech.mp3"'}
                        )
                    else:
                        error_text = await resp.text()
                        logger.error(f"Azure API error: {resp.status} - {error_text}")
                        return web.json_response({"error": f"Azure API error: {resp.status}"}, status=resp.status)
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def speech_to_text(self, request):
        """Convert speech to text using Azure Foundry"""
        try:
            # Handle audio upload
            reader = await request.multipart()
            audio_field = await reader.next()
            
            if not audio_field:
                return web.json_response({"error": "No audio file provided"}, status=400)
            
            audio_data = await audio_field.read()
            
            # Prepare request to Azure
            azure_url = f"{self.options['azure_endpoint']}/openai/deployments/{self.options['deployment_name']}/audio/transcriptions"
            headers = {
                'api-key': self.options['api_key']
            }
            
            # Create multipart form data
            form_data = {
                'file': ('audio.wav', audio_data, 'audio/wav'),
                'model': 'whisper-1'
            }
            
            async with ClientSession() as session:
                async with session.post(azure_url, data=form_data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return web.json_response({"text": result.get('text', '')})
                    else:
                        error_text = await resp.text()
                        logger.error(f"Azure API error: {resp.status} - {error_text}")
                        return web.json_response({"error": f"Azure API error: {resp.status}"}, status=resp.status)
        
        except Exception as e:
            logger.error(f"STT error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def chat_completion(self, request):
        """Chat completion using Azure Foundry"""
        try:
            data = await request.json()
            
            # Prepare request to Azure
            azure_url = f"{self.options['azure_endpoint']}/openai/deployments/{self.options['deployment_name']}/chat/completions"
            headers = {
                'api-key': self.options['api_key'],
                'Content-Type': 'application/json'
            }
            
            async with ClientSession() as session:
                async with session.post(azure_url, json=data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return web.json_response(result)
                    else:
                        error_text = await resp.text()
                        logger.error(f"Azure API error: {resp.status} - {error_text}")
                        return web.json_response({"error": f"Azure API error: {resp.status}"}, status=resp.status)
        
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return web.json_response({"error": str(e)}, status=500)

async def main():
    """Main service function"""
    service = AzureFoundryService()
    
    # Create web application
    app = web.Application()
    
    # Add routes
    app.router.add_get('/health', service.health_check)
    app.router.add_post('/api/tts', service.text_to_speech)
    app.router.add_post('/api/stt', service.speech_to_text)
    app.router.add_post('/api/chat', service.chat_completion)
    
    # Start server
    logger.info("Starting Azure Foundry AI service on port 8080")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Service stopped")

if __name__ == '__main__':
    asyncio.run(main())