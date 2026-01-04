#!/bin/bash

# setup.sh: The Sovereign Birth Script
echo "🌍 Initializing Armature - Sovereign Media Hub"
echo "=============================================="

# 1. Update the 'Body' (System)
echo "📦 Updating system hardware interfaces..."
sudo apt update && sudo apt upgrade -y

# 2. Install Docker (The Cellular Membrane)
echo "🐳 Installing Docker & Docker Compose..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose -y

# 3. Create the 'Organs' (Directory Structure)
echo "📁 Creating vital organ directories..."
mkdir -p services/{n8n,ollama,meilisearch,redis}
mkdir -p scripts docs

# 4. Inhale the Configuration
if [ ! -f .env ]; then
    echo "⚙️  No .env found. Copying from breath template (.env.example)..."
    cp .env.example .env
    echo "⚠️  ACTION REQUIRED: Edit the .env file with your real secrets!"
fi

# 5. Ignite the Core
echo "🚀 Starting the Transformer Services..."
docker-compose up -d

# 6. Tune the Heart (Ollama)
echo "🤖 Downloading AI Frequency Models..."
docker exec ollama ollama pull llama3
docker exec ollama ollama pull mistral

echo ""
echo "✅ Armature is ALIVE."
echo "=============================================="
echo "Access points:"
echo "- n8n (Nervous System): http://localhost:5678"
echo "- Ollama (Heartbeat): http://127.0.0.1:11434"
echo "- Meilisearch (Filter): http://localhost:7700"
echo ""
echo "🌍 Your sovereign territory is online."
