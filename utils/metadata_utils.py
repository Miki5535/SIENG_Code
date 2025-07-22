import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4

def add_metadata(file_path, metadata, output_path):
    if file_path.lower().endswith('.mp3'):
        audio = EasyID3(file_path)
        for key, value in metadata.items():
            audio[key] = value
        audio.save(output_path)
    elif file_path.lower().endswith('.mp4'):
        video = MP4(file_path)
        for key, value in metadata.items():
            video[key] = value
        video.save(output_path)
    else:
        raise ValueError("Unsupported file format for metadata addition.")
