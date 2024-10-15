import sys
import click
import vlc
import readchar
import curses
import threading
import time

class AudioPlayer:
    def __init__(self, playlist, stdscr):
        self.playlist = playlist
        self.stdscr = stdscr
        self.player = vlc.MediaPlayer()
        self.current_index = 0
        self.mode = 'current_song'
        self.running = True
        self.show_help = False
        self.play_song(self.current_index)
        threading.Thread(target=self.update_ui, daemon=True).start()

    def play_song(self, index):
        if index < 0 or index >= len(self.playlist):
            return
        self.current_index = index
        self.player.stop()
        media = vlc.Media(self.playlist[self.current_index])
        self.player.set_media(media)
        self.player.play()

    def next_song(self):
        if self.current_index + 1 < len(self.playlist):
            self.play_song(self.current_index + 1)

    def prev_song(self):
        if self.current_index -1 >= 0:
            self.play_song(self.current_index - 1)

    def seek(self, seconds):
        new_time = self.player.get_time() + seconds * 1000
        self.player.set_time(int(new_time))

    def jump_to_song(self, num):
        index = num - 1
        if index >= 0 and index < len(self.playlist):
            self.play_song(index)

    def progress_bar_seek(self, key):
        keys = 'qwertyuiop'
        position = keys.find(key)
        if position != -1:
            fraction = position / (len(keys) - 1)
            duration = self.player.get_length()
            new_time = duration * fraction
            self.player.set_time(int(new_time))

    def play_pause(self):
        self.player.pause()

    def toggle_mode(self):
        if self.mode == 'current_song':
            self.mode = 'playlist'
        else:
            self.mode = 'current_song'

    def display_help(self):
        self.show_help = not self.show_help

    def update_ui(self):
        while self.running:
            self.stdscr.clear()
            if self.show_help:
                self.display_help_screen()
            elif self.mode == 'current_song':
                self.display_current_song()
            else:
                self.display_playlist()
            self.stdscr.refresh()
            time.sleep(0.1)

    def display_current_song(self):
        title = f"Now Playing: {self.playlist[self.current_index]}"
        duration = self.player.get_length() // 1000
        current_time = self.player.get_time() // 1000
        progress = 0
        if duration > 0:
            progress = current_time / duration
        progress_bar = '[' + ('#' * int(progress * 50)).ljust(50) + ']'
        time_info = f"{self.format_time(current_time)} / {self.format_time(duration)}"
        self.stdscr.addstr(1, 2, title)
        self.stdscr.addstr(3, 2, progress_bar)
        self.stdscr.addstr(5, 2, time_info)

    def display_playlist(self):
        self.stdscr.addstr(1, 2, "Playlist:")
        for idx, song in enumerate(self.playlist):
            if idx == self.current_index:
                self.stdscr.addstr(3 + idx, 4, f"> {song}")
            else:
                self.stdscr.addstr(3 + idx, 6, song)

    def display_help_screen(self):
        commands = [
            "j: Next song",
            "k: Previous song",
            "h: Seek backward 10s",
            "l: Seek forward 10s",
            "1-0: Jump to song (1-10)",
            "q-p: Progress bar seek",
            "Space: Play/Pause",
            "Esc: Toggle UI mode",
            "?: Toggle help screen",
            "Ctrl+C: Exit"
        ]
        self.stdscr.addstr(1, 2, "Help:")
        for idx, cmd in enumerate(commands):
            self.stdscr.addstr(3 + idx, 4, cmd)

    def format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def stop(self):
        self.running = False
        self.player.stop()

def main_loop(player):
    while True:
        key = readchar.readchar()
        if key == 'j':
            player.next_song()
        elif key == 'k':
            player.prev_song()
        elif key == 'h':
            player.seek(-10)
        elif key == 'l':
            player.seek(10)
        elif key in '1234567890':
            num = int(key)
            if num == 0:
                num = 10
            player.jump_to_song(num)
        elif key in 'qwertyuiop':
            player.progress_bar_seek(key)
        elif key == ' ':
            player.play_pause()
        elif key == '\x1b':
            player.toggle_mode()
        elif key == '?':
            player.display_help()
        elif key == '\x03':
            player.stop()
            break

@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=False)
@click.option('-f', '--file', 'playlist_file', type=click.File('r'), help='Playlist file')
def main(files, playlist_file):
    playlist = []
    if '-' in files:
        playlist = [line.strip() for line in sys.stdin if line.strip()]
    elif playlist_file:
        playlist = [line.strip() for line in playlist_file if line.strip()]
    elif files:
        playlist = list(files)
    else:
        click.echo('No input files provided')
        sys.exit(1)

    curses.wrapper(run_player, playlist)

def run_player(stdscr, playlist):
    player = AudioPlayer(playlist, stdscr)
    try:
        main_loop(player)
    except KeyboardInterrupt:
        player.stop()

if __name__ == '__main__':
    main()
