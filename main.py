import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import subprocess
import threading
from pathlib import Path
import re

class FlacToMp3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("FLAC to MP3 Converter")
        self.root.geometry("800x750") # Increased height to accommodate new fields
        
        # Configuration file path
        self.config_file = "converter_config.json"
        
        # Default settings
        self.settings = {
            "source_folder": "",
            "destination_folder": "",
            "filename_template": "{artist} - {title}",
            # C:\Program Files (x86)\foobar2000\encoders\lame.exe
            "lame_path": "" if os.name == "nt" else "/usr/bin/lame",
            # C:\Program Files\ffmpeg\bin\ffmpeg.exe
            "ffmpeg_path": "" if os.name == "nt" else "/usr/bin/ffmpeg",
            # C:\Program Files\ffmpeg\bin\ffprobe.exe
            "ffprobe_path": "" if os.name == "nt" else "/usr/bin/ffprobe",
            "quality": "320"
        }
        
        self.load_settings()
        self.create_widgets()
        
    def load_settings(self):
        """Load settings from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Source folder selection
        ttk.Label(main_frame, text="Source Folder (FLAC files):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar(value=self.settings["source_folder"])
        self.source_entry = ttk.Entry(main_frame, textvariable=self.source_var, width=60)
        self.source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)
        
        # Destination folder selection
        ttk.Label(main_frame, text="Destination Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_var = tk.StringVar(value=self.settings["destination_folder"])
        self.dest_entry = ttk.Entry(main_frame, textvariable=self.dest_var, width=60)
        self.dest_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_destination).grid(row=1, column=2, padx=5, pady=5)
        
        # Filename template
        ttk.Label(main_frame, text="Filename Template:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.template_var = tk.StringVar(value=self.settings["filename_template"])
        self.template_entry = ttk.Entry(main_frame, textvariable=self.template_var, width=60)
        self.template_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Template help
        help_text = "Available variables: {artist}, {title}, {album}, {track}, {year}"
        ttk.Label(main_frame, text=help_text, font=("Arial", 8)).grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # LAME path
        lame_frame = ttk.Frame(main_frame) 
        lame_frame.grid(row=4, column=0, columnspan=3, sticky='w', padx=0, pady=5) 
        
        ttk.Label(lame_frame, text="LAME Encoder Path:").grid(row=0, column=0, sticky='w')
        self.lame_path_var = tk.StringVar(value=self.settings["lame_path"])
        self.lame_path_entry = ttk.Entry(lame_frame, textvariable=self.lame_path_var, width=50) 
        self.lame_path_entry.grid(row=0, column=1, padx=5)
        
        self.lame_status_label = ttk.Label(lame_frame, text="❓")
        self.lame_status_label.grid(row=0, column=2, padx=5)
        
        browse_button_lame = ttk.Button(lame_frame, text="Browse", command=self.browse_lame)
        browse_button_lame.grid(row=0, column=3, padx=5)
        
        # FFmpeg path
        ffmpeg_frame = ttk.Frame(main_frame)
        ffmpeg_frame.grid(row=5, column=0, columnspan=3, sticky='w', padx=0, pady=5)
        
        ttk.Label(ffmpeg_frame, text="FFmpeg Executable Path:").grid(row=0, column=0, sticky='w')
        self.ffmpeg_path_var = tk.StringVar(value=self.settings["ffmpeg_path"])
        self.ffmpeg_path_entry = ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path_var, width=50)
        self.ffmpeg_path_entry.grid(row=0, column=1, padx=5)
        
        self.ffmpeg_status_label = ttk.Label(ffmpeg_frame, text="❓")
        self.ffmpeg_status_label.grid(row=0, column=2, padx=5)
        
        browse_button_ffmpeg = ttk.Button(ffmpeg_frame, text="Browse", command=self.browse_ffmpeg)
        browse_button_ffmpeg.grid(row=0, column=3, padx=5)

        # FFprobe path
        ffprobe_frame = ttk.Frame(main_frame)
        ffprobe_frame.grid(row=6, column=0, columnspan=3, sticky='w', padx=0, pady=5)
        
        ttk.Label(ffprobe_frame, text="FFprobe Executable Path:").grid(row=0, column=0, sticky='w')
        self.ffprobe_path_var = tk.StringVar(value=self.settings["ffprobe_path"])
        self.ffprobe_path_entry = ttk.Entry(ffprobe_frame, textvariable=self.ffprobe_path_var, width=50)
        self.ffprobe_path_entry.grid(row=0, column=1, padx=5)
        
        self.ffprobe_status_label = ttk.Label(ffprobe_frame, text="❓")
        self.ffprobe_status_label.grid(row=0, column=2, padx=5)
        
        browse_button_ffprobe = ttk.Button(ffprobe_frame, text="Browse", command=self.browse_ffprobe)
        browse_button_ffprobe.grid(row=0, column=3, padx=5)
        
        # Quality selection (adjusted row)
        ttk.Label(main_frame, text="MP3 Quality (kbps):").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value=self.settings["quality"])
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, 
                                     values=["128", "160", "192", "256", "320"], 
                                     state="readonly", width=10)
        quality_combo.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Progress frame (adjusted row)
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding="5")
        progress_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5)
        
        # Buttons frame (adjusted row)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=10)
        
        self.convert_button = ttk.Button(button_frame, text="Convert Files", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        # Log frame (adjusted row)
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1) # Ensure log frame expands vertically
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_source(self):
        """Browse for source folder"""
        folder = filedialog.askdirectory(title="Select source folder with FLAC files",
                                         initialdir=self.source_var.get() if self.source_var.get() else os.getcwd())
        if folder:
            self.source_var.set(folder)
    
    def browse_destination(self):
        """Browse for destination folder"""
        folder = filedialog.askdirectory(title="Select destination folder for MP3 files",
                                         initialdir=self.dest_var.get() if self.dest_var.get() else os.getcwd())
        if folder:
            self.dest_var.set(folder)
    
    def browse_lame(self):
        """Browse for LAME executable"""
        initial_dir = os.path.dirname(self.lame_path_var.get()) if self.lame_path_var.get() else os.getcwd()
        file_path = filedialog.askopenfilename(title="Select LAME executable",
                                               filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
                                               initialdir=initial_dir)
        if file_path:
            self.lame_path_var.set(file_path)
            self.test_lame() # Test immediately after selection
        else: # Handle cancellation or no selection
            self.lame_path_var.set("") # Clear the path
            self.lame_status_label.config(text="❌") # Indicate not found

    def browse_ffmpeg(self):
        """Browse for FFmpeg executable"""
        initial_dir = os.path.dirname(self.ffmpeg_path_var.get()) if self.ffmpeg_path_var.get() else os.getcwd()
        file_path = filedialog.askopenfilename(title="Select FFmpeg executable",
                                               filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
                                               initialdir=initial_dir)
        if file_path:
            self.ffmpeg_path_var.set(file_path)
            self.test_ffmpeg() # Test immediately after selection
        else: # Handle cancellation or no selection
            self.ffmpeg_path_var.set("") # Clear the path
            self.ffmpeg_status_label.config(text="❌") # Indicate not found

    def browse_ffprobe(self):
        """Browse for FFprobe executable"""
        initial_dir = os.path.dirname(self.ffprobe_path_var.get()) if self.ffprobe_path_var.get() else os.getcwd()
        file_path = filedialog.askopenfilename(title="Select FFprobe executable",
                                               filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
                                               initialdir=initial_dir)
        if file_path:
            self.ffprobe_path_var.set(file_path)
            self.test_ffprobe() # Test immediately after selection
        else: # Handle cancellation or no selection
            self.ffprobe_path_var.set("") # Clear the path
            self.ffprobe_status_label.config(text="❌") # Indicate not found

    def test_executable(self, path_var, status_label, name, test_arg="--help"):
        """Generic function to test an executable"""
        status_label.config(text="❓") 
        exec_path = path_var.get()
        
        if not exec_path: # Path is empty
            status_label.config(text="❌")
            self.log(f"Error: {name} path is empty.")
            return False

        if not os.path.exists(exec_path):
            status_label.config(text="❌")
            self.log(f"Error: {name} not found at: {exec_path}")
            return False
        
        try:
            result = subprocess.run([exec_path, test_arg], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status_label.config(text="✅") 
                self.log(f"{name} test successful.")
                return True
            else:
                messagebox.showerror("Error", f"{name} test failed. Error: {result.stderr}")
                status_label.config(text="❌")
                self.log(f"Error: {name} test failed. Output: {result.stderr}")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"Error testing {name}: {str(e)}")
            status_label.config(text="❌") 
            self.log(f"Error testing {name}: {str(e)}")
            return False

    def test_lame(self):
        """Test if LAME encoder is working"""
        return self.test_executable(self.lame_path_var, self.lame_status_label, "LAME encoder", "--version") 

    def test_ffmpeg(self):
        """Test if FFmpeg is working"""
        return self.test_executable(self.ffmpeg_path_var, self.ffmpeg_status_label, "FFmpeg", "-version")

    def test_ffprobe(self):
        """Test if FFprobe is working"""
        return self.test_executable(self.ffprobe_path_var, self.ffprobe_status_label, "FFprobe", "-version")
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def get_flac_metadata(self, flac_path):
        """
        Extract metadata from FLAC file using ffprobe.

        If metadata extraction fails, falls back to using the filename as the title and default values for other fields.
        """
        ffprobe_path = self.ffprobe_path_var.get()
        try:
            cmd = [ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", str(flac_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                tags = data.get("format", {}).get("tags", {})
                
                # Normalize tag names (case insensitive)
                normalized_tags = {}
                for key, value in tags.items():
                    normalized_tags[key.lower()] = value
                
                return {
                    "artist": normalized_tags.get("artist", "Unknown Artist"),
                    "title": normalized_tags.get("title", "Unknown Title"),
                    "album": normalized_tags.get("album", "Unknown Album"),
                    "track": normalized_tags.get("track", ""),
                    "year": normalized_tags.get("date", normalized_tags.get("year", ""))
                }
            else:
                self.log(f"ffprobe failed for {flac_path.name}: {result.stderr.strip()}")
        except Exception as e:
            self.log(f"Error reading metadata from {flac_path.name}: {str(e)}")
        
        # Fallback to filename
        filename = Path(flac_path).stem
        return {
            "artist": "Unknown Artist",
            "title": filename,
            "album": "Unknown Album",
            "track": "",
            "year": ""
        }
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        return filename
    
    def format_filename(self, template, metadata):
        """Format filename using template and metadata"""
        try:
            formatted = template.format(**metadata)
            return self.sanitize_filename(formatted)
        except KeyError as e:
            self.log(f"Invalid template variable: {e}. Falling back to default filename format.")
            return self.sanitize_filename(f"{metadata['artist']} - {metadata['title']}")
    
    def convert_file(self, flac_path, output_path):
        """Convert single FLAC file to MP3"""
        lame_path = self.lame_path_var.get()
        ffmpeg_path = self.ffmpeg_path_var.get()
        quality = self.quality_var.get()
        
        try:
            # Create the command pipeline: ffmpeg -> lame
            ffmpeg_cmd = [
                ffmpeg_path, "-y", "-i", str(flac_path), "-f", "wav", "-"
            ]
            
            lame_cmd = [
                lame_path, "-b", quality, "-", str(output_path)
            ]
            
            # Run ffmpeg process
            ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Run lame process with ffmpeg output as input
            lame_process = subprocess.Popen(lame_cmd, stdin=ffmpeg_process.stdout, stderr=subprocess.PIPE)
            
            # Close ffmpeg stdout in parent process
            ffmpeg_process.stdout.close()
            
            # Wait for both processes to complete and capture stderr
            lame_stderr = lame_process.communicate()[1].decode('utf-8', errors='ignore')
            ffmpeg_stderr = ffmpeg_process.communicate()[1].decode('utf-8', errors='ignore')

            if lame_process.returncode == 0 and ffmpeg_process.returncode == 0:
                return True
            else:
                self.log(f"FFmpeg stderr: {ffmpeg_stderr.strip()}")
                self.log(f"LAME stderr: {lame_stderr.strip()}")
                return False
                
        except Exception as e:
            self.log(f"Conversion error for {flac_path.name}: {str(e)}")
            return False
    
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        # Update settings
        self.settings["source_folder"] = self.source_var.get()
        self.settings["destination_folder"] = self.dest_var.get()
        self.settings["filename_template"] = self.template_var.get()
        self.settings["lame_path"] = self.lame_path_var.get()
        self.settings["ffmpeg_path"] = self.ffmpeg_path_var.get()
        self.settings["ffprobe_path"] = self.ffprobe_path_var.get()
        self.settings["quality"] = self.quality_var.get()
        
        # Validate inputs
        if not os.path.exists(self.settings["source_folder"]):
            messagebox.showerror("Error", "Source folder does not exist")
            return
        
        # Explicitly re-test executables before conversion to ensure current paths are valid

        a = self.test_lame()
        b = self.test_ffmpeg() 
        c = self.test_ffprobe()
        if not (self.test_lame() and self.test_ffmpeg() and self.test_ffprobe()):
            messagebox.showerror("Error", "One or more required executables (LAME, FFmpeg, FFprobe) are not properly configured or found. Please check their paths.")
            return

        if not self.settings["destination_folder"]:
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        # Create destination folder if it doesn't exist
        os.makedirs(self.settings["destination_folder"], exist_ok=True)
        
        # Save settings
        self.save_settings()
        
        # Disable convert button
        self.convert_button.config(state='disabled')
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def convert_files(self):
        """Convert all FLAC files in the source folder"""
        source_folder = Path(self.settings["source_folder"])
        dest_folder = Path(self.settings["destination_folder"])
        template = self.settings["filename_template"]
        
        # Find all FLAC files
        flac_files = list(source_folder.glob("*.flac"))
        flac_files.extend(source_folder.glob("*.FLAC"))
        
        if not flac_files:
            self.log("No FLAC files found in source folder")
            self.status_var.set("No FLAC files found")
            self.convert_button.config(state='normal')
            return
        
        total_files = len(flac_files)
        self.log(f"Found {total_files} FLAC files to convert")
        
        converted = 0
        failed = 0
        
        for i, flac_path in enumerate(flac_files):
            progress = (i / total_files) * 100
            self.progress_var.set(progress)
            self.status_var.set(f"Converting {flac_path.name}...")
            
            # Get metadata
            metadata = self.get_flac_metadata(flac_path)
            
            # Format output filename
            output_filename = self.format_filename(template, metadata) + ".mp3"
            output_path = dest_folder / output_filename
            
            self.log(f"Converting: {flac_path.name} -> {output_filename}")
            
            # Convert file
            if self.convert_file(flac_path, output_path):
                converted += 1
                self.log(f"✓ Converted: {output_filename}")
            else:
                failed += 1
                self.log(f"✗ Failed: {flac_path.name}")
        
        # Final progress update
        self.progress_var.set(100)
        self.status_var.set(f"Complete: {converted} converted, {failed} failed")
        self.log(f"\nConversion complete: {converted} files converted, {failed} failed")
        
        # Re-enable convert button
        self.convert_button.config(state='normal')

def main():
    root = tk.Tk()
    app = FlacToMp3Converter(root)
    # Perform initial tests for all executables on startup
    app.test_lame()
    app.test_ffmpeg()
    app.test_ffprobe()
    root.mainloop()

if __name__ == "__main__":
    main()