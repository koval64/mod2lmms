ProTracker Module defaults:

Default values are 6 ticks/division, and
125 beats/minute (4 divisions = 1 beat).

1 minute = 125 beats
1 beat = 4 divisions
1 division = 6 ticks

6 ticks = 1 division
4 divisions = 1 beat
125 beats = 1 minute


BPM - Beats per minute. When used in mods, this usually refers to how many
      groups of four rows are played per minute at default tempo (i.e. ticks
      per row) settings. This default tempo is 6 in MOD and S3M. Setting the
      tempo to 3 means that as many groups of eight rows are played per
      minute as set by the BPM set command.

How to calculate this ?

F - set tempo
Fxy means "set tempo to x*16+y"

Let z = x*16+y
if z == 0: z = 1
z <= 32 means "set tick/divisions to z"
      1 - fastest
     32 - slowest

z > 32 means "set beats/minute to z"
     33 - slowest
    255 - fastest

                   24 * beats/minute
divisions/minute = -----------------
                    ticks/division

Example 1:

# Default tempo
24 * 125 / 6 = 500

Example 2:

24 * 125 / 7 = 428.57142857142856

Converting calculations to midi:

tempo = 60 000 000 / bpm
480000 = 60 000 000 / 125

tick_time = 24 * bpm / ticks
428.57142857142856 = 24 * 125 / 7.0

# to figure out where this parameter came from
ppq = 96

