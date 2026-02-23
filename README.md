# QR Kod Oluşturucu

Python ile yazılmış, modern arayüze sahip masaüstü QR kod oluşturucu uygulaması.

![Önizleme](assets/preview.png)

## Özellikler

- **Anlık QR Üretimi** — URL, metin veya her türlü içerik
- **Panoya Kopyala** — Tek tıkla QR görselini kopyala, direkt yapıştır
- **PNG / JPEG Kaydet** — QR kodu dosya olarak dışa aktar
- **Modern Arayüz** — Koyu lacivert-mor tema, tkinter tabanlı

## Gereksinimler

```
Python 3.10+
```

## Kurulum

```bash
# Gerekli kütüphaneleri yükle
pip install qrcode[pil] Pillow pywin32
```

## Kullanım

```bash
python main.py
```

1. Alt kutucuğa **URL veya metin** yaz
2. **QR Oluştur** butonuna bas (ya da Enter)
3. **Kopyala** → Panoya kopyalar (Ctrl+V ile yapıştırılabilir)
4. **Kaydet** → PNG / JPEG olarak dışa aktar

## EXE Olarak Derleme

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon="assets/qr.ico" --name "QR_Olusturucu" main.py
```

Çıktı: `dist/QR_Olusturucu.exe`

## Lisans

MIT
