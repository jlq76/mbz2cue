import requests
from bs4 import BeautifulSoup
import argparse

DEBUG_LEVEL = 0  # Global debug level

def debug_print(level, message):
    """Prints a debug message if the current global debug level is greater than or equal to the specified level.

    Args:
        level (int): The debug level required for the message to be printed.
        message (str): The debug message to print.
    """
    global DEBUG_LEVEL  # Access the global variable
    if DEBUG_LEVEL >= level:
        print(message)

def extract_album_title(soup):
    """Extracts the album title from the BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the album page.

    Returns:
        str: The extracted album title, or "Unknown Album" if not found.
    """
    title_tag = soup.find('h1')
    if title_tag and title_tag.find('bdi'):
        album_title = title_tag.find('bdi').get_text(strip=True)
        debug_print(2, f"Extracted album title: {album_title}")
        return album_title
    debug_print(1, "Album title not found.")
    return "Unknown Album"

def extract_tracklist(url):
    """Extracts the tracklist from a MusicBrainz release URL.

    Args:
        url (str): The MusicBrainz release URL.

    Returns:
        tuple: A tuple containing the tracklist (list of dictionaries) and the album title (str), or (None, None) if an error occurs.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        debug_print(1, f"Failed to fetch page: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    album_title = extract_album_title(soup)
    tracklist_div = soup.find('div', class_='tracklist-and-credits')

    if not tracklist_div:
        debug_print(1, "Tracklist div not found.")
        return None, album_title

    tracklist = []
    table_rows = tracklist_div.find_all('tr', class_=['odd', 'even'])

    for row in table_rows:
        columns = row.find_all('td')
        if len(columns) >= 5:
            track_number = columns[0].get_text(strip=True)
            title = columns[1].find('bdi').get_text(strip=True) if columns[1].find('bdi') else columns[1].get_text(strip=True)
            artist = columns[2].find('bdi').get_text(strip=True) if columns[2].find('bdi') else columns[2].get_text(strip=True)
            length = columns[4].get_text(strip=True)

            tracklist.append({
                'track_number': track_number,
                'title': title,
                'artist': artist,
                'length': length
            })

    debug_print(2, f"Extracted {len(tracklist)} tracks.")
    return tracklist, album_title

def create_cue_sheet(tracklist, album_title, performer, filename, wav_filename):
    """Creates a CUE sheet file.

    Args:
        tracklist (list): The list of track dictionaries.
        album_title (str): The album title.
        performer (str): The performer name.
        filename (str): The name of the CUE sheet file.
        wav_filename (str): The name of the WAV file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'PERFORMER "{performer}"\n')
        f.write(f'TITLE "{album_title}"\n')
        f.write(f'FILE "{wav_filename}" WAVE\n')

        total_seconds = 0
        for track in tracklist:
            minutes, seconds = map(int, track['length'].split(':'))
            track_start_minutes = total_seconds // 60
            track_start_seconds = total_seconds % 60
            index_time = f"{track_start_minutes:02}:{track_start_seconds:02}:00"

            f.write(f'\nTRACK {int(track["track_number"]):02} AUDIO\n')
            f.write(f'    TITLE "{track["title"]}"\n')
            f.write(f'    PERFORMER "{track["artist"]}"\n')
            f.write(f'    INDEX 01 {index_time}\n')

            total_seconds += minutes * 60 + seconds

    debug_print(1, f"CUE sheet written to {filename}.")

def main():
    """Parses command-line arguments and generates a CUE sheet."""
    global DEBUG_LEVEL  # Use the global keyword to modify it.
    parser = argparse.ArgumentParser(description="Extract tracklist from MusicBrainz and generate a CUE sheet.")
    parser.add_argument("--url", required=True, help="MusicBrainz release URL")
    parser.add_argument("--output_file", help="Output CUE file name")
    parser.add_argument("--wav_file", required=True, help="WAV file name referenced in the CUE sheet")
    parser.add_argument("--debug_level", type=int, default=0, help="Debug level (0-2)")
    args = parser.parse_args()

    DEBUG_LEVEL = args.debug_level  # Set the global debug level

    tracklist, album_title = extract_tracklist(args.url)

    if tracklist:
        output_file = args.output_file if args.output_file else f"{album_title}.cue"
        output_file = output_file.replace("/", "_")  # Sanitize filename

        create_cue_sheet(tracklist, album_title=album_title, performer="Various Artists", filename=output_file, wav_filename=args.wav_file)
        debug_print(1, "CUE sheet created successfully.")

if __name__ == "__main__":
    main()