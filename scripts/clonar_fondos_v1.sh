#!/bin/bash

# Script para clonar el repositorio fondos_v1 desde GitHub

REPO_URL="https://github.com/iccmu/fondos_v1.git"
TARGET_DIR="/Users/ivansimo/Documents/2025/fondos_v1"

echo "🔗 Clonando repositorio fondos_v1..."
echo "URL: $REPO_URL"
echo "Destino: $TARGET_DIR"
echo ""

# Verificar si el directorio ya existe
if [ -d "$TARGET_DIR" ]; then
    echo "⚠️  El directorio $TARGET_DIR ya existe."
    echo "¿Deseas actualizarlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        cd "$TARGET_DIR"
        git pull
        echo "✅ Repositorio actualizado"
    else
        echo "Operación cancelada"
        exit 1
    fi
else
    cd /Users/ivansimo/Documents/2025/
    git clone "$REPO_URL" fondos_v1
    echo "✅ Repositorio clonado exitosamente"
fi

echo ""
echo "📁 Ubicación del repositorio:"
echo "$TARGET_DIR"
echo ""
echo "Nota: Ya existe una copia local en:"
echo "/Users/ivansimo/Documents/2025/FONDOS/"

