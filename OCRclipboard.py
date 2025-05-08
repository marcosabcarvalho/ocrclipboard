#!/usr/bin/env python3
import os
import tempfile
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance
import pytesseract

class OCRClipboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCR Clipboard App")
        self.geometry("600x600")

        # Caminho absoluto para o arquivo temporário
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

        # Menu de contexto na imagem (botão direito)
        self.image_menu = tk.Menu(self, tearoff=0)
        self.image_menu.add_command(label="Copiar Imagem", command=self.copy_image_to_clipboard)
        self.image_label.bind("<Button-3>", self.show_image_menu)

    def select_area_ocr(self):
        # 1) Limpa conteúdo antigo
        self.image_label.configure(image='')
        self.text.delete("1.0", tk.END)

        # 2) Armazena o mtime anterior, se já existir
        old_mtime = os.path.getmtime(self.tmp) if os.path.exists(self.tmp) else None

        # 3) Esconde totalmente a janela para não aparecer no screenshot
        self.withdraw()
        self.update()

        # 4) Chama o gnome-screenshot para seleção
        try:
            subprocess.run(["gnome-screenshot", "-a", "-f", self.tmp], check=True)
        except subprocess.CalledProcessError:
            # Se o usuário cancelar ou der erro, restaura e mostra mensagem
            self.deiconify()
            messagebox.showerror("Erro", "Falha ao capturar a área.")
            return

        # 5) Restaura a janela ao foco
        self.deiconify()
        self.update()
        self.lift()
        self.focus_force()

        # 6) Aguarda indefinidamente até que o arquivo seja atualizado
        while True:
            if os.path.exists(self.tmp):
                new_mtime = os.path.getmtime(self.tmp)
                if old_mtime is None or new_mtime != old_mtime:
                    break
            time.sleep(0.1)

        # 7) Verifica existência real
        if not os.path.exists(self.tmp):
            messagebox.showerror("Erro", f"Nenhuma área capturada:\n{self.tmp}")
            return

        # 8) Carrega e exibe a imagem (redimensionada)
        try:
            img = Image.open(self.tmp)
        except Exception as e:
            messagebox.showerror("Erro ao abrir imagem", str(e))
            return

        img.thumbnail((500, 200), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.photo)

        # 9) Pré-processamento + OCR
        try:
            # converte para escala de cinza
            gray = Image.open(self.tmp).convert('L')
            # aumenta contraste
            enhancer = ImageEnhance.Contrast(gray)
            contrast = enhancer.enhance(2.0)
            # binariza (ponto de corte em 128)
            bw = contrast.point(lambda x: 0 if x < 128 else 255, '1')
            # executa OCR na imagem binarizada
            texto = pytesseract.image_to_string(bw, lang="por")
        except Exception as e:
            messagebox.showerror("Erro OCR", str(e))
            return

        # insere o texto
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

if __name__ == "__main__":
    app = OCRClipboardApp()
    app.mainloop()
