import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import os
import sys
from tkcalendar import DateEntry
import schedule_generator_chirp as sgc
import pandas as pd

class PMRSSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PMRS Emergency Scheduler")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        
        # Variables for user inputs
        self.user1_dob_var = tk.StringVar()
        self.user2_dob_var = tk.StringVar()
        self.days_var = tk.IntVar(value=14)
        
        # Store generated schedule
        self.schedule = None
        self.schedule_meta = None
        
        # Create the UI
        self.create_ui()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="PMRS Emergency Transmission Scheduler", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Schedule Parameters", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input Fields
        input_grid = ttk.Frame(input_frame)
        input_grid.pack(fill=tk.X, padx=5, pady=5)
        
        # User 1 DOB
        ttk.Label(input_grid, text="User 1 Date of Birth:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.user1_dob_entry = DateEntry(input_grid, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.user1_dob_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # User 2 DOB
        ttk.Label(input_grid, text="User 2 Date of Birth:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.user2_dob_entry = DateEntry(input_grid, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.user2_dob_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Days in rotation
        ttk.Label(input_grid, text="Days in Rotation:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        days_entry = ttk.Spinbox(input_grid, from_=1, to=30, textvariable=self.days_var, width=5)
        days_entry.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        
        # Generate Button
        generate_btn = ttk.Button(input_grid, text="Generate Schedule", command=self.generate_schedule)
        generate_btn.grid(row=0, column=6, padx=20, pady=5)
        
        # Export Buttons Frame
        export_frame = ttk.Frame(input_grid)
        export_frame.grid(row=1, column=0, columnspan=7, pady=10)
        
        # Export Buttons
        ttk.Button(export_frame, text="Export to CHIRP", command=self.export_chirp).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export to TXT", command=self.export_txt).pack(side=tk.LEFT, padx=5)
        
        # Results Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Regular Schedule Tab
        self.schedule_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_tab, text="Regular Schedule")
        
        # Create treeview for regular schedule
        self.create_schedule_treeview()
        
        # Emergency Quick Connect Tab
        self.emergency_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.emergency_tab, text="Emergency Quick Connect")
        
        # Create treeview for emergency schedule
        self.create_emergency_treeview()
        
        # Info Tab
        self.info_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.info_tab, text="Information")
        
        # Create Info Content
        self.create_info_content()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to generate schedule")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def create_schedule_treeview(self):
        # Frame for the treeview
        frame = ttk.Frame(self.schedule_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        y_scrollbar = ttk.Scrollbar(frame, orient="vertical")
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        columns = (
            "day", 
            "morning_time", "morning_channel", "morning_freq", "morning_ctcss",
            "afternoon_time", "afternoon_channel", "afternoon_freq", "afternoon_ctcss",
            "evening_time", "evening_channel", "evening_freq", "evening_ctcss"
        )
        self.schedule_tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=y_scrollbar.set)
        
        # Configure columns
        self.schedule_tree.heading("day", text="Day")
        self.schedule_tree.column("day", width=40, anchor=tk.CENTER)
        
        self.schedule_tree.heading("morning_time", text="Morning Time")
        self.schedule_tree.column("morning_time", width=100, anchor=tk.CENTER)
        
        self.schedule_tree.heading("morning_channel", text="Ch")
        self.schedule_tree.column("morning_channel", width=40, anchor=tk.CENTER)
        
        self.schedule_tree.heading("morning_freq", text="Frequency")
        self.schedule_tree.column("morning_freq", width=80, anchor=tk.CENTER)
        
        self.schedule_tree.heading("morning_ctcss", text="CTCSS")
        self.schedule_tree.column("morning_ctcss", width=60, anchor=tk.CENTER)
        
        self.schedule_tree.heading("afternoon_time", text="Afternoon Time")
        self.schedule_tree.column("afternoon_time", width=100, anchor=tk.CENTER)
        
        self.schedule_tree.heading("afternoon_channel", text="Ch")
        self.schedule_tree.column("afternoon_channel", width=40, anchor=tk.CENTER)
        
        self.schedule_tree.heading("afternoon_freq", text="Frequency")
        self.schedule_tree.column("afternoon_freq", width=80, anchor=tk.CENTER)
        
        self.schedule_tree.heading("afternoon_ctcss", text="CTCSS")
        self.schedule_tree.column("afternoon_ctcss", width=60, anchor=tk.CENTER)
        
        self.schedule_tree.heading("evening_time", text="Evening Time")
        self.schedule_tree.column("evening_time", width=100, anchor=tk.CENTER)
        
        self.schedule_tree.heading("evening_channel", text="Ch")
        self.schedule_tree.column("evening_channel", width=40, anchor=tk.CENTER)
        
        self.schedule_tree.heading("evening_freq", text="Frequency")
        self.schedule_tree.column("evening_freq", width=80, anchor=tk.CENTER)
        
        self.schedule_tree.heading("evening_ctcss", text="CTCSS")
        self.schedule_tree.column("evening_ctcss", width=60, anchor=tk.CENTER)
        
        # Pack treeview
        self.schedule_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        y_scrollbar.config(command=self.schedule_tree.yview)
    
    def create_emergency_treeview(self):
        # Frame for the treeview
        frame = ttk.Frame(self.emergency_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        y_scrollbar = ttk.Scrollbar(frame, orient="vertical")
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        columns = ("type", "time", "channel", "frequency", "ctcss", "notes")
        self.emergency_tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=y_scrollbar.set)
        
        # Configure columns
        self.emergency_tree.heading("type", text="Type")
        self.emergency_tree.column("type", width=100, anchor=tk.W)
        
        self.emergency_tree.heading("time", text="Time")
        self.emergency_tree.column("time", width=80, anchor=tk.CENTER)
        
        self.emergency_tree.heading("channel", text="Channel")
        self.emergency_tree.column("channel", width=60, anchor=tk.CENTER)
        
        self.emergency_tree.heading("frequency", text="Frequency")
        self.emergency_tree.column("frequency", width=100, anchor=tk.CENTER)
        
        self.emergency_tree.heading("ctcss", text="CTCSS")
        self.emergency_tree.column("ctcss", width=80, anchor=tk.CENTER)
        
        self.emergency_tree.heading("notes", text="Notes")
        self.emergency_tree.column("notes", width=300, anchor=tk.W)
        
        # Pack treeview
        self.emergency_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        y_scrollbar.config(command=self.emergency_tree.yview)
    
    def create_info_content(self):
        # Create a text widget for the info
        info_text = tk.Text(self.info_tab, wrap=tk.WORD, padx=10, pady=10)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert information about the application
        info_text.insert(tk.END, "PMRS Emergency Transmission Scheduler\n\n", "title")
        info_text.insert(tk.END, "This application generates personalized transmission schedules for emergency communications using public mobile radio service (PMRS) channels.\n\n")
        
        info_text.insert(tk.END, "How It Works:\n\n", "header")
        info_text.insert(tk.END, "1. Enter the date of birth for two users to generate a unique schedule\n")
        info_text.insert(tk.END, "2. Select the number of days in the rotation cycle\n")
        info_text.insert(tk.END, "3. Click 'Generate Schedule' to create your personalized schedule\n")
        info_text.insert(tk.END, "4. Export the schedule to CHIRP format for direct radio programming, or CSV/TXT for record keeping\n\n")
        
        info_text.insert(tk.END, "Schedule Features:\n\n", "header")
        info_text.insert(tk.END, "• Three communication windows per day (morning, afternoon, evening)\n")
        info_text.insert(tk.END, "• Each window has a specific channel, frequency, and CTCSS tone\n")
        info_text.insert(tk.END, "• Emergency quick-connect times for urgent communications\n")
        info_text.insert(tk.END, "• Backup protocol if regular schedule fails\n\n")
        
        info_text.insert(tk.END, "Usage Notes:\n\n", "header")
        info_text.insert(tk.END, "• Keep transmissions brief (30-60 seconds)\n")
        info_text.insert(tk.END, "• Listen before transmitting\n")
        info_text.insert(tk.END, "• If a channel is busy, try the next channel up\n")
        info_text.insert(tk.END, "• Each transmission window is 5 minutes long\n")
        info_text.insert(tk.END, "• Use CTCSS tones to reduce interference\n")
        
        # Configure text tags
        info_text.tag_configure("title", font=("Arial", 14, "bold"))
        info_text.tag_configure("header", font=("Arial", 12, "bold"))
        
        # Make text widget read-only
        info_text.config(state=tk.DISABLED)
    
    def generate_schedule(self):
        try:
            # Get input values
            user1_dob = self.user1_dob_entry.get()
            user2_dob = self.user2_dob_entry.get()
            days = self.days_var.get()
            
            # Clear existing treeview data
            for item in self.schedule_tree.get_children():
                self.schedule_tree.delete(item)
            
            for item in self.emergency_tree.get_children():
                self.emergency_tree.delete(item)
            
            # Generate schedule (don't create files yet)
            self.schedule, self.schedule_meta = sgc.generate_schedule(user1_dob, user2_dob, days, output_format=None)
            
            # Update status
            self.status_var.set(f"Schedule generated with {days} days in rotation.")
            
            # Populate the regular schedule treeview
            for day in range(1, days + 1):
                self.schedule_tree.insert("", tk.END,
                    values=(
                        day,
                        self.schedule[day]['morning']['time'],
                        self.schedule[day]['morning']['channel'],
                        self.schedule[day]['morning']['frequency'],
                        f"{self.schedule[day]['morning']['ctcss']:.1f}",
                        self.schedule[day]['afternoon']['time'],
                        self.schedule[day]['afternoon']['channel'],
                        self.schedule[day]['afternoon']['frequency'],
                        f"{self.schedule[day]['afternoon']['ctcss']:.1f}",
                        self.schedule[day]['evening']['time'],
                        self.schedule[day]['evening']['channel'],
                        self.schedule[day]['evening']['frequency'],
                        f"{self.schedule[day]['evening']['ctcss']:.1f}"
                    )
                )
            
            # Populate the emergency treeview
            self.emergency_tree.insert("", tk.END,
                values=(
                    "Quick Connect 1",
                    self.schedule_meta['quick_connect_times'][0]['time'],
                    self.schedule_meta['quick_connect_times'][0]['channel'],
                    self.schedule_meta['quick_connect_times'][0]['frequency'],
                    f"{self.schedule_meta['quick_connect_times'][0]['ctcss']:.1f}",
                    "Check at minutes past any hour"
                )
            )
            
            self.emergency_tree.insert("", tk.END,
                values=(
                    "Quick Connect 2",
                    self.schedule_meta['quick_connect_times'][1]['time'],
                    self.schedule_meta['quick_connect_times'][1]['channel'],
                    self.schedule_meta['quick_connect_times'][1]['frequency'],
                    f"{self.schedule_meta['quick_connect_times'][1]['ctcss']:.1f}",
                    "Check at minutes past any hour"
                )
            )
            
            self.emergency_tree.insert("", tk.END,
                values=(
                    "Backup Protocol",
                    "XX:00",
                    1,
                    "462.5625",
                    "67.0",
                    f"If no contact after {self.schedule_meta['cycle_days'] * 3} days"
                )
            )
            
            # Switch to the schedule tab
            self.notebook.select(0)
            
            messagebox.showinfo("Success", f"Schedule successfully generated with {days} days in rotation.")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            self.status_var.set("Error generating schedule. Check inputs.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error generating schedule.")
    
    def export_chirp(self):
        if not self.schedule:
            messagebox.showwarning("Warning", "No schedule has been generated yet.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".chirp",
                filetypes=[("CHIRP Files", "*.chirp"), ("All Files", "*.*")],
                title="Save CHIRP File"
            )
            
            if file_path:
                # Generate the CHIRP XML file
                sgc.output_chirp_file(self.schedule, self.schedule_meta)
                
                # Copy the generated file to the selected location
                if os.path.exists("emergency_schedule.chirp"):
                    # Read the content
                    with open("emergency_schedule.chirp", "r") as src_file:
                        content = src_file.read()
                    
                    # Write to the selected location
                    with open(file_path, "w") as dest_file:
                        dest_file.write(content)
                    
                    # Remove the original file
                    os.remove("emergency_schedule.chirp")
                    
                    self.status_var.set(f"CHIRP file saved to {file_path}")
                    messagebox.showinfo("Success", f"CHIRP file saved to {file_path}")
                else:
                    messagebox.showerror("Error", "CHIRP file generation failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CHIRP file: {str(e)}")
            self.status_var.set("Error exporting CHIRP file.")
    
    def export_csv(self):
        if not self.schedule:
            messagebox.showwarning("Warning", "No schedule has been generated yet.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save CSV File"
            )
            
            if file_path:
                # Generate the CSV file
                sgc.output_csv_file(self.schedule, self.schedule_meta)
                
                # Copy the generated file to the selected location
                if os.path.exists("emergency_schedule.csv"):
                    # Read the content
                    with open("emergency_schedule.csv", "r") as src_file:
                        content = src_file.read()
                    
                    # Write to the selected location
                    with open(file_path, "w") as dest_file:
                        dest_file.write(content)
                    
                    # Remove the original file
                    os.remove("emergency_schedule.csv")
                    
                    self.status_var.set(f"CSV file saved to {file_path}")
                    messagebox.showinfo("Success", f"CSV file saved to {file_path}")
                else:
                    messagebox.showerror("Error", "CSV file generation failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV file: {str(e)}")
            self.status_var.set("Error exporting CSV file.")
    
    def export_txt(self):
        if not self.schedule:
            messagebox.showwarning("Warning", "No schedule has been generated yet.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Text File"
            )
            
            if file_path:
                # Generate the text file
                sgc.output_text_file(self.schedule, self.schedule_meta)
                
                # Copy the generated file to the selected location
                if os.path.exists("emergency_schedule.txt"):
                    # Read the content
                    with open("emergency_schedule.txt", "r") as src_file:
                        content = src_file.read()
                    
                    # Write to the selected location
                    with open(file_path, "w") as dest_file:
                        dest_file.write(content)
                    
                    # Remove the original file
                    os.remove("emergency_schedule.txt")
                    
                    self.status_var.set(f"Text file saved to {file_path}")
                    messagebox.showinfo("Success", f"Text file saved to {file_path}")
                else:
                    messagebox.showerror("Error", "Text file generation failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export text file: {str(e)}")
            self.status_var.set("Error exporting text file.")


def main():
    root = tk.Tk()
    app = PMRSSchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()