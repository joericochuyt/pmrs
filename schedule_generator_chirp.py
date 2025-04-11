import datetime
import random
import argparse
import hashlib
import numpy as np
import csv
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Define frequency ranges for different bands
FREQUENCY_BANDS = {
    "PMRS": {
        "channels": range(1, 31),  # 1-30 channels
        "frequencies": [f"462.{5625+i*0.025:.4f}" for i in range(8)] + 
                       [f"467.{5625+i*0.025:.4f}" for i in range(8)] +
                       [f"462.{6625+i*0.025:.4f}" for i in range(7)] +
                       [f"467.{6625+i*0.025:.4f}" for i in range(7)],
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8, 
                        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 
                        131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 
                        179.9, 186.2, 192.8, 203.5]
    },
    "VLF": {
        "channels": range(1, 11),  # 1-10 channels
        "frequencies": [f"{3.0+i*0.3:.1f}" for i in range(10)],  # 3.0-5.7 kHz
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8]
    },
    "VHF": {
        "channels": range(1, 21),  # 1-20 channels
        "frequencies": [f"{144.0+i*0.5:.3f}" for i in range(20)],  # 144-153.5 MHz
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8, 
                        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8]
    },
    "UHF": {
        "channels": range(1, 21),  # 1-20 channels
        "frequencies": [f"{430.0+i*0.5:.3f}" for i in range(20)],  # 430-439.5 MHz
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
                        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8]
    },
    "2m Amateur": {
        "channels": range(1, 21),  # 1-20 channels
        "frequencies": [f"{144.1+i*0.25:.3f}" for i in range(20)],  # Amateur 2m band
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
                        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8]
    },
    "70cm Amateur": {
        "channels": range(1, 21),  # 1-20 channels
        "frequencies": [f"{432.1+i*0.25:.3f}" for i in range(20)],  # Amateur 70cm band
        "ctcss_tones": [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8,
                        97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8]
    }
}


def generate_schedule(user1_dob, user2_dob, days, start_date=None, output_format=None, frequency_band="PMRS"):
    """
    Generate a communication schedule based on user inputs.
    
    Parameters:
    - user1_dob: Date of birth for User 1 in the format YYYY-MM-DD
    - user2_dob: Date of birth for User 2 in the format YYYY-MM-DD
    - days: Number of days in the rotation cycle
    - start_date: Starting date for the schedule (datetime.date object)
    - output_format: Format for output (None, 'txt', 'csv', or 'chirp')
    - frequency_band: Frequency band to use ("PMRS", "VLF", "VHF", "UHF", etc.)
    
    Returns:
    - schedule: Dictionary containing the schedule
    - meta: Dictionary containing metadata
    """
    
    # Get the selected frequency band configuration
    if frequency_band not in FREQUENCY_BANDS:
        raise ValueError(f"Unsupported frequency band: {frequency_band}")
        
    band_config = FREQUENCY_BANDS[frequency_band]
    
    # Get channels, frequencies, and CTCSS tones from the band configuration
    channels = list(band_config["channels"])
    frequencies = band_config["frequencies"]
    ctcss_tones = band_config["ctcss_tones"]
    
    # Convert DOBs to datetime objects
    try:
        u1_dob = datetime.datetime.strptime(user1_dob, "%Y-%m-%d")
        u2_dob = datetime.datetime.strptime(user2_dob, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format: {str(e)}")
    
    # Set start_date if not provided
    if start_date is None:
        start_date = datetime.date.today()
    
    # Calculate hash values from user DOBs
    hash_u1 = int(hashlib.sha256(u1_dob.strftime("%Y%m%d").encode()).hexdigest(), 16)
    hash_u2 = int(hashlib.sha256(u2_dob.strftime("%Y%m%d").encode()).hexdigest(), 16)
    
    # Use hash values to seed random generators
    seed_value = (hash_u1 + hash_u2) % (2**32 - 1)
    random.seed(seed_value)
    np.random.seed(seed_value)
    
    schedule = {}
    
    # Generate a list of dates starting from start_date
    dates = [start_date + datetime.timedelta(days=i) for i in range(days)]
    
    # Determine channel selection for each time period
    # Instead of hardcoding channel ranges like (1, 31), use the range from band_config
    channel_selection = random.sample(channels, min(len(channels), days * 3))
    
    # If we need more channels than are available, repeat with different offsets
    if days * 3 > len(channels):
        additional_needed = days * 3 - len(channels)
        additional_channels = []
        
        for i in range(additional_needed):
            # Pick from available channels again with a different seed
            seed_value = (hash_u1 + hash_u2 + i) % (2**32 - 1)
            random.seed(seed_value)
            additional_channels.append(random.choice(channels))
        
        channel_selection.extend(additional_channels)
    
    # Shuffle to ensure variety
    random.shuffle(channel_selection)
    
    # Reset seed
    random.seed(hash_u1 + hash_u2)
    
    # Determine CTCSS tone selection for each time period
    # Use the CTCSS tones from band_config instead of hardcoded list
    ctcss_selection = []
    for _ in range(days * 3):
        ctcss_selection.append(random.choice(ctcss_tones))
    
    # Create a consistent mapping between channels and frequencies based on user hashes
    channel_to_freq = {}
    
    # Use the frequencies from band_config instead of hardcoded list
    freq_pool = frequencies.copy()
    random.shuffle(freq_pool)
    
    for ch in channels:
        if freq_pool:
            channel_to_freq[ch] = freq_pool.pop(0)
        else:
            # If we run out of frequencies, start reusing them with an offset
            random.seed(hash_u1 + hash_u2 + ch)
            channel_to_freq[ch] = random.choice(frequencies)
    
    morning_start = 7
    morning_end = 10
    afternoon_start = 12
    afternoon_end = 15
    evening_start = 18
    evening_end = 21

    # Generate initial times
    morning_time = f"{random.randint(morning_start, morning_end-1)}:{random.choice(['00', '15', '30', '45'])}"
    afternoon_time = f"{random.randint(afternoon_start, afternoon_end-1)}:{random.choice(['00', '15', '30', '45'])}"
    evening_time = f"{random.randint(evening_start, evening_end-1)}:{random.choice(['00', '15', '30', '45'])}"
    
    # Keep track of used hours to avoid repetition
    used_morning_hours = set()
    used_afternoon_hours = set()
    used_evening_hours = set()
    
    # Keep track of recent channels and tones to avoid repetition
    recent_channels = []
    recent_tones = []
    
    for day in range(1, days + 1):
        # Reset if we've used all hours in a block
        if len(used_morning_hours) >= (morning_end - morning_start) * 4:
            used_morning_hours = set()
        if len(used_afternoon_hours) >= (afternoon_end - afternoon_start) * 4:
            used_afternoon_hours = set()
        if len(used_evening_hours) >= (evening_end - evening_start) * 4:
            used_evening_hours = set()
        
        # Generate times ensuring no repetition
        while True:
            morning_hour = random.randint(morning_start, morning_end - 1)
            morning_minute = random.choice([0, 15, 30, 45])
            morning_time = f"{morning_hour:02d}:{morning_minute:02d}"
            if morning_time not in used_morning_hours:
                used_morning_hours.add(morning_time)
                break
        
        while True:
            afternoon_hour = random.randint(afternoon_start, afternoon_end - 1)
            afternoon_minute = random.choice([0, 15, 30, 45])
            afternoon_time = f"{afternoon_hour:02d}:{afternoon_minute:02d}"
            if afternoon_time not in used_afternoon_hours:
                used_afternoon_hours.add(afternoon_time)
                break
        
        while True:
            evening_hour = random.randint(evening_start, evening_end - 1)
            evening_minute = random.choice([0, 15, 30, 45])
            evening_time = f"{evening_hour:02d}:{evening_minute:02d}"
            if evening_time not in used_evening_hours:
                used_evening_hours.add(evening_time)
                break
        
        # Generate channels for each time window
        # Avoid repeating recent channels
        available_channels = [ch for ch in channels if ch not in recent_channels[-3:]] if recent_channels else list(channels)
        
        morning_channel = random.choice(available_channels)
        recent_channels.append(morning_channel)
        if len(recent_channels) > 10:
            recent_channels.pop(0)
            
        available_channels = [ch for ch in channels if ch not in recent_channels[-3:]]
        afternoon_channel = random.choice(available_channels)
        recent_channels.append(afternoon_channel)
        if len(recent_channels) > 10:
            recent_channels.pop(0)
            
        available_channels = [ch for ch in channels if ch not in recent_channels[-3:]]
        evening_channel = random.choice(available_channels)
        recent_channels.append(evening_channel)
        if len(recent_channels) > 10:
            recent_channels.pop(0)
        
        # Generate CTCSS tones for each time window
        # Avoid repeating recent tones
        available_tones = [tone for tone in ctcss_tones if tone not in recent_tones[-5:]] if recent_tones else ctcss_tones.copy()
        
        morning_tone = random.choice(available_tones)
        recent_tones.append(morning_tone)
        if len(recent_tones) > 10:
            recent_tones.pop(0)
            
        available_tones = [tone for tone in ctcss_tones if tone not in recent_tones[-5:]]
        afternoon_tone = random.choice(available_tones)
        recent_tones.append(afternoon_tone)
        if len(recent_tones) > 10:
            recent_tones.pop(0)
            
        available_tones = [tone for tone in ctcss_tones if tone not in recent_tones[-5:]]
        evening_tone = random.choice(available_tones)
        recent_tones.append(evening_tone)
        if len(recent_tones) > 10:
            recent_tones.pop(0)
        
        schedule[day] = {
            "morning": {
                "time": f"{morning_time} - {morning_hour:02d}:{morning_minute+5:02d}",
                "channel": morning_channel,
                "frequency": channel_to_freq[morning_channel],
                "ctcss": morning_tone
            },
            "afternoon": {
                "time": f"{afternoon_time} - {afternoon_hour:02d}:{afternoon_minute+5:02d}",
                "channel": afternoon_channel,
                "frequency": channel_to_freq[afternoon_channel],
                "ctcss": afternoon_tone
            },
            "evening": {
                "time": f"{evening_time} - {evening_hour:02d}:{evening_minute+5:02d}",
                "channel": evening_channel,
                "frequency": channel_to_freq[evening_channel],
                "ctcss": evening_tone
            }
        }
    
    # Generate emergency quick-connect times and channels based on the combined DOB
    quick_connect_1 = (u1_dob.day + u2_dob.day) % 60
    quick_connect_2 = (u1_dob.month + u2_dob.month) % 60
    
    # Ensure they're at least 15 minutes apart
    while abs(quick_connect_1 - quick_connect_2) < 15:
        quick_connect_2 = (quick_connect_2 + 7) % 60
    
    # Generate emergency channels
    emergency_channel_1 = ((u1_dob.day + u2_dob.month) % len(channels)) + 1
    emergency_channel_2 = ((u1_dob.month + u2_dob.day) % len(channels)) + 1
    
    # Ensure different emergency channels
    if emergency_channel_1 == emergency_channel_2:
        emergency_channel_2 = emergency_channel_2 % 22 + 1
    
    # Generate emergency CTCSS tones
    emergency_tone_1 = ctcss_tones[((u1_dob.day + u2_dob.year) % len(ctcss_tones))]
    emergency_tone_2 = ctcss_tones[((u1_dob.year + u2_dob.day) % len(ctcss_tones))]
    
    # Add schedule metadata
    schedule_meta = {
        "quick_connect_times": [
            {
                "time": f"XX:{quick_connect_1:02d}",
                "channel": emergency_channel_1,
                "frequency": channel_to_freq[emergency_channel_1],
                "ctcss": emergency_tone_1
            },
            {
                "time": f"XX:{quick_connect_2:02d}",
                "channel": emergency_channel_2,
                "frequency": channel_to_freq[emergency_channel_2],
                "ctcss": emergency_tone_2
            }
        ],
        "seed": seed_value,
        "cycle_days": days
    }
    
    # Generate output files
    if output_format in ["text", "all"]:
        output_text_file(schedule, schedule_meta)
        
    if output_format in ["csv", "all"]:
        output_csv_file(schedule, schedule_meta)
        
    if output_format in ["chirp", "all"]:
        output_chirp_file(schedule, schedule_meta)
    
    return schedule, schedule_meta

def output_text_file(schedule, meta):
    """Output the schedule to a text file"""
    with open("emergency_schedule.txt", "w") as f:
        f.write("###### EMERGENCY TRANSMISSION SCHEDULE ######\n")
        f.write(f"Generated from personal information - {meta['cycle_days']}-Day Rotation\n\n")
        
        f.write("DAY | MORNING WINDOW | CHANNEL | FREQUENCY | CTCSS | AFTERNOON WINDOW | CHANNEL | FREQUENCY | CTCSS | EVENING WINDOW | CHANNEL | FREQUENCY | CTCSS\n")
        f.write("-" * 150 + "\n")
        
        for day in range(1, len(schedule) + 1):
            morning = schedule[day]['morning']
            afternoon = schedule[day]['afternoon']
            evening = schedule[day]['evening']
            
            f.write(f"{day:2d} | {morning['time']:13s} | Ch {morning['channel']:2d} | {morning['frequency']:8s} | {morning['ctcss']:5.1f} | ")
            f.write(f"{afternoon['time']:13s} | Ch {afternoon['channel']:2d} | {afternoon['frequency']:8s} | {afternoon['ctcss']:5.1f} | ")
            f.write(f"{evening['time']:13s} | Ch {evening['channel']:2d} | {evening['frequency']:8s} | {evening['ctcss']:5.1f}\n")
        
        f.write("\n## Emergency Quick-Connect Times ##\n")
        for i, qc in enumerate(meta['quick_connect_times'], 1):
            f.write(f"Quick Connect {i}: {qc['time']} on Channel {qc['channel']} ({qc['frequency']} MHz) with CTCSS {qc['ctcss']} Hz\n")
        
        f.write("\n## Backup Protocol ##\n")
        f.write(f"If no contact after three complete cycles ({meta['cycle_days'] * 3} days):\n")
        f.write("1. Try the top of each hour for 5 minutes for 24 hours\n")
        f.write("2. Use Channel 1 (462.5625 MHz) with CTCSS 67.0 Hz as the backup channel\n")
        f.write("3. Return to primary schedule after the 24-hour attempt\n")
        
        f.write("\n## Notes ##\n")
        f.write("- Keep transmissions brief (30-60 seconds)\n")
        f.write("- Listen before transmitting\n")
        f.write("- If a channel is busy, try the next channel up\n")
        f.write("- Each transmission window is 5 minutes long\n")
        f.write("- Use CTCSS tones to reduce interference and ensure privacy\n")
        f.write("- CHIRP file included for direct radio programming\n")
    
    print(f"Text schedule saved to emergency_schedule.txt")

def output_csv_file(schedule, meta):
    """Output the schedule to a CSV file"""
    with open("emergency_schedule.csv", "w", newline='') as csvfile:
        fieldnames = [
            'Day', 'Morning Time', 'Morning Channel', 'Morning Frequency', 'Morning CTCSS',
            'Afternoon Time', 'Afternoon Channel', 'Afternoon Frequency', 'Afternoon CTCSS',
            'Evening Time', 'Evening Channel', 'Evening Frequency', 'Evening CTCSS'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for day in range(1, len(schedule) + 1):
            writer.writerow({
                'Day': day,
                'Morning Time': schedule[day]['morning']['time'],
                'Morning Channel': schedule[day]['morning']['channel'],
                'Morning Frequency': schedule[day]['morning']['frequency'],
                'Morning CTCSS': schedule[day]['morning']['ctcss'],
                'Afternoon Time': schedule[day]['afternoon']['time'],
                'Afternoon Channel': schedule[day]['afternoon']['channel'],
                'Afternoon Frequency': schedule[day]['afternoon']['frequency'],
                'Afternoon CTCSS': schedule[day]['afternoon']['ctcss'],
                'Evening Time': schedule[day]['evening']['time'],
                'Evening Channel': schedule[day]['evening']['channel'],
                'Evening Frequency': schedule[day]['evening']['frequency'],
                'Evening CTCSS': schedule[day]['evening']['ctcss']
            })
    
    # Write emergency info to a separate CSV
    with open("emergency_quick_connect.csv", "w", newline='') as csvfile:
        fieldnames = ['Type', 'Time', 'Channel', 'Frequency', 'CTCSS', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerow({
            'Type': 'Quick Connect 1',
            'Time': meta['quick_connect_times'][0]['time'],
            'Channel': meta['quick_connect_times'][0]['channel'],
            'Frequency': meta['quick_connect_times'][0]['frequency'],
            'CTCSS': meta['quick_connect_times'][0]['ctcss'],
            'Notes': 'Check at minutes past any hour'
        })
        writer.writerow({
            'Type': 'Quick Connect 2',
            'Time': meta['quick_connect_times'][1]['time'],
            'Channel': meta['quick_connect_times'][1]['channel'],
            'Frequency': meta['quick_connect_times'][1]['frequency'],
            'CTCSS': meta['quick_connect_times'][1]['ctcss'],
            'Notes': 'Check at minutes past any hour'
        })
        writer.writerow({
            'Type': 'Backup Protocol',
            'Time': 'XX:00',
            'Channel': 1,
            'Frequency': '462.5625',
            'CTCSS': 67.0,
            'Notes': f'If no contact after {meta["cycle_days"] * 3} days'
        })
    
    print(f"CSV schedule saved to emergency_schedule.csv and emergency_quick_connect.csv")

def output_chirp_file(schedule, meta, file_path="emergency_schedule.chirp"):
    """Output the schedule to a CHIRP compatible file"""
    # Create the root element
    root = ET.Element("memories", version="1.0")
    
    # Add memory entries for each scheduled transmission
    memory_count = 1
    
    # Add normal schedule channels
    for day in range(1, len(schedule) + 1):
        # Morning channel
        morning = schedule[day]['morning']
        morning_memory = ET.SubElement(root, "memory")
        ET.SubElement(morning_memory, "number").text = str(memory_count)
        ET.SubElement(morning_memory, "name").text = f"D{day}M"
        ET.SubElement(morning_memory, "frequency").text = morning['frequency']
        ET.SubElement(morning_memory, "tmode").text = "TSQL"
        ET.SubElement(morning_memory, "ctone").text = str(morning['ctcss'])
        ET.SubElement(morning_memory, "rtone").text = str(morning['ctcss'])
        ET.SubElement(morning_memory, "comment").text = f"Day {day} Morning {morning['time']}"
        memory_count += 1
        
        # Afternoon channel
        afternoon = schedule[day]['afternoon']
        afternoon_memory = ET.SubElement(root, "memory")
        ET.SubElement(afternoon_memory, "number").text = str(memory_count)
        ET.SubElement(afternoon_memory, "name").text = f"D{day}A"
        ET.SubElement(afternoon_memory, "frequency").text = afternoon['frequency']
        ET.SubElement(afternoon_memory, "tmode").text = "TSQL"
        ET.SubElement(afternoon_memory, "ctone").text = str(afternoon['ctcss'])
        ET.SubElement(afternoon_memory, "rtone").text = str(afternoon['ctcss'])
        ET.SubElement(afternoon_memory, "comment").text = f"Day {day} Afternoon {afternoon['time']}"
        memory_count += 1
        
        # Evening channel
        evening = schedule[day]['evening']
        evening_memory = ET.SubElement(root, "memory")
        ET.SubElement(evening_memory, "number").text = str(memory_count)
        ET.SubElement(evening_memory, "name").text = f"D{day}E"
        ET.SubElement(evening_memory, "frequency").text = evening['frequency']
        ET.SubElement(evening_memory, "tmode").text = "TSQL"
        ET.SubElement(evening_memory, "ctone").text = str(evening['ctcss'])
        ET.SubElement(evening_memory, "rtone").text = str(evening['ctcss'])
        ET.SubElement(evening_memory, "comment").text = f"Day {day} Evening {evening['time']}"
        memory_count += 1
    
    # Add emergency quick-connect channels
    for i, qc in enumerate(meta['quick_connect_times'], 1):
        qc_memory = ET.SubElement(root, "memory")
        ET.SubElement(qc_memory, "number").text = str(memory_count)
        ET.SubElement(qc_memory, "name").text = f"QC{i}"
        ET.SubElement(qc_memory, "frequency").text = qc['frequency']
        ET.SubElement(qc_memory, "tmode").text = "TSQL"
        ET.SubElement(qc_memory, "ctone").text = str(qc['ctcss'])
        ET.SubElement(qc_memory, "rtone").text = str(qc['ctcss'])
        ET.SubElement(qc_memory, "comment").text = f"Quick Connect {i}: {qc['time']}"
        memory_count += 1
    
    # Add backup channel
    backup_memory = ET.SubElement(root, "memory")
    ET.SubElement(backup_memory, "number").text = str(memory_count)
    ET.SubElement(backup_memory, "name").text = "BACKUP"
    ET.SubElement(backup_memory, "frequency").text = "462.5625"
    ET.SubElement(backup_memory, "tmode").text = "TSQL"
    ET.SubElement(backup_memory, "ctone").text = "67.0"
    ET.SubElement(backup_memory, "rtone").text = "67.0"
    ET.SubElement(backup_memory, "comment").text = "Backup channel - top of hour"
    
    # Create XML tree and save to file
    tree = ET.ElementTree(root)
    
    # Pretty print the XML
    xml_string = ET.tostring(root, encoding='unicode')
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
    
    with open(file_path, "w") as f:
        f.write(pretty_xml)
    
    print(f"CHIRP file saved to {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate an emergency transmission schedule based on dates of birth')
    parser.add_argument('user1_dob', help='First user\'s date of birth in format YYYY-MM-DD')
    parser.add_argument('user2_dob', help='Second user\'s date of birth in format YYYY-MM-DD')
    parser.add_argument('--days', type=int, default=14, help='Number of days in the rotation cycle (default: 14)')
    parser.add_argument('--output', choices=['text', 'csv', 'chirp', 'all'], default='all', help='Output format (default: all)')
    
    args = parser.parse_args()
    
    try:
        user1_dob = args.user1_dob
        user2_dob = args.user2_dob
        days = args.days
        output_format = args.output
        
        schedule, meta = generate_schedule(user1_dob, user2_dob, days, output_format)
        print(f"Emergency schedule successfully generated with {days} days in rotation.")
        print(f"This schedule uses {len(set(day[period]['channel'] for day in schedule.values() for period in day))} different PMRS channels.")
        print(f"This schedule uses {len(set(day[period]['ctcss'] for day in schedule.values() for period in day))} different CTCSS tones.")
        print(f"Total memory channels in CHIRP file: {days * 3 + 3}")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please ensure dates are in the format YYYY-MM-DD")
