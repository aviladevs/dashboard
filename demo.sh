#!/bin/bash
# Script de demonstração do Dashboard Ávila Transportes

echo "🚛 Dashboard Ávila Transportes - Demonstração"
echo "=============================================="
echo ""

echo "📋 Status atual do sistema:"
cd "Banco de dados layout"

echo ""
echo "✅ Verificando dependências básicas..."
python -c "
import sys
try:
    import pandas, streamlit
    print('✅ Pandas e Streamlit instalados')
except ImportError as e:
    print(f'❌ Dependências básicas faltando: {e}')
    
try:
    import pyodbc, sqlalchemy
    print('✅ Dependências Azure disponíveis')
except ImportError:
    print('⚠️  Dependências Azure não instaladas (modo CSV ativo)')

try:
    import data_loader
    print(f'✅ Sistema de dados carregado (Azure disponível: {data_loader.AZURE_AVAILABLE})')
except Exception as e:
    print(f'❌ Erro no sistema: {e}')
"

echo ""
echo "📊 Informações dos dados:"
if [ -f "base.csv" ]; then
    lines=$(wc -l < base.csv)
    echo "✅ Arquivo base.csv encontrado com $((lines-1)) registros"
else
    echo "⚠️  Arquivo base.csv não encontrado"
fi

echo ""
echo "🔧 Para usar com Azure Database:"
echo "1. pip install -r ../requirements.txt"
echo "2. Configurar arquivo .env com credenciais Azure"
echo "3. Executar create_tables.sql no Azure SQL Database"
echo "4. streamlit run main.py"
echo ""

echo "📁 Para usar com CSV local apenas:"
echo "1. streamlit run main.py"
echo "2. O sistema funcionará automaticamente com os dados CSV"
echo ""

echo "🌐 Iniciando demonstração web..."
echo "Acesse http://localhost:8501 no seu navegador"
echo "Pressione Ctrl+C para parar"
streamlit run main.py --server.headless false --server.port 8501