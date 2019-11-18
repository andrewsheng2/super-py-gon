Welcome to Super Py-gon, a game that is inspired by the popular game Super Hexagon!

The basic premise of the game is that there will be hexagons (with openings) and a
user has to guide an arrow between these openings without hitting the sides of the
hexagon. This is the Normal mode of the game, in which these obstacles will be generated
at a constant time frequency. There are 4 modes total in the game, which are the
aforementioned Normal mode, Custom mode, in which users can upload their own music
file and obstacles will be generate at every beat (or every other beat) of the song,
while the background is simultaneously changing color to match the dominant frequency,
Versus (Local) mode, where two people can compete against each other on the same computer,
and Versus (Online) mode, where two people can compete against each other without
needing to use the same computer.

All python (.py) files should be in the main directory, whereas all text files (.txt),
besides this README.txt file should be in the data folder, and all other media and font
files (.ttf, .png, and .wav) should be in the resources folder.

Before running the game, there are multiple modules that would need to be installed.
These are pygame, pyaudio, and numpy. All three of these modules can be installed using
'pip install' followed by the module name in the command line.

In order to run the game, there are two main ways. To avoid using an IDE like Pyzo or
Sublime, users can run the RUN .bat or .sh files corresponding to their operating system.
If this does not work, however, users should run the Game_client.py and/or Game_server.py
files.

If a user wants to play multiplayer, you first need to set up Game_client.py and
Game_server.py to allow for this. First find the host computer's IP address using something
like  https://www.whatismyip.com/ and input that IP address in lines 46 of the client file
and line 8 of the server file. The server file will be run by the host computer, and all
players, including the host computer if it is playing, should run the client file.

There is one main 'cheat code' that is implemented in the app. If a user presses 'i' on
their keyboard, the player will then turn invincible. Note that if this key is pressed in
multiplayer, both players will turn invincible. Alternatively, in Normal and Custom modes,
a user can press 's' after they lost to 'remove' the obstacle they lost at and continue
playing the game.