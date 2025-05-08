#!/usr/bin/env python3
import os
import tempfile
import subprocess
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance
import pytesseract
from googletrans import Translator

class OCRClipboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCR & Translate Clipboard App")
        self.geometry("600x800")

        # Arquivo temporário absoluto
        self.tmp = os.path.join(tempfile.gettempdir(), "ocr_area.png")

        # Tradutor
        self.translator = Translator()

        # Botão de captura
        self.btn = ttk.Button(self, text="Selecionar Área", command=self.select_area_ocr)
        self.btn.pack(pady=10)

        # Exibição da imagem
        self.image_label = ttk.Label(self)
        self.image_label.pack(pady=5)

        # Área OCR
        ttk.Label(self, text="Texto OCR:").pack(anchor="w", padx=10)
        self.text_ocr = tk.Text(self, wrap="word", height=12)
        self.text_ocr.pack(fill="both", expand=False, padx=10, pady=(0,10))

        # Área Tradução
        ttk.Label(self, text="Tradução (PT):").pack(anchor="w", padx=10)
        self.text_trans = tk.Text(self, wrap="word", height=8)
        self.text_trans.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Menu de contexto para imagem
        self.image_menu = tk.Menu(self, tearoff=0)
        self.image_menu.add_command(label="Copiar Imagem", command=self.copy_image_to_clipboard)
        self.image_label.bind("<Button-3>", self.show_image_menu)

        # Menu de contexto para text_ocr
        self.ocr_menu = tk.Menu(self, tearoff=0)
        self.ocr_menu.add_command(label="Copiar Texto", command=lambda: self.copy_text(self.text_ocr))
        self.text_ocr.bind("<Button-3>", lambda e: self.show_text_menu(e, self.ocr_menu))

        # Menu de contexto para text_trans
        self.trans_menu = tk.Menu(self, tearoff=0)
        self.trans_menu.add_command(label="Copiar Texto", command=lambda: self.copy_text(self.text_trans))
        self.text_trans.bind("<Button-3>", lambda e: self.show_text_menu(e, self.trans_menu))

    def select_area_ocr(self):
        # Limpa conteúdo antigo
        self.image_label.configure(image='')
        self.text_ocr.delete("1.0", tk.END)
        self.text_trans.delete("1.0", tk.END)

        # Guarda mtime anterior
        old_mtime = os.path.getmtime(self.tmp) if os.path.exists(self.tmp) else None

        # Esconde a janela
        self.withdraw()
        self.update()

        # Captura
        try:
            subprocess.run(["gnome-screenshot", "-a", "-f", self.tmp], check=True)
        except subprocess.CalledProcessError:
            self.deiconify()
            messagebox.showerror("Erro", "Falha ao capturar a área.")
            return

        # Restaura
        self.deiconify()
        self.update()
        self.lift()
        self.focus_force()

        # Aguarda novo arquivo
        while True:
            if os.path.exists(self.tmp):
                new_mtime = os.path.getmtime(self.tmp)
                if old_mtime is None or new_mtime != old_mtime:
                    break
            time.sleep(0.1)

        # Verifica existência
        if not os.path.exists(self.tmp):
            messagebox.showerror("Erro", f"Nenhuma área capturada:\n{self.tmp}")
            return

        # Carrega e mostra imagem
        try:
            img = Image.open(self.tmp)
        except Exception as e:
            messagebox.showerror("Erro ao abrir imagem", str(e))
            return
        img.thumbnail((500, 200), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=self.photo)

        # Pré-processamento OCR
        gray = Image.open(self.tmp).convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        contrast = enhancer.enhance(2.0)
        bw = contrast.point(lambda x: 0 if x < 128 else 255, '1')

        # Executa OCR
        try:
            texto = pytesseract.image_to_string(bw, lang="por+eng")
        except Exception as e:
            messagebox.showerror("Erro OCR", str(e))
            return
        self.text_ocr.insert("1.0", texto.strip())

        # Detecta idioma e traduz
        try:
            detected = self.translator.detect(texto)
            if detected.lang != 'pt':
                traduzido = self.translator.translate(texto, dest='pt').text
            else:
                traduzido = "--- Já está em português ---"
        except Exception as e:
            traduzido = f"[Erro na tradução: {e}]"
        self.text_trans.insert("1.0", traduzido)

    def show_image_menu(self, event):
        self.image_menu.tk_popup(event.x_root, event.y_root)
        self.image_menu.grab_release()

    def show_text_menu(self, event, menu):
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def copy_text(self, widget):
        try:
            sel = widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(sel)
        except tk.TclError:
            # sem seleção
            pass

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
