#!/bin/bash

# Script de inicio rápido para WebApp

echo "=========================================="
echo "     WebApp - Inicio Rápido"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null
then
    echo -e "${YELLOW}⚠ Python 3 no está instalado${NC}"
    echo "Por favor, instala Python 3.7 o superior"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 detectado${NC}"
python3 --version
echo ""

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creando entorno virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
    echo ""
fi

# Activar entorno virtual
echo -e "${BLUE}Activando entorno virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Instalar dependencias
echo -e "${BLUE}Instalando dependencias...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Iniciar la aplicación
echo "=========================================="
echo -e "${GREEN}🚀 Iniciando WebApp...${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}La aplicación estará disponible en:${NC}"
echo -e "${GREEN}   👉 http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener el servidor${NC}"
echo ""

python app.py
