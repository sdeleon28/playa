import sys
import click
import vlc
import readchar

class AudioPlayer:
    def __init__(self, playlist):
        self.playlist = playlist
        self.player = vlc.MediaPlayer()
        self.current_index = 0
        self.play_song(self.current_index)

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

    player = AudioPlayer(playlist)

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
        elif key == '\x03':
            break

if __name__ == '__main__':
    main()
