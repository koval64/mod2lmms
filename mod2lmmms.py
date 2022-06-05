#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
from includes.utils import debug_count_notes_in_patterns_track
from includes.utils import choose_file
from includes.utils import name_generic
from includes.utils import name_multitrack
from includes.utils import read_instruments_file
from includes.utils import get_generic_instruments
from includes.protracker_module_loader import ProtrackerModuleLoader
from includes.protracker_module_loader import print_module_info
from includes.protracker_module_converter import process_patterns
from includes.lmms_exporter import export_to_lmms_file


def separate_by_instrument_and_channel( channels ):     # instruments * channels
    event_tracks = []
    for idx in range( 32 * 4 ):
        ins_nr      = int( idx/4 )
        chan_nr     = idx%4
        event_tracks.append( channels[ chan_nr ].get_array_track( ins_nr ) )
    return event_tracks

def separate_by_instrument_only( channels ):
    array_tracks = [ [] for _ in range( 32 ) ]
    for idx, events in enumerate( separate_by_instrument_and_channel( channels ) ):
        array_tracks[ int( idx/4 ) ].extend( events )
    for track in array_tracks:
        track.sort()
    return array_tracks

def change_event_tracks_into_pattern_classes( generate_tracks_name, event_tracks ):
    tracks = []
    for idx, events in enumerate( event_tracks ):
        name = generate_tracks_name( idx )
        if len( events ) > 0:
            patterns_track = split_events_track_into_patterns( events )
            tracks.append( ( name, patterns_track ) )

            # DEBUG START #
            debug_count_notes_in_patterns_track( name, events, patterns_track )
            # DEBUG END #

    return tracks

def split_events_track_into_patterns( events ):
    patterns_track = []
    prev_pos       = 0
    tmp_pattern    = []
    tmp_start_pos  = 0
    for ev_pos, ev_note, ev_vol, ev_len in events:
        if ( ev_pos - prev_pos ) > 192:
            if len( tmp_pattern ) > 0:
                patterns_track.append( [ 'no names yet', tmp_start_pos, tmp_pattern ] )
            tmp_pattern = []
            tmp_start_pos = int( ev_pos / 192 ) * 192   # align pattern start ( 48 * 4 = 192 )
        prev_pos = ev_pos + ev_len      # calculate end position
        ev_pos = ev_pos - tmp_start_pos
        tmp_pattern.append( ( ev_pos, ev_note, ev_vol, ev_len ) )
    if len( tmp_pattern ) > 0:
        patterns_track.append( [ 'pattern name', tmp_start_pos, tmp_pattern ] )
    return patterns_track

def create_file( filename, instruments, sorting_function, mod_file ):
    loader = ProtrackerModuleLoader()
    if loader.load_module( mod_file ):
        module = loader.get_module_data()
        # print_module_info( module )
        channels, tempo_track, instruments = process_patterns( module, instruments )
        tracks      = sorting_function( channels )     # one instrument one channel
        patterns    = change_event_tracks_into_pattern_classes( name_generic, tracks )
        export_to_lmms_file( filename, patterns, tempo_track, instruments )
    else:
        print( "error loading file..." )

if __name__ == "__main__":
    data_dir = os.getcwd() + "/data/"
    mod_file = choose_file( data_dir, ".mod" )
    print( "mod file choosen :  ", mod_file )

    name = mod_file[:-4] + ".mmp"
    if os.path.exists( name ):
        print(  " !  instruments file exists creating multitrack version" )
        name             = mod_file[:-4] + " - multitrack.mmp"
        instruments      = read_instruments_file( mod_file[:-3] + "mmp" )
        sorting_function = separate_by_instrument_and_channel
    else:
        # if file doesn't exist
        # create such file with default instrument
        print( " !  creating generic version  ! " )
        name             = mod_file[:-4] + ".mmp"
        instruments      = get_generic_instruments()
        sorting_function = separate_by_instrument_only

    create_file( name, instruments, sorting_function, mod_file )
















