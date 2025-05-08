# ocrclipboard
OCR Clipboard App – Captura uma região da tela, faz OCR usando Tesseract e exibe o texto reconhecido em uma interface Tkinter editável.
# OCR Clipboard App

Uma aplicação de desktop em Python que permite capturar qualquer área da tela, executar OCR (reconhecimento óptico de caracteres) com o Tesseract e exibir o texto resultante em uma janela editável.

---

## Funcionalidades

- **Selecionar área da tela** para captura de imagem.  
- **Pré-processamento** da imagem (escala de cinza, contraste e binarização) para melhorar a acurácia do OCR.  
- **Exibição** da imagem capturada e do texto reconhecido em um campo editável.  
- **Copiar imagem** diretamente da interface para o clipboard com clique direito.  
- **Pacote .deb** pronto para instalação em Debian/Ubuntu amd64.

---

## Dependências

### Runtime (Debian/Ubuntu)

- `gnome-screenshot`  
- `xclip`  
- `tesseract-ocr`  
- `tesseract-ocr-por`  (dados de idioma português)  
- `python3-tk`        (Tkinter)

### Python (instaladas via pip)

- `pillow`  
- `pytesseract`  
- `ttkthemes`

> **Obs.:** O binário empacotado com PyInstaller já inclui todas as libs Python, então o usuário final não precisa instalar nada manualmente além das dependências de sistema acima.

---

## Instalação

1. **Instalar dependências de sistema**  
   ```bash
   sudo apt update
   sudo apt install gnome-screenshot xclip tesseract-ocr tesseract-ocr-por python3-tk
