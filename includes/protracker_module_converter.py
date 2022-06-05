
# volume convert component: 127 * 0.7874015748031497 = 100.0
# volume convert component:  64 * 1.5625             = 100.0

class Channel:

    def __init__(self):
        self.event_start_marker = ( 0, None, None, 64 )
        self.instruments = [ [] for a in range(32) ]    # separates instuments on individual tracks

    def feed( self, tick, ins, note, effect_cmd, effect_data ):

        volume = 64
        if effect_cmd == 0xc:                   # "c" protracker effect command
            volume = int( effect_data )

        if ins == 0:                            # instrument 0 means contiunue previous instrument
            ins = self.get_previously_used_instrument()

        if note > -1:
            # note += 48                          # transpose all notes
            self.create_event( tick )
            self.event_start_marker = ( tick, ins, note, volume ) # remember what was just played

    def create_event( self, tick ):
        esm_pos, esm_chann, esm_note, esm_vol = self.event_start_marker
        note_len = tick - esm_pos
        if note_len > 0 and esm_note != None:   # check if we can end our note
            pos = esm_pos * 12
            len = note_len * 12
            vol = int( round( esm_vol * 1.5625 ) )
            self.instruments[ esm_chann ].append( ( pos, esm_note, vol, len ) )

    def end( self, tick ):
        self.create_event( tick )

    def get_previously_used_instrument( self ):
        return self.event_start_marker[ 1 ]

    def get_array_track( self, track_nr ):
        return self.instruments[ track_nr ]

class TempoTrack:

    def __init__( self ):
        self.tempo_track = []

    def set( self, time_pos, bpm, ticks ):
        tempo = int( round( 24 * bpm / float( ticks ) / 3.95 ) ) 
        # tempo = int( round( 48 * bpm / float( ticks ) / 7 ) ) 
        self.tempo_track.append( [ time_pos, tempo ] )

    def get_data( self ):
        return self.tempo_track

    def get_track_length( self ):
        last_arr_el = -1
        time        = 0
        note_len    = 1
        return ( self.tempo_track[ last_arr_el ][ time ] + note_len ) * 12

def process_patterns( module, instruments ):
    # default constants for protracker module
    bpm = 125                                       # BPM = 125
    ticks = 6                                       # TICKS = 6
    patt_len = 64 * module.get_channels_count()	    # pattern rows * channels
    time_pos = 0
    tempo_track = TempoTrack()
    channels = [ Channel() for i in range( module.get_channels_count() ) ]
    sequence = module.get_sequence()

    for pattern_nr in sequence:

        pattern         = module.get_pattern( pattern_nr )
        notes           = pattern.get_notes()
        channels_count  = pattern.get_channels_count() - 1      # ( four channels: 0,1,2,3 )

        flags = []
        for n in notes:
            note, ins, effect_cmd, effect_data, channel_nr = n.get_data()
            if note > -1:
                note += 24             # transpose all notes
            channels[ channel_nr ].feed( time_pos, ins, note, effect_cmd, effect_data )

            if effect_cmd == 0xd:    # "d00"
                flags.append('break')
            elif effect_cmd == 0xf:    # "f07"
                if effect_data <= 32:
                    ticks = max( 1, effect_data )
                elif effect_data > 32:
                    bpm = effect_data
                tempo_track.set( time_pos, bpm, ticks )

            if channel_nr == channels_count:
                time_pos += 1
                if 'break' in flags:
                    break

    for b in range( len( channels ) ):
        channels[ b ].end( time_pos )

    return channels, tempo_track, instruments




