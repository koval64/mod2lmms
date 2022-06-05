
import os

def debug_count_notes_in_patterns_track( name, input_events, patterns_track ):
    counter = 0
    for name, start_pos, events in patterns_track:
        for event in events:
            counter += 1
    if len( input_events ) != counter:
        print( "something in events converting went wrong" )
        print( "name :  %s   events :  %s   counter:  %s" % ( name, len( input_events ), counter ) )

def get_generic_instruments():
    raw_ins = open( "includes/mmp_skel/ins_track_begin.txt", 'r' ).read()
    return [ { "name": "default", "data": raw_ins } ]

def read_instruments_file( filename ):
    instruments = []
    record = False
    raw_ins = []
    name_marker = "name=\""
    align = len( name_marker )
    name =""
    try:
        f = open( filename, encoding = 'utf-8' )
        content = f.readlines()
        for line in content:
            if "<track " in line:
                start = line.find( name_marker ) + align
                end = line.find( "\"", start ) 
                name = line[ start : end ].lower()
                record = True
            elif "</instrumenttrack>" in line:
                raw_ins.append( line )
                record = False
                if name != "automation track":
                    instruments.append( { "name": name, "data": "".join( raw_ins ) } )
                raw_ins = []
            if record:
                raw_ins.append( line )
    finally:
        f.close()
    return instruments

def name_generic( index ):
    return "%02d" % int( index )

def name_multitrack( index ):
    # 65+ uppercase, 97+ lowercase
    return "%02d-%c-%02d" % ( int( index / 4 ), ( 65 + index%4), int( index ) )

def choose_file( directory, extension ):
    files = os.listdir( directory )
    filtered = [ x for x in files if x.lower().endswith( extension ) ] # sort out files

    if len( filtered ) > 0:
        for index, filename in enumerate( filtered ):
            print( "%d)  %s" % (index + 1, filename ) )

        print("choose file in range:  from  1  to  %d" % len( filtered ) )
        file_idx = input()
        if file_idx.isnumeric():
            file_idx = int( file_idx ) - 1
            if file_idx in range(0, len( files ) ):
                return directory + filtered[ file_idx ]
            else:
                print( "choose file within range" )
    else:
        print( "no files found in :  " + directory + "   with extension :  " + extension )
    
    return -1

