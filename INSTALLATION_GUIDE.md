# Step-by-Step Installation Guide

## Phase 1: Azure Setup

### 1. Create Azure AI Foundry Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource**
3. Search for "Azure OpenAI" or "AI Foundry"
4. Click **Create**
5. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose closest region
   - **Name**: e.g., "my-home-assistant-ai"
   - **Pricing Tier**: Standard S0
6. Click **Review + Create** → **Create**

### 2. Deploy Models

1. Go to your Azure OpenAI resource
2. Click **Model deployments** → **Create new deployment**
3. Deploy these models:
   - **TTS Model**: `tts-1` (for text-to-speech)
   - **STT Model**: `whisper-1` (for speech-to-text)
   - **Chat Model**: `gpt-4` or `gpt-3.5-turbo` (for conversation)

### 3. Get Configuration Values

1. In Azure OpenAI resource, go to **Keys and Endpoint**
2. Copy:
   - **Endpoint**: e.g., `https://my-ai.openai.azure.com/`
   - **Key 1**: Your API key
3. Note your **deployment names** from step 2

## Phase 2: GitHub Setup

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click **New repository**
3. Name: `ha-azure-foundry-addon`
4. Make it **Public**
5. Initialize with README: **No** (we'll upload our files)
6. Click **Create repository**

### 2. Upload Add-on Files

**Option A: Web Interface (Easier)**
1. Click **uploading an existing file**
2. Drag the entire `azure_foundry_ai` folder
3. Commit with message: "Initial add-on release"

**Option B: Git Command Line**
```bash
git clone https://github.com/yourusername/ha-azure-foundry-addon.git
cd ha-azure-foundry-addon
# Copy azure_foundry_ai folder here
git add .
git commit -m "Initial add-on release"
git push origin main
```

## Phase 3: Home Assistant Setup

### 1. Install HACS (if not installed)

1. Go to [HACS Installation Guide](https://hacs.xyz/docs/setup/download)
2. Follow the installation steps
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search "HACS" and configure it

### 2. Add Custom Repository

1. In Home Assistant: **HACS** → **Add-ons**
2. Click **⋮** (3 dots) → **Custom repositories**
3. Add:
   - **Repository**: `https://github.com/yourusername/ha-azure-foundry-addon`
   - **Category**: Add-on
4. Click **Add**

### 3. Install the Add-on

1. In HACS Add-ons, find "Azure Foundry AI"
2. Click **Download**
3. Go to **Settings** → **Add-ons** → **Azure Foundry AI**
4. Click **Install**

### 4. Configure the Add-on

1. In the add-on Configuration tab, enter:
```yaml
azure_endpoint: "https://your-resource-name.openai.azure.com/"
api_key: "your-api-key-from-azure"
deployment_name: "your-tts-deployment-name"
tts_voice: "alloy"
```

2. Click **Save**
3. Go to **Info** tab
4. Click **Start**
5. Enable **Start on boot** and **Watchdog**

## Phase 4: Home Assistant Integration

### 1. Configure TTS

Edit `configuration.yaml`:

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

### 2. Restart Home Assistant

1. **Settings** → **System** → **Restart**
2. Wait for restart to complete

### 3. Test TTS Service

1. **Developer Tools** → **Services**
2. Service: `tts.azure_foundry_tts_say`
3. Target: Choose a media player
4. Message: "Hello, this is Azure Foundry AI"
5. Click **Call Service**

## Phase 5: Voice Pipeline (Advanced)

### 1. Configure Voice Assistant

In `configuration.yaml`:

```yaml
assist_pipeline:
  - name: "Azure Assistant"
    conversation_engine: homeassistant
    conversation_language: en
    language: en
    tts_engine: azure_foundry_tts
    wake_word_engine: openwakeword
    wake_word_id: "ok_nabu"
```

### 2. Set as Default

1. **Settings** → **Voice assistants**
2. Select "Azure Assistant" 
3. Set as preferred pipeline

## Troubleshooting Commands

### Check Add-on Status
```bash
# In Home Assistant, go to Add-on → Logs tab
# Look for these log messages:

# Success:
[INFO] Configuration loaded successfully
[INFO] Starting Azure Foundry AI service on port 8080

# Errors:
[ERROR] Azure API error: 401 - Check your API key
[ERROR] Options file not found - Check configuration
```

### Test API Directly
```bash
# Replace YOUR_HA_IP with your Home Assistant IP
curl -X POST http://YOUR_HA_IP:8080/api/tts \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}' \
  --output test.mp3

# Check if file is created and playable
```

### Verify Azure Connection
1. Test your Azure endpoint in a web browser
2. Should show: "Welcome to Azure OpenAI Service"
3. If not accessible, check Azure resource status

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Add-on won't start | Check configuration syntax in YAML |
| TTS returns error | Verify Azure API key and endpoint |
| No sound output | Check Home Assistant media player setup |
| 404 errors | Confirm deployment names in Azure match config |

## Next Steps

Once working:
1. Create automations using the TTS service
2. Set up voice commands
3. Customize voices and settings
4. Add to Home Assistant dashboards