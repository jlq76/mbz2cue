import requests
from bs4 import BeautifulSoup
import argparse

DEBUG_LEVEL = 0  # 0: No debug, 1: Errors, 2: Info, 3: Debug

def debug_print(level, message):
    """Prints a debug message """
    global DEBUG_LEVEL  
    if DEBUG_LEVEL >= level:
        print(message)

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
    
    title_tag = soup.find('h1')
    if title_tag and title_tag.find('bdi'):
        album_title = title_tag.find('bdi').get_text(strip=True)
        debug_print(2, f"Extracted album title: {album_title}")
    else:
        debug_print(1, "Album title not found.")
        album_title= "Unknown Album"

    tracklists = []
    # disc_divs = soup.find_all('div', class_='tracklist-and-credits') 
    disc_tables = soup.find_all('table', class_='tbl medium') 

    if not disc_tables:
        debug_print(1, "No tracklist divs found!")
        return None, album_title

    for disc_num, tracklist_div in enumerate(disc_tables, start=1):  
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
                    'length': length,
                    'disc_number': disc_num  
                })
                debug_print(3, f"Extracted track: {track_number} - {title} - {artist} - {length}")

        debug_print(2, f"Extracted {len(tracklist)} tracks for disc {disc_num}.")
        tracklists.append(tracklist) 

    return tracklists, album_title

def create_cue_sheet(tracklist, album_title, performer, filename, wav_filename): 
    """Creates a CUE sheet file.

    Args:
        tracklist (list): The list of track dictionaries.
        album_title (str): The album title.
        performer (str): The performer name.
        filename (str): The name of the CUE sheet file.
        wav_filename (str): The name of the WAV file.
    """
    for disc_tracklist in tracklist:  
        disc_number = disc_tracklist[0]['disc_number'] 
        filename_disc = filename.replace(".cue", f"_disc{disc_number}.cue") 
        wav_filename = f"{wav_filename}" 
        with open(filename_disc, 'w', encoding='utf-8') as f:
            f.write(f'PERFORMER "{performer}"\n')
            f.write(f'TITLE "{album_title} (Disc {disc_number})"\n') 
            f.write(f'FILE "{wav_filename}" WAVE\n')

            total_seconds = 0
            for track in disc_tracklist:
                minutes, seconds = map(int, track['length'].split(':'))
                track_start_minutes = total_seconds // 60
                track_start_seconds = total_seconds % 60
                index_time = f"{track_start_minutes:02}:{track_start_seconds:02}:00"

                f.write(f'\nTRACK {int(track["track_number"]):02} AUDIO\n')
                f.write(f'    TITLE "{track["title"]}"\n')
                f.write(f'    PERFORMER "{track["artist"]}"\n')
                f.write(f'    INDEX 01 {index_time}\n')

                total_seconds += minutes * 60 + seconds

        debug_print(1, f"CUE sheet written to {filename_disc}.")

def main():
    """Parses command-line arguments and generates a CUE sheet."""
    global DEBUG_LEVEL
    parser = argparse.ArgumentParser(description="Extract tracklist from MusicBrainz and generate a CUE sheet.")
    parser.add_argument("--url", required=True, help="MusicBrainz release URL")
    parser.add_argument("--output_file", help="Output CUE file name (e.g., album.cue will create album_disc1.cue, album_disc2.cue, etc.)")
    parser.add_argument("--wav_filename", required=True, help="WAV file name")
    parser.add_argument("--debug_level", type=int, default=0, help="Debug level (0-2)")
    args = parser.parse_args()

    DEBUG_LEVEL = args.debug_level

    tracklists, album_title = extract_tracklist(args.url)

    if tracklists:
        output_file = args.output_file if args.output_file else f"{album_title}.cue"
        output_file = output_file.replace("/", "_")

        create_cue_sheet(tracklists, album_title=album_title, performer="Various Artists", filename=output_file, wav_filename=args.wav_filename)
        debug_print(1, "CUE sheets created successfully.")


if __name__ == "__main__":
    main()