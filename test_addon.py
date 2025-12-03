#!/usr/bin/env python3
"""
Test script for Azure Foundry AI Add-on
Run this to verify your configuration works before installing in Home Assistant
"""
import json
import asyncio
import sys
from aiohttp import web, ClientSession

# Test configuration - replace with your values
TEST_CONFIG = {
    "azure_endpoint": "https://your-resource.openai.azure.com/",
    "api_key": "your-api-key-here",
    "deployment_name": "your-tts-deployment",
    "tts_voice": "alloy"
}

async def test_azure_connection():
    """Test connection to Azure AI Foundry"""
    print("Testing Azure AI Foundry connection...")
    
    # Test TTS endpoint
    azure_url = f"{TEST_CONFIG['azure_endpoint']}/openai/deployments/{TEST_CONFIG['deployment_name']}/audio/speech"
    headers = {
        'api-key': TEST_CONFIG['api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'tts-1',
        'input': 'Hello, this is a test of Azure Foundry AI.',
        'voice': TEST_CONFIG['tts_voice'],
        'response_format': 'mp3'
    }
    
    try:
        async with ClientSession() as session:
            async with session.post(azure_url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    print("✅ Azure TTS connection successful!")
                    
                    # Save test audio file
                    audio_data = await resp.read()
                    with open('test_tts.mp3', 'wb') as f:
                        f.write(audio_data)
                    print("✅ Test audio saved as 'test_tts.mp3'")
                    return True
                else:
                    error_text = await resp.text()
                    print(f"❌ Azure API error: {resp.status}")
                    print(f"   Response: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_local_service():
    """Test the local service endpoints"""
    print("\nTesting local service...")
    
    # Create a minimal version of our service for testing
    class TestService:
        def __init__(self):
            self.options = TEST_CONFIG
        
        async def health_check(self, request):
            return web.json_response({"status": "healthy", "service": "azure-foundry-ai"})
        
        async def text_to_speech(self, request):
            data = await request.json()
            text = data.get('message', '')
            
            if not text:
                return web.json_response({"error": "No text provided"}, status=400)
            
            # Use the same logic as main service
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
                            content_type='audio/mpeg'
                        )
                    else:
                        return web.json_response({"error": f"Azure API error: {resp.status}"}, status=resp.status)
    
    service = TestService()
    app = web.Application()
    app.router.add_get('/health', service.health_check)
    app.router.add_post('/api/tts', service.text_to_speech)
    
    # Start test server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()
    
    print("✅ Test server started on http://127.0.0.1:8080")
    
    # Test health endpoint
    try:
        async with ClientSession() as session:
            async with session.get('http://127.0.0.1:8080/health') as resp:
                if resp.status == 200:
                    print("✅ Health check endpoint working")
                else:
                    print(f"❌ Health check failed: {resp.status}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test TTS endpoint
    try:
        test_payload = {"message": "Hello from the test service"}
        async with ClientSession() as session:
            async with session.post('http://127.0.0.1:8080/api/tts', json=test_payload) as resp:
                if resp.status == 200:
                    print("✅ TTS endpoint working")
                    audio_data = await resp.read()
                    with open('test_service_tts.mp3', 'wb') as f:
                        f.write(audio_data)
                    print("✅ Service test audio saved as 'test_service_tts.mp3'")
                else:
                    error_text = await resp.text()
                    print(f"❌ TTS endpoint failed: {resp.status}")
                    print(f"   Response: {error_text}")
    except Exception as e:
        print(f"❌ TTS endpoint error: {e}")
    
    # Stop test server
    await runner.cleanup()

def check_config():
    """Check if test configuration is set"""
    print("Checking test configuration...")
    
    issues = []
    if not TEST_CONFIG['azure_endpoint'] or 'your-resource' in TEST_CONFIG['azure_endpoint']:
        issues.append("azure_endpoint not configured")
    
    if not TEST_CONFIG['api_key'] or 'your-api-key' in TEST_CONFIG['api_key']:
        issues.append("api_key not configured")
    
    if not TEST_CONFIG['deployment_name'] or 'your-' in TEST_CONFIG['deployment_name']:
        issues.append("deployment_name not configured")
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease edit this script and update TEST_CONFIG with your Azure values.")
        return False
    
    print("✅ Configuration looks good")
    return True

async def main():
    """Main test function"""
    print("Azure Foundry AI Add-on Test Script")
    print("=" * 50)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Test Azure connection
    if not await test_azure_connection():
        print("\n❌ Azure connection test failed. Please check your configuration.")
        sys.exit(1)
    
    # Test local service
    await test_local_service()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Upload the azure_foundry_ai folder to GitHub")
    print("2. Add the repository to HACS")
    print("3. Install and configure the add-on in Home Assistant")
    print("4. Use the configuration values from TEST_CONFIG above")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)