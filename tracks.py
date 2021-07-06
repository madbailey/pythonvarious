#import libraries
import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    genre_id INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')

#import xml file with relevant data
fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'Library.xml'

#this is what our data looks like

# <key>Track ID</key> <integer>369</integer>
# <key>Name</key> <string>Another One Bites The Dust</string>
# <key>Artist</key> <string>Queen</string>
# <key>Genre</key> <string>Rock</string>


#create a function to find the element tag
def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text #returns text value of key if Found
        if child.tag == 'key' and child.text == key :
            found = True
    return None #if no tag is found, returns None

stuff = ET.parse(fname) #parse the xml file

all = stuff.findall('dict/dict/dict')
print('Dict count:', len(all))
for entry in all:
    if ( lookup(entry, 'Track ID') is None ) : continue #skips loop if no track ID
    #extracts relevant information
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    genre = lookup(entry, 'Genre')
    #print(genre)
    album = lookup(entry, 'Album')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time')
    #if we've reached this point and there's no data, something went wrong
    if name is None or artist is None or album is None or genre is None :
        continue
    #print retrieved values
    print(name, artist, album, genre, count, rating, length)

    #create a SQLite table with our extracted values
    cur.execute('''INSERT OR IGNORE INTO Artist (name)
        VALUES ( ? )''', ( artist, ) )
    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
        VALUES ( ?, ? )''', ( album, artist_id ) )
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name)
        VALUES ( ? )''', ( genre, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count)
        VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( name, album_id, genre_id, length, rating, count ) )
    cur.execute('SELECT len FROM TABLE WHERE len = 0 ', (len, ))
    row = cur.fetchone()
    print(row)
    conn.commit()

print('All Done!')
