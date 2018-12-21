
from json import JSONDecoder
import requests
from pyDes import *
import base64
from bs4 import BeautifulSoup
import wget
from urllib.parse import unquote
import eyed3
import os
from sys import platform

json_decoder = JSONDecoder()
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}

def clrscr():
    if platform.startswith('win'):                                      
        os.system('cls')

    elif platform.startswith('linux'):                                
        os.system('clear')


clrscr()
print("\nJio-Saavn Mp3 Downloader by Mani Goyal.\n\n")


def input_query(choice):
    
    if choice ==1:
        search_query = input("Enter the song to search : ")
    elif choice ==2:
        search_query = input("Enter the album to search : ")
    while len(search_query) <= 1:
        print("Please don't leave the field blank!!")
        search_query = input("Enter again: ")
    return str(search_query)
      
def get_albums(query):
    url =  "https://www.jiosaavn.com/search/album/"+query
    res = requests.get(url, headers=headers, data =  [         ('bitrate', '320')]  )
    soup = BeautifulSoup(res.text,"lxml")
    h3 = soup.find_all('h3',{'class':'title ellip'})
    lent = len(h3)
    p = soup.find_all('p',{'class':'meta'})
    if lent>10:
        h3 = h3[0:11]
        pme=p[0:21:2]
        p=p[1:21:2]
        lent=10
    else:
        h3 = h3[0:lent]
        p=p[0:lent*2]
        pme=p[0:lent*2:2]
        p=p[1:lent*2:2]
    album_list=[]
    album ={}
    for i in range(0,lent):
        soup1 = BeautifulSoup(str(h3[i]),'lxml')
        soup2 = BeautifulSoup(str(pme[i]),'lxml')
        soup3 = BeautifulSoup(str(p[i]),'lxml')
        album['link']= soup1.a.get('href')
        album['album'] =soup1.a.text
        album['singers'] = soup2.a.text
        album['year'] = soup3.a.text
        album_list.append(album.copy())
    return album_list

def album_select(query):
    albums = get_albums(query)
    while len(albums)== 0 :
        print("No result found!! Try a different keyword.")
        query = input_query(2)
        print("\nSearching.....")
        albums = get_albums(query)
    print("Top 10 results: ")
    counter =1
    for i in albums:
        print("............................")
        print(str(counter) + "." ,end="")
        print(i['album']  )
        print("  " +i['singers'] + "  Year:" + i['year'])
        counter=counter +1
    dl  = int(input("\n\nEnter the option(0 for none): "))
    if dl==0 :
        print("\nBye!!!")
        exit()
    while (dl>counter-1):
        dl=int(input("Please enter in the range[1-" +str(counter-1)+"]: "))
    return albums[dl-1]

def meta_data(filename, song_data):
    audiofile = eyed3.load(filename)
    if (audiofile.tag == None):
        audiofile.initTag()
    audiofile.tag.artist = song_data['singers']
    audiofile.tag.album = song_data['album']
    audiofile.tag.recording_date = song_data['year']
    song_data['image_url'] = song_data['image_url'][:-11]+ "500x500.jpg"
    album_art = wget.download(song_data['image_url'])
    audiofile.tag.images.set(3, open(album_art,'rb').read(), 'image/jpeg')
    os.remove(album_art)
    audiofile.tag.save()




def download_album(album_choice):
    url = album_choice['link']
    res = requests.get(url, headers=headers, data =  [         ('bitrate', '320')]  )
    soup = BeautifulSoup(res.text,"lxml")
    all_song_divs = soup.find_all('div',{"class":"hide song-json"})
    songs = []
    for i in all_song_divs:
        song_info = json_decoder.decode(i.text)
        songs.append(song_info)
           
    for i in songs:
            i['url'] = decrypt_url(i['url'])
    counter = 1
    print( i['album']+ " by "+i['singers'] +"\n\n" )
    for i in songs:
        print(".........................................")
        print(str(counter) + "." ,end="")
        print(i['title'] )
        i['tno'] = counter
        i['duration'] = str(int(i['duration'])//60)+" min " + str(int(i['duration'])%60) + " sec"
        print("   " +i['duration'])

        counter = counter + 1
    dl  = input("\n\nEnter the songs to download (100 for full album / comma seperated values for particular songs/0 for none): ")
    path= album_choice['album']+" by " +album_choice['singers']
    if dl=='0' :
        print("\nBye!!!")
        exit()
    
    elif dl == '100':
        
        if(os.path.isdir("Saavn_Downloader/"+path)==False):
            os.system("mkdir "+"\""+"Saavn_Downloader/"+ path+ "\"")
        downloaded = []
        for i in songs:
            print("Downloading " + i['title'] +" :" )
            filename = wget.download(i['url'],"Saavn_Downloader/"+path+ "/"+ i['title'] + ".mp3")
            meta_data(filename,i)
            downloaded.append(i['title'])
            clrscr()
            print("Downloaded:")
            for j in range(0,len(downloaded)):
                print(str(j+1)+". "+ downloaded[j])
        print("All the " +str(len(downloaded))+" songs from album "+ i['album']+ " downloaded successfully.")
        exit()

    else :
        if(os.path.isdir("Saavn_Downloader/"+path)==False):
            os.system("mkdir "+"\""+"Saavn_Downloader/"+ path+ "\"")
        dl = dl.split(",")
        downloaded = []
        for tno in range(0,len(dl)):
            
            if (int(dl[tno])<counter):
                for j in songs:
                    if(j['tno']==int(dl[tno])):
                        print("Downloading " + j['title'] +" :" )
                        filename= wget.download(j['url'],"Saavn_Downloader/"+path+ "/"+ j['title'] + ".mp3")
                        meta_data(filename,j)
                        downloaded.append((j['tno'],j['title']))
                        clrscr()
                        print("Downloaded:")
                        for k in range(0,len(downloaded)):
                            print(str(downloaded[k][0])+". "+ downloaded[k][1])
        exit()



def get_songs(query):
    url = "https://www.jiosaavn.com/search/"+query
    res = requests.get(url, headers=headers, data =  [         ('bitrate', '320')]  )
    soup = BeautifulSoup(res.text,"lxml")
    all_song_divs = soup.find_all('div',{"class":"hide song-json"})
    songs = []
    for i in all_song_divs:
        song_info = json_decoder.decode(i.text)
        songs.append(song_info)
           
    return songs



clrscr()


des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0" , pad=None, padmode=PAD_PKCS5)
base_url = 'http://h.saavncdn.com'
def decrypt_url(url):
    enc_url = base64.b64decode(url.strip())
    dec_url = des_cipher.decrypt(enc_url,padmode=PAD_PKCS5).decode('utf-8')
    dec_url = base_url + dec_url[10:] + '.mp3'
    return dec_url







def song_download(song_data):   
    print("Downloading : " +song_data['title']  + " by " + song_data['singers'] + " of album "+ song_data["album"] )

    
    filename = wget.download(song_data['url'], "Saavn_Downloader/"+song_data['title']+'.mp3')


    audiofile = eyed3.load(filename)
    if (audiofile.tag == None):
        audiofile.initTag()
    audiofile.tag.artist = song_data['singers']
    audiofile.tag.album = song_data['album']
    audiofile.tag.recording_date = song_data['year']
    song_data['image_url'] = song_data['image_url'][:-11]+ "500x500.jpg"
    album_art = wget.download(song_data['image_url'],"Saavn_Downloader/"+song_data['image_url'][27:])
    audiofile.tag.images.set(3, open(album_art,'rb').read(), 'image/jpeg')
    os.remove(album_art)
    audiofile.tag.save()
    clrscr()
    print("Song downloaded:\n\n" +song_data['title']  + " by " + song_data['singers'] + " of album "+ song_data["album"] + "\nSize : " +str(os.path.getsize(filename)/1024/1024)[:4]+ " MB")

def song_select(query):
    songs = get_songs(query)
    while len(songs)== 0 :
        print("No result found!! Try a different keyword.")
        query = input_query(1)
        print("\nSearching.....")
        songs = get_songs(query)
    for i in songs:
            i['url'] = decrypt_url(i['url'])
    counter = 1
    for i in songs:
        print(".........................................")
        print(str(counter) + "." ,end="")
        print(i['title'] +" ,Album :" + i["album"] )
        print("  " +i['singers'] + "  Year:" + i['year'])
        i['duration'] = str(int(i['duration'])//60)+" min " + str(int(i['duration'])%60) + " sec"
        print("  " +i['duration'])

        counter = counter + 1
    dl  = int(input("\n\nEnter the option(0 for none): "))
    if dl==0 :
        print("\nBye!!!")
        exit()
    while (dl>counter-1):
        dl=int(input("Please enter in the range[1-" +str(counter-1)+"]: "))
    return songs[dl-1]

if (os.path.isdir("Saavn_Downloader")==False):
    os.system("mkdir Saavn_Downloader")

choice = int(input("You want to download song or album (1 for song/2 for album): "))
while (choice != 1) and (choice != 2):
    choice = int(input("Please enter a valid option[1-2]: "))
query = input_query(choice)
print("\nSearching.....")
if choice==1:
    song_choice= song_select(query)
    song_download(song_choice)
elif choice ==2 :
    album_link = album_select(query)
    download_album(album_link)

    
