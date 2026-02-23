"""
QR Kod Oluşturucu
Modern dark-indigo arayüz · Kaydet · Panoya Kopyala
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
from PIL import Image, ImageTk, ImageDraw
import io

# Pano kopyalama (Windows)
try:
    import win32clipboard
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# ── Renk paleti ──────────────────────────────────────────────────────────────
BG       = "#0F0F17"   # en derin arka plan
SURFACE  = "#16161F"   # kart zemini
BORDER   = "#2A2A3D"   # ince kenarlık
ACCENT   = "#7C3AED"   # canlı mor (primary)
ACCENT2  = "#5B21B6"   # koyu mor (hover / secondary)
SUCCESS  = "#10B981"   # kaydet/kopyala tonu
TEXT     = "#F1F0FF"
SUBTEXT  = "#7070A0"
ENTRY_BG = "#1E1E2E"
WHITE    = "#FFFFFF"
QR_FG    = "#1E1E2E"   # QR koyu renk
QR_BG    = "#F8F8FF"   # QR açık arka plan

FONT     = "Segoe UI"


# ── Yardımcı: köşe yuvarlı dikdörtgen canvas ─────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, r=18, **kw):
    pts = [
        x1+r, y1,  x2-r, y1,
        x2, y1,    x2, y1+r,
        x2, y2-r,  x2, y2,
        x2-r, y2,  x1+r, y2,
        x1, y2,    x1, y2-r,
        x1, y1+r,  x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


# ── Ana uygulama ─────────────────────────────────────────────────────────────
class QRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Oluşturucu")
        self.geometry("480x680")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._qr_pil   = None   # PIL Image (kaydet/kopyala)
        self._tk_img   = None   # tkinter referansı

        self._build_ui()

    # ── Arayüz ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ••• Başlık •••
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(28, 0))

        tk.Label(hdr, text="QR Oluşturucu",
                 font=(FONT, 22, "bold"), bg=BG, fg=TEXT).pack(side="left")

        # ••• QR Kartı •••
        card_outer = tk.Frame(self, bg=BG)
        card_outer.pack(padx=30, pady=(18, 0))

        self._card_canvas = tk.Canvas(
            card_outer, width=420, height=360,
            bg=SURFACE, highlightthickness=1, highlightbackground=BORDER,
            relief="flat"
        )
        self._card_canvas.pack()
        self._draw_placeholder()

        # ••• Aksiyon butonları •••
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=30, pady=(14, 0))

        self.copy_btn = self._icon_btn(
            btn_row, "📋  Kopyala", SUCCESS, self._copy_to_clipboard, side="left"
        )
        self.save_btn = self._icon_btn(
            btn_row, "💾  Kaydet", ACCENT, self._save_qr, side="right"
        )
        # Başlangıçta pasif görünüm
        self._set_action_btns(enabled=False)

        # ••• Ayırıcı •••
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=30, pady=(20, 0))

        # ••• Giriş alanı •••
        entry_lbl = tk.Frame(self, bg=BG)
        entry_lbl.pack(fill="x", padx=30, pady=(16, 0))
        tk.Label(entry_lbl, text="İçerik", font=(FONT, 10, "bold"),
                 bg=BG, fg=SUBTEXT).pack(anchor="w")
        tk.Label(entry_lbl, text="URL, metin veya herhangi bir içerik yazın",
                 font=(FONT, 9), bg=BG, fg=SUBTEXT).pack(anchor="w")

        entry_wrap = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        entry_wrap.pack(fill="x", padx=30, pady=(8, 0))

        inner = tk.Frame(entry_wrap, bg=ENTRY_BG)
        inner.pack(fill="x")

        self.entry = tk.Entry(
            inner,
            font=(FONT, 13), bg=ENTRY_BG, fg=TEXT,
            insertbackground=ACCENT,
            relief="flat", bd=10,
            selectbackground=ACCENT2, selectforeground=WHITE
        )
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", lambda _: self._generate())
        self.entry.focus_set()

        # ••• Oluştur butonu •••
        gen_wrap = tk.Frame(self, bg=BG)
        gen_wrap.pack(fill="x", padx=30, pady=(16, 30))

        self.gen_btn = tk.Button(
            gen_wrap,
            text="  QR Oluştur  ⚡",
            font=(FONT, 13, "bold"),
            bg=ACCENT, fg=WHITE,
            activebackground=ACCENT2, activeforeground=WHITE,
            relief="flat", cursor="hand2",
            pady=13, bd=0,
            command=self._generate
        )
        self.gen_btn.pack(fill="x")
        self._add_hover(self.gen_btn, ACCENT, ACCENT2)

    # ── Yardımcılar ──────────────────────────────────────────────────────────
    def _icon_btn(self, parent, label, color, cmd, side):
        btn = tk.Button(
            parent, text=label,
            font=(FONT, 10, "bold"),
            bg=SURFACE, fg=color,
            activebackground=BORDER, activeforeground=color,
            relief="flat", cursor="hand2",
            padx=14, pady=8, bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            command=cmd
        )
        btn.pack(side=side)
        return btn

    def _set_action_btns(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in (self.copy_btn, self.save_btn):
            btn.configure(state=state)

    def _add_hover(self, widget, normal, hover):
        widget.bind("<Enter>", lambda _: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda _: widget.configure(bg=normal))

    # ── Yer tutucu ───────────────────────────────────────────────────────────
    def _draw_placeholder(self):
        c = self._card_canvas
        c.delete("all")
        w, h = 420, 360

        # Merkez noktalı dokular
        dot_gap = 24
        for xi in range(dot_gap, w, dot_gap):
            for yi in range(dot_gap, h, dot_gap):
                c.create_oval(xi-1, yi-1, xi+1, yi+1, fill=BORDER, outline="")

        # Daire + ikon
        cx, cy, r = w//2, h//2, 70
        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=BORDER, width=2, fill=SURFACE)
        c.create_text(cx, cy-10, text="▦", font=(FONT, 36), fill=BORDER)
        c.create_text(cx, cy+36, text="QR burada görünecek",
                      font=(FONT, 11), fill=SUBTEXT)

    # ── QR Oluştur ───────────────────────────────────────────────────────────
    def _generate(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showwarning("Uyarı", "Lütfen bir metin veya URL girin.", parent=self)
            return

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=9,
            border=3,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=QR_FG, back_color=QR_BG).convert("RGB")

        # 320×320 içine ortala, etrafı SURFACE dolgu
        SIZE = 320
        img = img.resize((SIZE, SIZE), Image.LANCZOS)

        canvas_img = Image.new("RGB", (420, 360), SURFACE)
        ox = (420 - SIZE) // 2
        oy = (360 - SIZE) // 2
        canvas_img.paste(img, (ox, oy))

        self._qr_pil = img   # orijinal QR
        self._tk_img = ImageTk.PhotoImage(canvas_img)

        c = self._card_canvas
        c.delete("all")
        c.create_image(0, 0, anchor="nw", image=self._tk_img)

        # Küçük etiket
        c.create_rectangle(0, 330, 420, 360, fill="#111118", outline="")
        c.create_text(210, 345, text="✓  QR hazır", font=(FONT, 10, "bold"),
                      fill=SUCCESS)

        self._set_action_btns(enabled=True)

    # ── Kaydet ───────────────────────────────────────────────────────────────
    def _save_qr(self):
        if self._qr_pil is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Tüm Dosyalar", "*.*")],
            title="QR Kodu Kaydet",
            parent=self
        )
        if path:
            self._qr_pil.save(path)
            messagebox.showinfo("Kaydedildi", f"QR kod kaydedildi:\n{path}", parent=self)

    # ── Panoya Kopyala ───────────────────────────────────────────────────────
    def _copy_to_clipboard(self):
        if self._qr_pil is None:
            return

        if not HAS_WIN32:
            messagebox.showerror(
                "Eksik Kütüphane",
                "Kopyalama için 'pywin32' gerekli.\n"
                "pip install pywin32 yazın ve tekrar deneyin.",
                parent=self
            )
            return

        try:
            # BMP formatında pano'ya yaz
            output = io.BytesIO()
            self._qr_pil.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]   # BMP başlığını atla (14 byte)
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

            # Kısa onay göster
            self._flash_status("📋  Panoya kopyalandı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kopyalama başarısız:\n{e}", parent=self)

    def _flash_status(self, msg: str):
        """Canvas altına kısa süre mesaj göster."""
        c = self._card_canvas
        tag = "flash"
        c.delete(tag)
        c.create_rectangle(0, 330, 420, 360, fill="#0D2B22", outline="", tags=tag)
        c.create_text(210, 345, text=msg, font=(FONT, 10, "bold"),
                      fill=SUCCESS, tags=tag)
        # 2 saniye sonra eski "QR hazır" etiketi dönüş
        def restore():
            c.delete(tag)
            c.create_rectangle(0, 330, 420, 360, fill="#111118", outline="")
            c.create_text(210, 345, text="✓  QR hazır", font=(FONT, 10, "bold"), fill=SUCCESS)
        self.after(2000, restore)


# ── Giriş noktası ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QRApp()
    app.mainloop()
