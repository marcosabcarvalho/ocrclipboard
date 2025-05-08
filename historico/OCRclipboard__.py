#!/usr/bin/env python3
import os
import tempfile
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pytesseract

class OCRClipboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCR Clipboard App")
        self.geometry("600x600")

        # Pasta temporária (sempre absoluta!)
        self.tmp = os.path.join(tempfile.gettempdir(), "ocr_area.png")

        # Botão para selecionar área
        self.btn = ttk.Button(self, text="Selecionar Área", command=self.select_area_ocr)
        self.btn.pack(pady=10)

        # Label para exibir imagem
        self.image_label = ttk.Label(self)
        self.image_label.pack(pady=5)

        # Textarea para o texto OCR
        self.text = tk.Text(self, wrap="word", height=15)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        # Menu de contexto na imagem
        self.image_menu = tk.Menu(self, tearoff=0)
        self.image_menu.add_command(label="Copiar Imagem", command=self.copy_image_to_clipboard)
        self.image_label.bind("<Button-3>", self.show_image_menu)

    def select_area_ocr(self):
        # --- 1) Limpa qualquer conteúdo antigo ---
        self.image_label.configure(image='')
        self.text.delete("1.0", tk.END)

        # --- 2) Armazena o mtime anterior (se existir) ---
        old_mtime = None
        if os.path.exists(self.tmp):
            old_mtime = os.path.getmtime(self.tmp)

        # Oculta a janela para não atrapalhar o screenshot
        self.withdraw()
        try:
            subprocess.run(["gnome-screenshot", "-a", "-f", self.tmp], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Erro", "Falha ao capturar a área.")
            self.deiconify()
            return

        # Traz a janela de volta
        self.deiconify()

        # --- 3) Aguarda indefinidamente até o novo arquivo aparecer ---
        while True:
            if os.path.exists(self.tmp):
                new_mtime = os.path.getmtime(self.tmp)
                if old_mtime is None or new_mtime != old_mtime:
                    break
            time.sleep(0.1)

        # Verifica existência do arquivo
        if not os.path.exists(self.tmp):
            messagebox.showerror("Erro", f"Nenhuma área capturada:\n{self.tmp}")
            return

        # Exibe a imagem
        try:
            img = Image.open(self.tmp)
        except Exception as e:
            messagebox.showerror("Erro ao abrir imagem", str(e))
            return

        # Redimensiona mantendo proporção
        max_w, max_h = 500, 200
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.photo)

        # Executa OCR e preenche o textarea
        try:
            texto = pytesseract.image_to_string(Image.open(self.tmp), lang="por")
        except Exception as e:
            messagebox.showerror("Erro OCR", str(e))
            return

        self.text.insert("1.0", texto)

    def show_image_menu(self, event):
        self.image_menu.tk_popup(event.x_root, event.y_root)
        self.image_menu.grab_release()

    def copy_image_to_clipboard(self):
        try:
            subprocess.run([
                "xclip", "-selection", "clipboard",
                "-t", "image/png", "-i", self.tmp
            ], check=True)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao copiar imagem:\n{e}")
        # textbox de confirmação removido

if __name__ == "__main__":
    app = OCRClipboardApp()
    app.mainloop()
