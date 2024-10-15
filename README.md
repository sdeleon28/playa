# playa

Comfy command line audio player

## Usage

```
echo ~/tmp/song1.wav > playlist.txt
echo ~/tmp/song2.wav >> playlist.txt
python playa.py -f playlist.txt
```

Then when the player is running:

```
j: Next song
k: Previous song
h: Seek backward 10s
l: Seek forward 10s
1-10: Jump to song (1-10)
q-p: Progress bar seek
Space: Play/Pause
Esc: Toggle song / playlist UI modes
?: Toggle help screen
Ctrl+C: Exit
```

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
