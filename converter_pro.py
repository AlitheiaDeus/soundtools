import os
from concurrent.futures import ProcessPoolExecutor
from pydub import AudioSegment
from pydub.utils import mediainfo  # <--- Added this to read tags
from tqdm import tqdm

# Configuration
SOURCE_EXT = ".flac"
TARGET_EXT = ".mp3"
BITRATE = "320k"

def convert_file(file_info):
    """
    Worker function that converts a single file.
    """
    filepath, output_path = file_info
    
    try:
        # 1. Extract tags separately using mediainfo
        # Pydub doesn't load tags into the AudioSegment object automatically
        info = mediainfo(filepath)
        original_tags = info.get('TAG', {})
        
        # 2. Load the audio data
        audio = AudioSegment.from_file(filepath, format=SOURCE_EXT.replace(".", ""))
        
        # 3. Export with the tags we found
        audio.export(
            output_path, 
            format="mp3", 
            bitrate=BITRATE,
            tags=original_tags # Pass the dictionary of tags here
        )
        return None # Success
    except Exception as e:
        return f"Error processing {filepath}: {e}"

def main():
    files_to_process = []
    current_dir = os.getcwd()
    
    print(f"Scanning {current_dir} for {SOURCE_EXT} files...")
    
    for filename in os.listdir(current_dir):
        if filename.lower().endswith(SOURCE_EXT):
            input_path = os.path.join(current_dir, filename)
            output_path = os.path.splitext(input_path)[0] + TARGET_EXT
            
            if not os.path.exists(output_path):
                files_to_process.append((input_path, output_path))

    total_files = len(files_to_process)
    
    if total_files == 0:
        print("No new files to convert.")
        return

    print(f"Starting parallel conversion for {total_files} files...")

    # Run parallel processing
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(convert_file, files_to_process), 
            total=total_files, 
            unit="song"
        ))

    errors = [r for r in results if r is not None]
    if errors:
        print("\nErrors encountered:")
        for err in errors:
            print(err)
    else:
        print("\nSuccess! All files converted cleanly.")

if __name__ == "__main__":
    main()