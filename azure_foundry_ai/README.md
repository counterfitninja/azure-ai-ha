# Azure Foundry AI Home Assistant Add-on

This add-on integrates Azure AI Foundry with Home Assistant to provide voice services including Text-to-Speech (TTS), Speech-to-Text (STT), and Chat completion.

## Features

- **Text-to-Speech**: Convert text to natural speech using Azure's TTS models
- **Speech-to-Text**: Transcribe audio to text using Whisper models
- **Chat Completion**: AI chat responses using Azure's language models
- **Home Assistant Integration**: Works seamlessly with HA voice pipeline

## Installation

## Installation

### Prerequisites

1. **Azure AI Foundry Account**: You need an active Azure subscription with AI Foundry access
2. **HACS (Home Assistant Community Store)**: Install HACS if not already installed
3. **GitHub Account**: For hosting your custom repository

### Step 1: Set up GitHub Repository

1. Create a new repository on GitHub (e.g., `ha-azure-foundry-addon`)
2. Upload all files from this `azure_foundry_ai` folder to your repository
3. Make sure the repository is public or accessible to your Home Assistant instance

### Step 2: Add to HACS

1. In Home Assistant, go to **HACS** → **Add-ons**
2. Click the **3 dots menu** → **Custom repositories**
3. Add your GitHub repository URL: `https://github.com/yourusername/ha-azure-foundry-addon`
4. Select category: **Add-on**
5. Click **Add**

### Step 3: Install the Add-on

1. Find "Azure Foundry AI" in HACS add-ons
2. Click **Install**
3. Go to **Settings** → **Add-ons** → **Azure Foundry AI**
4. Click **Install** and wait for completion

### Step 4: Configure the Add-on

In the add-on configuration, set:

```yaml
azure_endpoint: "https://your-foundry-endpoint.openai.azure.com"
api_key: "your-azure-api-key"
deployment_name: "your-deployment-name"
tts_voice: "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Step 5: Start the Add-on

1. Click **Start**
2. Enable **Start on boot** and **Watchdog**
3. Check the logs to ensure it starts successfully

## Home Assistant Configuration

### Text-to-Speech Setup

Add to your `configuration.yaml`:

```yaml
tts:
  - platform: rest
    name: azure_foundry_tts
    resource: http://127.0.0.1:8080/api/tts
    method: POST
    headers:
      Content-Type: "application/json"
    data_template: |
      {
        "message": "{{ message }}"
      }
```

### Voice Assistant Setup

For complete voice pipeline integration:

```yaml
# Voice Assistant Configuration
assist_pipeline:
  - name: "Azure Foundry Assistant"
    conversation_engine: homeassistant
    conversation_language: en
    language: en
    stt_engine: azure_foundry_stt
    tts_engine: azure_foundry_tts
    wake_word_engine: openwakeword
    wake_word_id: "ok_nabu"

# Speech-to-Text (if supported)
stt:
  - platform: rest
    name: azure_foundry_stt
    resource: http://127.0.0.1:8080/api/stt
    method: POST
    headers:
      Content-Type: "multipart/form-data"
```

## Testing

### Test TTS Service

Use the Developer Tools in Home Assistant:

1. Go to **Developer Tools** → **Services**
2. Select `tts.azure_foundry_tts_say`
3. Enter target entity (like `media_player.living_room`)
4. Add message: "Hello, this is a test"
5. Click **Call Service**

### Test via REST API

```bash
# Test TTS
curl -X POST http://your-ha-ip:8080/api/tts \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello World"}' \
  --output test.mp3

# Test Health Check
curl http://your-ha-ip:8080/health
```

## Troubleshooting

### Common Issues

1. **Add-on won't start**: Check logs for configuration errors
2. **TTS not working**: Verify Azure endpoint and API key
3. **No audio output**: Check Home Assistant media player configuration

### Debug Steps

1. **Check Add-on Logs**:
   - Go to Add-on → Logs tab
   - Look for connection errors or API failures

2. **Verify Configuration**:
   - Test Azure endpoint manually
   - Confirm deployment name exists
   - Check API key permissions

3. **Network Issues**:
   - Ensure Home Assistant can reach Azure endpoints
   - Check firewall settings

### Log Examples

**Successful Start**:
```
[INFO] Configuration loaded successfully
[INFO] Starting Azure Foundry AI service on port 8080
```

**Configuration Error**:
```
[ERROR] Options file not found: /data/options.json
```

**Azure API Error**:
```
[ERROR] Azure API error: 401 - Unauthorized
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/tts` - Text-to-speech conversion
- `POST /api/stt` - Speech-to-text transcription
- `POST /api/chat` - Chat completion

## Support

For issues and questions:
1. Check the Home Assistant logs
2. Review Azure Foundry documentation
3. Submit issues to your GitHub repository