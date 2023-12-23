import os
import time
import argparse
import subprocess
import signal
import datetime

# Configurables
REFRESH_INTERVAL = 5  # seconds - no less than 5
OUTPUT_DIRECTORY = r'output directory' #output directory
OAUTH_TOKEN = 'oath token' #alt account token
RETRY_INTERVAL = '5'  # retry interval in seconds

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("channel_name", help="Twitch channel name")
parser.add_argument("--quality", default="best", help="Stream quality")
args = parser.parse_args()

def is_stream_live(channel_name):
    try:
        subprocess.check_output(['streamlink', '--http-header', f'Authorization=OAuth {OAUTH_TOKEN}', '--stream-url', f'https://www.twitch.tv/{channel_name}', args.quality])
        return True
    except subprocess.CalledProcessError:
        return False

def get_output_filename(channel_name):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    count = 1
    while True:
        filename = f"({date_str}) {channel_name}_{count:02}.ts"
        filepath = os.path.join(OUTPUT_DIRECTORY, filename)
        if not os.path.exists(filepath):
            return filepath
        count += 1

def record_stream(channel_name):
    output_filepath = get_output_filename(channel_name)
    streamlink_command = [
        'streamlink',
        '--http-header', f'Authorization=OAuth {OAUTH_TOKEN}',
        '--hls-live-restart',
        '--twitch-disable-hosting',
        '--retry-streams', RETRY_INTERVAL,
        f'https://www.twitch.tv/{channel_name}',
        args.quality,
        '-o', output_filepath
    ]
    subprocess.call(streamlink_command)

def main():
    loading_symbols = ['|', '/', '-', '\\']
    loading_index = 0
    print_once = True
    if os.name == 'posix':
        os.system('clear')
    elif os.name in ('nt', 'dos', 'ce'):
        os.system('cls')
    try:
        while True:
            if is_stream_live(args.channel_name):
                print(f"\033[95mStream for {args.channel_name} is live! Starting recording...\033[0m")
                record_stream(args.channel_name)
                print_once = True  # Reset the print_once flag after recording, so next "not available" message will be printed again
            else:
                if print_once:
                    print(f"\033[93mStream for {args.channel_name} not available.\033[0m", end='')
                    print_once = False
                
                loading_symbol = loading_symbols[loading_index % len(loading_symbols)]
                print(f"\r\033[93mStream for {args.channel_name} not available. Checking... {loading_symbol}\033[0m", end='', flush=True)
                
                time.sleep(REFRESH_INTERVAL)
                loading_index += 1
    except KeyboardInterrupt:
        print("\033[0m\nScript terminated by user.")


if __name__ == "__main__":
    main()
