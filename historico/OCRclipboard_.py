# -*- coding: utf-8 -*-
# OCR Clipboard App com TTkThemes
# Dependências:
#   pip install pillow pytesseract ttkthemes
#   sudo apt install python3-tk gnome-screenshot xclip

import subprocess
import os
import io
from PIL import Image, ImageTk
import pytesseract
import tkinter as tk
from tkinter import scrolledtext, ttk
from ttkthemes import ThemedTk

# Variável global para bytes da última imagem
last_image_data = None

# Processa arquivo de imagem e extrai OCR
def process_image_file(path):
    global last_image_data
    text_widget.delete('1.0', tk.END)
    try:
        with open(path, 'rb') as f:
            last_image_data = f.read()
        image = Image.open(io.BytesIO(last_image_data))
    except Exception as e:
        text_widget.insert(tk.END, f"Erro ao abrir imagem: {e}")
        return
    display_image(image)
    text = pytesseract.image_to_string(image, lang='por')
    text_widget.insert(tk.END, text)

# Captura área da tela e processa via arquivo
def select_area_ocr():
    text_widget.delete('1.0', tk.END)
    image_label.config(image='')
    tmp = '/tmp/ocr_area.png'
    if os.path.exists(tmp):
        os.remove(tmp)
    root.withdraw()
    root.update()
    try:
        subprocess.run(['gnome-screenshot', '-a', '-f', tmp], check=True)
    except subprocess.CalledProcessError:
        root.deiconify()
        text_widget.insert(tk.END, "Seleção de área cancelada ou falha na captura.")
        return
    root.deiconify()
    root.lift()
    root.focus_force()
    # Aguarda arquivo existir antes de processar
    while not os.path.exists(tmp):
        root.update()
        root.after(100)
    process_image_file(tmp)

# Exibe imagem reduzida na interface
def display_image(image):
    max_w, max_h = 500, 300
    img = image.copy()
    try:
        resample = Image.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS
    img.thumbnail((max_w, max_h), resample)
    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo  # evita coleta de lixo

# Copia texto selecionado para clipboard
def copy_to_clipboard():
    try:
        selected = text_widget.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected)
    except tk.TclError:
        pass

# Copia imagem exibida para clipboard
def copy_image_to_clipboard():
    global last_image_data
    if not last_image_data:
        return
    try:
        subprocess.run(
            ['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'],
            input=last_image_data,
            check=True
        )
    except Exception:
        pass

# Mostra menu de contexto para texto
def show_text_context_menu(event):
    try:
        _ = text_widget.selection_get()
        text_context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        text_context_menu.grab_release()

# Mostra menu de contexto para imagem
def show_image_context_menu(event):
    image_context_menu.tk_popup(event.x_root, event.y_root)
    image_context_menu.grab_release()

# Inicializa GUI
def main():
    global root, text_widget, image_label, text_context_menu, image_context_menu
    root = ThemedTk(theme="equilux")
    root.title("OCR Clipboard App")
    root.geometry("600x650")

    btn = ttk.Button(root, text="Selecionar Área", command=select_area_ocr)
    btn.pack(pady=5)

    # Imagem capturada (menu de contexto para copiar)
    image_label = ttk.Label(root)
    image_label.pack(padx=10, pady=5)
    image_context_menu = tk.Menu(root, tearoff=0)
    image_context_menu.add_command(label="Copiar Imagem", command=copy_image_to_clipboard)
    image_label.bind('<Button-3>', show_image_context_menu)
    image_label.bind('<Button-1>', show_image_context_menu)

    # Área de texto (menu de contexto para copiar texto)
    text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
    text_context_menu = tk.Menu(root, tearoff=0)
    text_context_menu.add_command(label="Copiar Texto", command=copy_to_clipboard)
    text_widget.bind('<Button-3>', show_text_context_menu)
    text_widget.bind('<Button-1>', lambda e: None)

    root.mainloop()

if __name__ == "__main__":
    main()
