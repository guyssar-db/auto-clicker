# 🖱️ Advanced Auto Clicker by guyssar

โปรแกรม Auto Clicker ขั้นสูงสำหรับ Windows  
✨ ใช้งานง่าย กำหนด Hotkey เองได้ จดจำโปรไฟล์ได้ Pick Mouse Position ได้

---

## 🚀 Features

- ตั้ง Click Interval ได้ละเอียด (ชั่วโมง/นาที/วินาที/มิลลิวินาที)
- เลือก Mouse Button ได้ (Left / Right / Middle)
- Single หรือ Double Click
- Repeat N times หรือ Click ไปเรื่อยๆ
- เลือกตำแหน่งเมาส์: Current หรือ Pick Location
- ตั้งค่า Hotkey ได้เอง
- บันทึก/โหลดโปรไฟล์ได้
- GUI ด้วย PyQt5

---

## 📥 Installation

1. ดาวน์โหลดหรือ Clone โครงการนี้:
   ```bash
   git clone https://github.com/guyssar-db/auto-clicker.git
   cd auto-clicker
   ```

2. ติดตั้ง Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. รันโปรแกรม:
   ```bash
   python autoclicker.py
   ```

---

## 🗃️ Build `.exe` (Windows)

1. เตรียมไฟล์ `icon.ico` อยู่ในโฟลเดอร์เดียวกัน
2. ติดตั้ง PyInstaller:
   ```bash
   pip install pyinstaller
   ```
3. สร้าง `.exe`:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico autoclicker.py
   ```
4. จะได้ไฟล์ `dist/autoclicker.exe`

---

## ⚙️ Configuration

- ไฟล์โปรไฟล์จะถูกสร้างเป็น `profiles.json` ในโฟลเดอร์เดียวกับไฟล์ `.exe`

---

## 📦 Dependencies

- Python 3.8+
- PyQt5
- pyautogui
- keyboard
- pynput

---

## 🧑‍💻 Author

by guyssar  
GitHub: [guyssar](https://github.com/guyssar-db)

---

## 📃 License

MIT License

# auto-clicker
