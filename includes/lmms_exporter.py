
class LmmsExporter:

    def __init__( self ):
        self.dir = 'includes/mmp_skel/'
        dir = self.dir
        self.file_begin      = open( dir + 'mmp_begin.txt','r' ).read()
        self.file_end        = open( dir + 'mmp_end.txt'   ,'r' ).read()
        self.ins_trk_begin   = open( dir + 'ins_track_begin.txt', 'r' ).read()
        self.ins_trk_end     = open( dir + 'ins_track_end.txt', 'r' ).read()
        self.tempo_trk_begin = open( dir + 'tempo_track_begin.txt', 'r' ).read()
        self.tempo_trk_end   = open( dir + 'tempo_track_end.txt','r' ).read()

    def set_instruments( self, instruments ):
        self.instruments = instruments

    def begin_file( self, filename ):
        self.fh = open( filename, 'w' )
        self.fh.write( self.file_begin )

    def begin_instrument_track( self, instrument_index ):
        index = int( instrument_index[:2] ) - 1
        if len( self.instruments ) > index:
            self.fh.write( self.instruments[ index ].get( 'data' ) )
        else:
            # generic instrument
            self.fh.write( self.ins_trk_begin )

    def begin_instrument_pattern( self, name, start_pos ):
        self.fh.write( '        <pattern type="1" name="%s" pos="%s" muted="0" steps="16">\n' % ( name, start_pos ) )

    # add note/event
    def add_note( self, pos, key, vol, len ):
        self.fh.write( '<note pos="%s" pan="0" key="%s" vol="%s" len="%s"/>\n' % ( pos, key, vol, len ) )

    def end_instrument_pattern( self ):
        self.fh.write( '        </pattern>\n' )

    def end_instrument_track( self ):
        self.fh.write( self.ins_trk_end )

    def begin_tempo_track( self, track_length ):
        self.fh.write( self.tempo_trk_begin )
        self.fh.write( '<automationpattern len="%s" prog="0" name="Tempo" pos="0" mute="0" tens="1">\n' % track_length )

    def add_tempo_change( self, time, tempo ):
        self.fh.write( '<time pos="%s" value="%s"/>\n' % ( time, tempo ) )

    def end_tempo_track( self ):
        self.fh.write( self.tempo_trk_end )

    def end_file( self ):
        self.fh.write( self.file_end )
        self.fh.close()


def export_to_lmms_file( filename, tracks, tempo_track, instruments ):
    exporter = LmmsExporter()
    exporter.set_instruments( instruments )
    exporter.begin_file( filename )

    for name, patterns in tracks:
        if len( patterns ) > 0:             # skip empty channels
            exporter.begin_instrument_track( name )
            for nme, start_pos, events in patterns:
                exporter.begin_instrument_pattern( name, start_pos )
                for pos, key, vol, length in events:
                    exporter.add_note( pos, key, vol, length )
                exporter.end_instrument_pattern()
            exporter.end_instrument_track()
        # else:
        #     print("len patterns <= 0 :  ", patterns)
    exporter.begin_tempo_track( tempo_track.get_track_length() )
    for time, tempo in tempo_track.get_data():
        exporter.add_tempo_change( time * 12, tempo )
    exporter.end_tempo_track()
    exporter.end_file()



