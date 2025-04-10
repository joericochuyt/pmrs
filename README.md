# PMRS Emergency Transmission Scheduler

A cross-platform desktop application for generating personalized emergency communication schedules using public mobile radio service (PMRS) channels. This tool helps coordinate emergency communications when normal infrastructure is unavailable.

![Schermafbeelding 2025-04-10 071217](https://github.com/user-attachments/assets/641b123e-ddea-40ab-92d6-b2cdc98d3153)


## Features

- Generates unique, personalized transmission schedules based on dates of birth
- Provides three scheduled transmission windows per day (morning, afternoon, evening)
- Creates emergency quick-connect times for urgent communication
- Includes backup protocol if regular schedule fails
- Exports to multiple formats:
  - CHIRP format (for direct radio programming)
  - CSV files (for record keeping)
  - TXT files (for printing)
- Cross-platform: Windows, Linux, and macOS support

## How It Works

The application generates a unique communication schedule using two dates of birth as seed values. This creates a rotating schedule with varying:

- Transmission times
- PMRS channels and frequencies
- CTCSS tones for privacy

The schedule follows a rotation pattern (default 14 days) and includes emergency quick-connect times that can be used at any hour of the day.

## Installation

### Pre-built Binaries

Download the latest pre-built binary for your platform from the [Releases](https://github.com/joericochuyt/pmrs-scheduler/releases) page.

### Running from Source

1. Clone this repository
2. Install Python 3.9 or higher
3. Install dependencies:
   ```
   pip install tk tkcalendar
   ```
4. Run the application:
   ```
   python app_gui.py
   ```

## Building Standalone Executables

### Windows

```batch
pip install nuitka
nuitka --standalone --onefile --disable-console --include-data-files=schedule_generator_chirp.py=schedule_generator_chirp.py --include-module=tkcalendar --plugin-enable=tk-inter --enable-plugin=upx app_gui.py
upx --best app_gui.dist\app_gui.exe
```

### Linux (using Docker from Windows)

1. Install Docker Desktop
2. Create a Dockerfile in your project directory:

```dockerfile
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    patchelf \
    upx-ucl \
    libx11-dev \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY app_gui.py schedule_generator_chirp.py /app/

# Install Python dependencies
RUN pip install --no-cache-dir nuitka tk tkcalendar

# Build the application
RUN python -m nuitka --standalone --onefile \
    --include-data-files=schedule_generator_chirp.py=schedule_generator_chirp.py \
    --include-module=tkcalendar \
    --plugin-enable=tk-inter \
    --enable-plugin=upx \
    app_gui.py

# Compress with UPX
RUN upx --best app_gui.dist/app_gui

# Make executable
RUN chmod +x app_gui.dist/app_gui
```

3. Build and extract the Linux executable:

```batch
docker build -t pmrs-linux-builder .
docker create --name pmrs-temp pmrs-linux-builder
docker cp pmrs-temp:/app/app_gui.dist/app_gui ./pmrs_scheduler_linux
docker rm pmrs-temp
```

### macOS

For macOS builds, you'll need to use a macOS machine:

```bash
pip install nuitka
nuitka --standalone --onefile --macos-create-app-bundle --include-data-files=schedule_generator_chirp.py=schedule_generator_chirp.py --include-module=tkcalendar --plugin-enable=tk-inter app_gui.py
```

## Usage

1. Enter the date of birth for both users
2. Select the start date for your schedule
3. Choose the number of days in rotation (default: 14)
4. Click "Generate Schedule"
5. Export the schedule to your preferred format

## Requirements for Running Standalone Binaries

### Linux
- libx11-6
- tk

Install with:
```bash
sudo apt-get install libx11-6 tk
```

### macOS
- No additional requirements

### Windows
- No additional requirements

## License

[MIT License](LICENSE)
