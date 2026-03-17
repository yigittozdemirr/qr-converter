# 📱 Modern QR Generator

A minimalist desktop application built with Python for fast QR code generation. Features seamless clipboard integration and a clean dark theme.

## ✨ Features
- **Instant Generation:** Convert URLs or text to QR codes.
- **Clipboard Support:** Copy QR images directly (Ctrl+V into any app).
- **File Export:** Save as PNG or JPEG.
- **Modern UI:** Dark-themed interface for a better user experience.

## 🛠️ Installation
```bash
pip install qrcode[pil] Pillow pywin32
```

## 🚀 Usage
```bash
python main.py
```

Enter Text/URL.

Press Enter or click Generate.

Use Copy to paste immediately or Save to export.

## 📦 Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon="assets/qr.ico" --name "QR_Generator" main.py
```

📄 License
MIT

Author: [Yiğit Özdemir](https://github.com/yigittozdemirr)
