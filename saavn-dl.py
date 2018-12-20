
from json import JSONDecoder
import requests
from pyDes import *
import base64
from bs4 import BeautifulSoup
import eyed3
import os

json_decoder = JSONDecoder()
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}

def input_query():
    try:
        search_query = input("Enter the song to search : ")
        if len(search_query) <= 1:
            raise IndexError
        return ' '.join(search_query)
    except IndexError:
        print(color.BOLD + color.YELLOW + "Enter at least one search query." + color.END)
        sys.exit()

def get_songs(query):
    url = "https://www.jiosaavn.com/search/"+query
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text,"lxml")
    all_song_divs = soup.find_all('div',{"class":"hide song-json"})
    if all_song_divs == None:
        print("No match found!!")
        exit()
    songs = []
    for i in all_song_divs:
        song_info = json_decoder.decode(i.text)
        songs.append(song_info)
    return songs
query = input("Enter the song to search : ")
songs = get_songs(query)
os.system('clear')


des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0" , pad=None, padmode=PAD_PKCS5)
base_url = 'http://h.saavncdn.com'
def decrypt_url(url):
    enc_url = base64.b64decode(url.strip())
    dec_url = des_cipher.decrypt(enc_url,padmode=PAD_PKCS5).decode('utf-8')
    dec_url = base_url + dec_url[10:] + '.mp3'
    return dec_url

for i in songs:
    i['url'] = decrypt_url(i['url'])

counter = 1

for i in songs:
    print(str(counter) + "." ,end=" ")
    print(i['title'] + " by " + i['singers'] + " of album "+ i["album"] )
    counter = counter + 1
dl  = int(input("\n\nEnter the option: "))
print("Downloading : " +songs[dl-1]['title']  + " by " + songs[dl-1]['singers'] + " of album "+ songs[dl-1]["album"] )

import wget
from urllib.parse import unquote
filename = wget.download(songs[dl-1]['url'], songs[dl-1]['title']+'.mp3')


audiofile = eyed3.load(filename)
if (audiofile.tag == None):
    audiofile.initTag()
audiofile.tag.artist = songs[dl-1]['singers']
audiofile.tag.album = songs[dl-1]['album']
songs[dl-1]['image_url'] = songs[dl-1]['image_url'][:-11]+ "500x500.jpg"
album_art = wget.download(songs[dl-1]['image_url'])
audiofile.tag.images.set(3, open(album_art,'rb').read(), 'image/jpeg')
os.remove(album_art)
audiofile.tag.save()
os.system('clear')
print("Song downloaded:\n\n" +songs[dl-1]['title']  + " by " + songs[dl-1]['singers'] + " of album "+ songs[dl-1]["album"] + "\nSize : " +str(os.path.getsize(filename)/1024/1024)[:4]+ " MB")
