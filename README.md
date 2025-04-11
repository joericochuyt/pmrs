# Emergency Transmission Scheduler

A cross-platform desktop application for generating **personalized emergency communication schedules** using configurable radio frequency bands. Ideal for coordination when normal infrastructure is unavailable.

![Screenshot](https://github.com/user-attachments/assets/641b123e-ddea-40ab-92d6-b2cdc98d3153)

---

## 🔧 Features

- Unique schedule generation based on two users' **dates of birth**
- **Configurable frequency bands**: PMRS, VLF, VHF, UHF, 2m Amateur, 70cm Amateur
- Three daily communication windows: **Morning, Afternoon, Evening**
- Smart use of **CTCSS tones** and dynamic channel rotation
- **Emergency quick-connect times** and **backup protocols**
- Export to:
  - 📄 TXT (Printable text summary)
  - 📊 CSV (View/edit with spreadsheet apps)
  - 📡 CHIRP-compatible `.chirp` file (for direct radio programming)
- GUI features:
  - Highlight current day
  - View full schedule and emergency channels
  - Load/export CSVs
- Cross-platform: **Windows**, **Linux**, and **macOS**

---

## 🧠 How It Works

Using two dates of birth, the tool generates a **predictable yet randomized schedule**. This includes:

- Personalized transmission windows (randomized within time blocks)
- Allocated channels from the selected **frequency band**
- Associated **frequencies and CTCSS tones**
- Two emergency fallback times
- A "backup protocol" to restore contact after prolonged silence

---

## 💻 Installation

### 🐍 Run from Source

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/pmrs-scheduler.git
   cd pmrs-scheduler
   ```
2. Install Python 3.9+ and required dependencies:
   ```bash
   pip install tk tkcalendar numpy
   ```
3. Launch the GUI:
   ```bash
   python app_gui.py
   ```

---

## 🏗️ Building Standalone Executables

### 🪟 Windows

```batch
pip install nuitka
nuitka --standalone --onefile --disable-console ^
  --include-data-files=schedule_generator_chirp.py=schedule_generator_chirp.py ^
  --include-module=tkcalendar --plugin-enable=tk-inter ^
  --enable-plugin=upx app_gui.py
upx --best app_gui.dist\app_gui.exe
```

### 🐧 Linux (via Docker)

```bash
docker build -t pmrs-linux-builder .
docker create --name pmrs-temp pmrs-linux-builder
docker cp pmrs-temp:/app/app_gui.dist/app_gui ./pmrs_scheduler_linux
docker rm pmrs-temp
```

> See the included Dockerfile in the project for full build setup.

### 🍎 macOS

```bash
pip install nuitka
nuitka --standalone --onefile --macos-create-app-bundle \
  --include-data-files=schedule_generator_chirp.py=schedule_generator_chirp.py \
  --include-module=tkcalendar --plugin-enable=tk-inter app_gui.py
```

---

## 🚀 Usage

1. Launch the GUI
2. Enter both users’ **dates of birth**
3. Select a **start date**, **frequency band**, and **rotation duration**
4. Click **"Generate Schedule"**
5. Export using one of the buttons: TXT, CSV, or CHIRP

---

## 📦 Requirements for Standalone Binaries

### Linux

```bash
sudo apt install libx11-6 tk
```

### macOS & Windows

- No additional dependencies

---

## 📜 License

[MIT License](LICENSE)
