# MKV Cleaner

MKV Cleaner is a simple GUI for tidying Matroska (`.mkv`) files. It lets you remove unwanted audio or subtitle tracks, choose which track should be default, toggle forced subtitles and batch process many files at once.

## Dependencies

- Python 3.10 or later
- [PySide6](https://pypi.org/project/PySide6/)
- [MKVToolNix](https://mkvtoolnix.download/) (`mkvmerge` and `mkvextract` must be in your `PATH`)

Install the Python dependency with `pip install pyside6` or using `poetry install` if you use Poetry.

## Usage

1. Install the dependencies above.
2. Start the application with:

   ```bash
   python mkv_cleaner.py
   ```
   or, with Poetry:
   ```bash
   poetry run mkv-cleaner
   ```
3. Click **Open Files** to select one or more MKV files.
4. For each group of files with the same track layout you can:
   - uncheck tracks you wish to remove
   - set a default audio or subtitle track
   - toggle the forced subtitle flag
   - preview subtitle text
   - wipe all subtitles if desired
5. Use **Process Group** or **Process All** to create cleaned files in the output directory (by default `cleaned/`).

Paths to `mkvmerge`/`mkvextract`, the output directory and other options can be configured via the Preferences dialog (⚙️ icon).

## Testing

Run the unit tests with:

```bash
pytest
```

