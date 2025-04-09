# pmrs

This script generates a secure, randomized communication schedule for two individuals using their dates of birth (DOB) as the basis for reproducibility. It is designed for scenarios like emergency preparedness, where consistent yet varied radio transmission parameters are required. Here's a detailed breakdown:

Key Features
Input-Driven Randomization:

Uses dates of birth to seed the random number generator, ensuring reproducibility.

Generates a 14-day rotation cycle by default (customizable via --days).

Schedule Structure:

Three daily transmission windows:

Morning (6:00 AM – 10:00 AM)

Afternoon (12:00 PM – 4:00 PM)

Evening (7:00 PM – 11:00 PM)

Each window includes:

Time slot (5-minute duration, e.g., 06:15 - 06:20)

PMRS channel (1–22, with frequencies like 462.5625 MHz)

CTCSS tone (privacy code, e.g., 67.0 Hz).

Anti-Repetition Logic:

Avoids repeating times, channels, or tones within recent windows to minimize predictability.

Emergency Protocols:

Quick-connect times: Two emergency check-ins per hour, calculated from DOBs (e.g., XX:12 and XX:27).

Backup protocol: Fallback to Channel 1 if no contact is made after three cycles.

Export Options:

Export to CHIRP format for direct radio programming
Export to CSV for data analysis
Export to TXT for easy printing and reference

EXE
pyinstaller --onefile --windowed --add-data "schedule_generator_chirp.py;." --hidden-import tkcalendar app_gui.py

--onefile: Creates a single executable file instead of a directory
--windowed: Prevents a console window from appearing when the application runs
--add-data "schedule_generator_chirp.py;.": Includes the required schedule generator script in the executable (the ; separator is for Windows, use : on macOS/Linux)

