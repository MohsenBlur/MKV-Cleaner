# MKV Cleaner

MKV Cleaner is an easy-to-use GUI for tidying Matroska (`.mkv`) files. You can quickly remove unwanted audio or subtitle tracks, choose which track should be default or forced and even process many files at once.

## Dependencies

- [Python 3.10 or later](https://www.python.org/downloads/)
- [PySide6](https://pypi.org/project/PySide6/)
- [MKVToolNix](https://mkvtoolnix.download/) (`mkvmerge` and `mkvextract` must be in your `PATH`) *(optional if using FFmpeg)*
- [FFmpeg](https://ffmpeg.org/) (`ffmpeg` and `ffprobe` must be in your `PATH` if selected)

After installing Python, open a command prompt and run `pip install pyside6` to install the GUI framework.

## Usage

1. Install the dependencies above.

2. On Windows, simply double-click `mkv_cleaner.py` to launch the program. If you prefer the command line, run:
=======
2. Start the application with:

   ```bash
   python mkv_cleaner.py
   ```
3. Click **Open Files** to select one or more MKV files.
4. For each group of files with the same track layout you can:
   - uncheck tracks you wish to remove
   - set a default audio or subtitle track
   - toggle the forced subtitle flag
   - preview subtitle text
   - wipe all subtitles if desired
5. Use **Process Group** or **Process All** to create cleaned files in the output directory (by default `cleaned/`).

Paths to the command line tools, the output directory and the preferred backend (MKVToolNix or FFmpeg) can be configured via the Preferences dialog (⚙️ icon).

## Testing

Run the unit tests with:

```bash
pytest
```

