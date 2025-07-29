#!/bin/bash

# Dashboard Ávila Transportes - Startup Script
echo "🚛 Iniciando Dashboard Ávila Transportes..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3 para continuar."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip não encontrado. Instale pip para continuar."
    exit 1
fi

# Install dependencies
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro ao instalar dependências."
    exit 1
fi

# Start the Streamlit application
echo "🚀 Iniciando aplicação..."
streamlit run main.py --server.port 8501 --server.address 0.0.0.0

echo "🎉 Dashboard finalizado!"