#!/usr/bin/python3
#-*- coding: utf-8 -*-

from os import SEEK_END
from struct import unpack
from codecs import decode
from codecs import encode

class RawFile:

    def __init__( self ):
        self.fsock    = None
        self.filesize = None

    def load_file( self, path ):
        try:
            self.fsock = open( path, 'rb', 0)
            self.fsock.seek( 0, SEEK_END)
            self.filesize = self.fsock.tell()
            self.fsock.seek( 0, 0 )
        except IOError:
            return False
        return True

    def get_string( self, index, length ):
        self.fsock.seek( index, 0 )
        return decode( self.fsock.read( length ) )

    def get_bytes( self, index, length ):
        self.fsock.seek( index, 0 )
        array = []
        for pos in range( length ):
            array.append( self.get_unsigned_byte( index + pos ) )
        return array

    def get_unsigned_word( self, index ):
        self.fsock.seek( index, 0 )
        return unpack( '<H', self.fsock.read( 2 ) )[ 0 ]

    def get_unsigned_byte( self, index ):
        self.fsock.seek( index, 0 )
        return unpack( '<B', self.fsock.read( 1 ) )[ 0 ]

    def get_signed_byte( self, index ):
        self.fsock.seek( index, 0 )
        return unpack( '<b', self.fsock.read( 1 ) )[ 0 ]

    def get_file_size( self ):
        return self.filesize

class Pattern:

    def __init__( self, notes, channels ):
        self.notes      = notes
        self.channels   = channels

    def get_notes( self ):
        return self.notes

    def get_channels_count( self ):
        return self.channels

class Note:

    def __init__(self, note_pitch, sample_number, effect_cmd, effect_data, channel):
        self.note_pitch     = note_pitch
        self.sample_number  = sample_number
        self.effect_cmd     = effect_cmd
        self.effect_data    = effect_data
        self.channel        = channel

    def get_data( self ):
        return ( self.note_pitch,
                 self.sample_number,
                 self.effect_cmd,
                 self.effect_data,
                 self.channel
               )

class SampleInfo:

    def __init__(self, name, length, finetune, volume, repeat_start, repeat_end):
        self.name           = name
        self.length         = int( length )
        self.finetune       = int( finetune )
        self.volume         = int( volume )
        self.repeat_end     = int( repeat_end )
        self.repeat_start   = int( repeat_start )
        if int( repeat_start ) <= 1:
            self.repeat_start = 0

    def get_name( self ):
        return self.name

    def get_length( self ):
        return self.length

    def get_finetune( self ):
        return self.finetune

    def get_volume( self ):
        return self.volume

    def get_repeat_start( self ):
        return self.repeat_start

    def get_repeat_end( self ):
        return self.repeat_end

class ProTrackerModuleData:

    def __init__( self, title, sequence, id, samples, patterns, channels_count ):
        self.title      = title
        self.sequence   = sequence
        self.id         = id
        self.samples    = samples
        self.patterns   = patterns
        self.channels   = channels_count

    def get_title( self ):
        return self.title

    def get_sequence( self ):
        return self.sequence

    def get_id( self ):
        return self.id

    def get_samples( self ):
        return self.samples

    def get_pattern( self, pattern_nr ):
        return self.patterns[ pattern_nr ]

    def get_patterns( self ):
        return self.patterns

    def get_channels_count( self ):
        return self.channels

    def get_songlength( self ):
        return len( self.sequence )

class ProtrackerModuleLoader:

    def __init__( self ):
        self.sample_count           = None
        self.pattern_notes_count    = None
        self.channels               = None
        self.raw_file               = None

    def load_module( self, path ):
        self.raw_file = RawFile()
        if self.raw_file.load_file( path ):
            self.sample_count           = 31
            self.pattern_notes_count    = 256  # 64 lines * 4 channels ( 1024 bytes )
            return True
        return False

    def get_module_data( self ):
        title       = self.raw_file.get_string( 0, 20 )
        songlength  = self.raw_file.get_unsigned_byte( 950 )
        sequence    = self.raw_file.get_bytes( 952, songlength )
        id          = self.raw_file.get_string( 1080, 4 )
        channels    = self.calc_num_channels( id )
        samples     = self._read_samples_info()
        patterns    = self.get_patterns_data( self.find_max_pattern_number( sequence ) )
        return ProTrackerModuleData( title, sequence, id, samples, patterns, channels )

    def calc_num_channels( self, id ):
        num_channels = {
            "TDZ1": 1,
            "TDZ2": 2,
            "TDZ3": 3,
            "M.K.": 4,
            "M!K!": 4,
            "M&K!": 4,
            "N.T.": 4,
            "FLT4": 4,
            "FLT8": 8,
            "CD81": 8,
            "OKTA": 8,
            "OCTA": 8
            }.get( id, 0 )      # 0 means that format is not recognized
        if id[1:] == "CHN":
            num_channels = int( id[:1] )
        elif id[2:] == "CH":
            num_channels = int( id[:2] )
        self.channels = num_channels
        return num_channels

    def _read_single_sample( self, index ):
        name            = self.raw_file.get_string( index, 22 ).replace('\0', ' ')
        length          = self.raw_file.get_unsigned_word( index + 22 )
        finetune        = self.raw_file.get_signed_byte( index + 24 )
        volume          = self.raw_file.get_unsigned_byte( index + 25 )
        repeat_start    = self.raw_file.get_unsigned_word( index + 26)
        repeat_end      = self.raw_file.get_unsigned_word( index + 28 )
        return SampleInfo( name, length, finetune, volume, repeat_start, repeat_end )

    def _read_samples_info( self  ):
        samples = []
        for i in range( self.sample_count ):
            index = 20 + i * 30
            samples.append( self._read_single_sample( index ) )
        return samples

    def find_max_pattern_number( self, sequence ):
        highest = 0
        for pattern in sequence:
            highest = max( highest, pattern )
        # print("max pattern number :  ", highest )
        return highest

    def get_patterns_data( self, highest_pattern_number ):
        patterns = []
        for i in range( highest_pattern_number + 1 ):
            patterns.append( self.encode_pattern( i ) )
        return patterns

    def encode_pattern( self, nr ):
        notes = []
        pattern_align = 1084 + nr * self.pattern_notes_count * 4
        for i in range( self.pattern_notes_count ):
            note = self.raw_file.get_bytes( pattern_align + i * 4, 4 )
            notes.append( self.encode_note( note, i % self.channels ) )
        return Pattern( notes, self.channels )

    def encode_note( self, note, channel ):
        pitch           = (( note[ 0 ] & 0x0f ) << 8 ) | note[ 1 ] 
        sample_number   = ( note[ 0 ] & 0xf0 ) | ( ( note[ 2 ] & 0xf0 ) >> 4 )
        effect_cmd      = (note[ 2 ] & 0x0f )
        effect_data     = note[ 3 ]
        pitch           = self.change_period_value_into_note_index( pitch )
        return Note( pitch, sample_number, effect_cmd, effect_data, channel )

    def change_period_value_into_note_index( self, pitch ):
        # change ProTracker period value into number 0-35 ( 0,1,2... means C1,Cis1,D... and so on..)
        # change period value into (in future maybe: midi ?) note index
        # -1 means no note
        period_table = [856,808,762,720,678,640,604,570,538,508,480,453,
                        428,404,381,360,339,320,302,285,269,254,240,226,
                        214,202,190,180,170,160,151,143,135,127,120,113]
        if pitch in period_table:
            return period_table.index(pitch)
        return -1

def print_samples_info( samples ):
    for s in samples:
        n  = s.get_name()
        l  = s.get_length()
        f  = s.get_finetune()
        v  = s.get_volume()
        sr = s.get_repeat_start()
        er = s.get_repeat_end()
        print( f"{n:22}  {l:>5}  {f:3}  {v:>2}  {sr:>5}  {er:>5}" )

def print_pattern_data( pattern ):
    notes = pattern.get_notes()
    channels = pattern.get_channels_count() - 1
    for i, d in enumerate( notes ):
        if d.get_channel() == 0:
            print( "%02d" % int(i/4), end=" " )
        note    = "---" if (d.get_note() < 0) else d.get_note()
        ins     = d.get_sample_number()
        cmd     = d.get_effect_cmd()
        data    = d.get_effect_data()
        print( f"{ins:>2}  {note:3}  {cmd:>2}  {data:>2}", end="  |  ")
        if d.get_channel() == channels:
            print()

def count_patterns( patterns ):
    count = 0
    for p in patterns:
        count += 1
    return count

def print_patterns_not_in_sequence( module ):
    not_used = []
    sequence = module.get_sequence()
    for i, p in enumerate( module.get_patterns() ):
        if i not in sequence:
            not_used.append( i )
    print("patterns not used :  ", not_used )

def print_module_info( module ):
    print( "title           :  %s" % module.get_title() )
    print( "songlength      :  %s" % module.get_songlength() )
    print( "patterns used   :  %s" % count_patterns( module.get_patterns() ) )
    print_patterns_not_in_sequence( module )
    print( "id              :  %s" % module.get_id() )
    print( "channels        :  %s" % module.get_channels_count() )
    print( "sequence        :  %s" % module.get_sequence() )
    print_samples_info( module.get_samples() )
    print_pattern_data( module.get_pattern( 1 ) )

if __name__ == "__main__":

    module_loader = ProtrackerModuleLoader()
    # if module_loader.load_module( "../data/Knulla Kuk.mod" ):
    if module_loader.load_module( "../data/Siedler_II.MOD" ):
        print_module_info( module_loader.get_module_data() )
    else:
        print( "error loading file..." )




