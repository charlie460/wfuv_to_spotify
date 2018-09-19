import requests
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util

# fetch yesterday's playlist
yesterday = datetime.now() - timedelta(days=1)
date = yesterday.strftime('%y-%m-%d')
dat = requests.get('http://nowplaying.wfuv.org/pleditor/external/playlist.php?id=2&day=' + date)

if dat.status_code != 200: sys.exit('Failed to download playlist')

songlist = []
not_added = []

dat = dat.content

soup = BeautifulSoup(dat, features='html.parser')

# each track is in a tr with class="music"
songs = soup.find_all('tr', 'music')

for each in songs:
  song = each.find_all('td')
  # td[0] = play time, td[1] = artist, td[3] = title
  artist = song[1].text
  track = song[2].text.replace("FUV's New Dig: ", '')
  
  if 'FUV ' not in track:
    songlist.append(artist + '~' + track)




token = util.prompt_for_user_token('charlie460','playlist-modify-public',client_id='****API CLIENT ID REMOVED****',client_secret='****API CLIENT SECRET REMOVED****',redirect_uri='http://127.0.0.1/callback')

if token:
  tracks_to_add = []
  sp = spotipy.Spotify(auth=token)
  # retrieve current playlist so we can check for duplicates and not add them
  current_playlist = sp.user_playlist_tracks('charlie460', '3KmIkv1Df20YvcDRvdZM7W')
  current_tracks = current_playlist['items']
  current_ids = []
  # spotify API only retrieves 100 items per request...
  while current_playlist['next']:
    current_playlist = sp.next(current_playlist)
    current_tracks.extend(current_playlist['items'])
  for track in current_tracks:
    current_ids.append(track['track']['id'])

  for song in songlist:
    try:
      search_title = song.replace('~', ' ')
      print('Trying ' + search_title + '... ', end='')
      result = sp.search(search_title, type='track', limit=1)
      id = result['tracks']['items'][0]['id']
      if id not in current_ids:
        name = result['tracks']['items'][0]['name']
        print('Done! ' + id)
        tracks_to_add.append(id)
      else:
        print('Duplicate! ' + id)
    except KeyboardInterrupt:
      sys.exit('Keyboard interrupt')
    except:
      print('Failed.')
      not_added.append(song)
  # spotify api only allows 100 tracks per request, split into seperate requests
  # when adding to playlist
  split_list = [tracks_to_add[i:i+100] for i in range(0, len(tracks_to_add), 100)]
  for add in split_list:
    print(sp.user_playlist_add_tracks('charlie460', '3KmIkv1Df20YvcDRvdZM7W', add))
  #print(tracks_to_add)
else:
  print ("Can't get token for", username)
    

print("\n\n Matched & added " + str(len(tracks_to_add)) + "/" + str(len(songlist)) + " tracks. Any unsuccessful matches are listed below.")
if (not_added): print(*not_added, sep="\n")
    

