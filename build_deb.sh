#!/usr/bin/env bash
set -euo pipefail

# --------------------------------------------------
# Configurações do pacote
# --------------------------------------------------
PY_SCRIPT="OCRclipboardTranslate.py"
PACKAGE="ocrclipboardtranslate"
VERSION="1.0"
ARCH="amd64"
MAINTAINER="Marcos Carvalho <marcosabcarvalho@yahoo.com>"
DEPENDS="gnome-screenshot, xclip, tesseract-ocr, tesseract-ocr-por"

# --------------------------------------------------
# Limpa builds anteriores
# --------------------------------------------------
rm -rf build dist __pycache__ *.spec

# --------------------------------------------------
# 1) Garante dependências de sistema (runtime)
# --------------------------------------------------
sudo apt-get update
sudo apt-get install -y \
  gnome-screenshot \
  xclip \
  tesseract-ocr \
  tesseract-ocr-por

# --------------------------------------------------
# 2) Instala PyInstaller e libs Python no virtualenv
# --------------------------------------------------
python3 -m pip install --upgrade \
  pyinstaller pillow pytesseract ttkthemes googletrans==4.0.0-rc1

# --------------------------------------------------
# 3) Gera executável com PyInstaller
# --------------------------------------------------
echo "→ Gerando executável com PyInstaller..."
python3 -m PyInstaller \
  --onefile \
  --windowed \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=PIL.ImageTk \
  "${PY_SCRIPT}" \
  --name "${PACKAGE}"

# --------------------------------------------------
# 4) Monta estrutura do .deb
# --------------------------------------------------
WORKDIR="build/${PACKAGE}-${VERSION}"
DEBIAN_DIR="${WORKDIR}/DEBIAN"
BIN_DIR="${WORKDIR}/usr/bin"
APPS_DIR="${WORKDIR}/usr/share/applications"
ICON_DIR="${WORKDIR}/usr/share/icons/hicolor/128x128/apps"

mkdir -p "${DEBIAN_DIR}" "${BIN_DIR}" "${APPS_DIR}" "${ICON_DIR}"

# Copia o binário para /usr/bin
install -m755 "dist/${PACKAGE}" "${BIN_DIR}/${PACKAGE}"

# --------------------------------------------------
# 5) Cria DEBIAN/control
# --------------------------------------------------
cat > "${DEBIAN_DIR}/control" <<EOF
Package: ${PACKAGE}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: ${DEPENDS}
Maintainer: ${MAINTAINER}
Description: OCR Clipboard + Translate App
 Captura área da tela, faz OCR, detecta idioma e traduz para PT.
EOF

# --------------------------------------------------
# 6) Script pós-instalação (update menu)
# --------------------------------------------------
cat > "${DEBIAN_DIR}/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database
fi
exit 0
EOF
chmod 755 "${DEBIAN_DIR}/postinst"

# --------------------------------------------------
# 7) Cria atalho .desktop
# --------------------------------------------------
cat > "${APPS_DIR}/${PACKAGE}.desktop" <<EOF
[Desktop Entry]
Name=OCR & Translate Clipboard App
Comment=Captura área da tela, faz OCR e traduz para português
Exec=/usr/bin/${PACKAGE}
Icon=ocrclipboard
Terminal=false
Type=Application
Categories=Utility;
Path=/tmp
EOF

# --------------------------------------------------
# 8) Empacota num .deb
# --------------------------------------------------
dpkg-deb --build "${WORKDIR}"
mv "${WORKDIR}.deb" "${PACKAGE}_${VERSION}_${ARCH}.deb"

echo
echo "✅ Pacote gerado: ${PACKAGE}_${VERSION}_${ARCH}.deb"
echo "Para instalar, basta:"
echo "  sudo dpkg -i ${PACKAGE}_${VERSION}_${ARCH}.deb"
echo "  sudo apt --fix-broken install"
