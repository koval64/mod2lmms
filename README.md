



#Protracker music module to lmms ( Linux Multi Media Software ) format.

For now it converts notes, their length and initial volume.

## In `final_versions` directory you will find two examples of converted files.

## HOWTO covnert using linux

Put modules files inside `data/` directory and run program with command:

> python3 mod2lmms.py

Program will ask you which MOD file to convert.

For first time it creates file with generic instrument and one channel per one istrument ( max 32 channels ).
Load this file to LMMS end choose what intruments you like.

1) If you happy with result just save it and use it.
2) If you wanna create multitrack version than save it with `mmp` extension in data directory,
and run again with:

> python3 mod2lmms.py

It copies instruments from generic version in which you choosen instruments,
but makes it more polyphonic.

## In generic version there are up to 32 tracks.
## In multitrack version there are up to 128 tracks ( 4 channels * 32 iunstruments ).




