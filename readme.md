# MusicBrainz Tracklist to CUE Sheet

This Python script extracts tracklist information from a MusicBrainz release URL and generates a CUE sheet.  The primary purpose of this script is to facilitate splitting a long WAV file into individual tracks based on the tracklist information retrieved from MusicBrainz. The generated CUE sheet can then be used with tools like `cuetools` to perform the actual splitting.

## Functionality

The script performs the following actions:

1. **Retrieves Tracklist:** Fetches the HTML content of a MusicBrainz release page using `requests` and parses it using `BeautifulSoup`. It then extracts the album title and tracklist (track number, title, artist, and length) from the page.

2. **Generates CUE Sheet:** Creates a CUE sheet file containing the extracted track information.  The CUE sheet includes the `PERFORMER`, `TITLE`, `FILE`, `TRACK`, `INDEX`, and other necessary directives for splitting the WAV file. The timing information for each track is calculated based on the track lengths.

3. **Splits WAV File (External Tool):**  While this script *generates* the CUE sheet, it does *not* perform the actual WAV file splitting.  You would typically use a tool like `cuetools` (or similar software) along with the generated CUE sheet to split your long WAV file.

## Pre
```bash 
pip install requests
pip install BeautifulSoup4

## Usage

```bash
python musicbrainz_to_cue.py --url <MUSICBRAINZ_URL> --wav_file <WAV_FILE> [--output_file <OUTPUT_CUE_FILE>] [--debug_level <DEBUG_LEVEL>]