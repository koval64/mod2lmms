



# Protracker music module to lmms ( Linux Multi Media Software ) format.

For now it converts notes, their length and initial volume.

# Demo files

In `final_versions` directory you will find two examples of converted files.
Just download them and load to LMMS to listen the results.

## HOWTO convert using linux

Just download or copy your favorite protracker module files to `data/` directory and run program with command:

> python3 mod2lmms.py

Program will ask you which MOD file to convert.

For first time it creates file with generic instrument and one track per one istrument ( max 32 tracks ).
Load this file to LMMS end choose what intruments you like.

1) If you happy with result just save it and use it.
2) If you wanna create multitrack version than save it with exactly the same name that you loaded it and with `mmp` extension.
Then run again:

> python3 mod2lmms.py

and choose the same file as previous. It will detect *.mmp file and copy instruments.

## In generic version there are up to 32 tracks.
## In multitrack version there are up to 128 tracks ( 4 channels * 32 iunstruments ).




