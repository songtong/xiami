# monitor.py
# coding=utf-8

import random
import time
import urllib2

from bs4 import BeautifulSoup


path_format = '/artist/top/id/{0}/page/{1}'

# current (2014-04-12) max artist count is 127079
max_artist_count = 127079

# max page count is 5
page_count = 5

# count per thread
count_per_thread = 43000

# thread count
thread_count = 3

# want songs which were listened more than filter_count times
filter_count = 100000

# cookie = '_xiamitoken=ebb96d63fd19fba00698fdbfb5ae9df3; _unsign_token=c74a46d0dea0c59a847b98dea14eae86'
cookie_format = '_xiamitoken={0}; _unsign_token={1}'
cookie = '_unsign_token=c74a46d0dea0c59a847b98dea14eae85; __gads=ID=d7d2c89f133e4f91:T=1397351242:S=ALNI_MZf3zJDYMOqSTDd8Ugx98IknqpZKA; bdshare_firstime=1397351242943; sec=534a318619e14bd6024c884bb116341729bdb225; _xiamitoken=ebb96d63fd19fba00698fdbfb5ae9df2; pnm_cku822=133fCJmZk4PGRVHHxtNZngkZ3k%2BaC52PmgTKQ%3D%3D%7CfyJ6Zyd9OGIlYHUhYXUpaRg%3D%7CfiB4D15%2BZH9geTp%2FJyN8PDJtLBMbCF4lHw%3D%3D%7CeSRiYjNhIHA3cGE3cGU9e2cgeTt8Pn9oO39sMHRtLXo7YCVpez4X%7CeCVoaEATTRdRHBZADAZIDQgmbS9qdWt0OnUxN347ODhhKgcu%7CeyR8C0obRRVJDB5KDwVZARxbDE4LQgYQWx4MVBAQWwpMeFU%3D%7CeiJmeiV2KHMvangudmM6eXk%2BAA%3D%3D; CNZZDATA921634=cnzz_eid%3D1820570737-1397312547-http%253A%252F%252Falisec.xiami.com%252F%26ntime%3D1397371270%26cnzz_a%3D12%26sin%3Dnone%26ltime%3D1397371270409%26rtime%3D1; CNZZDATA2629111=cnzz_eid%3D1320819292-1397312547-http%253A%252F%252Falisec.xiami.com%252F%26ntime%3D1397371270%26cnzz_a%3D12%26sin%3Dnone%26ltime%3D1397371270790%26rtime%3D1; __utma=251084815.693881941.1397312550.1397350440.1397371271.4; __utmb=251084815.8.10.1397371271; __utmc=251084815; __utmz=251084815.1397371271.4.4.utmcsr=alisec.xiami.com|utmccn=(referral)|utmcmd=referral|utmcct=/checkcodev3.php'

def random_str():
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    ret = str()
    for idx in range(32):  # @UnusedVariable
        ret = ret + chars[random.randint(0, 15)]
    return ret

class Artist:
    def __init__(self):
        self.id = int()
        self.area = str()
        self.name = str()
        self.hot_songs = []
        
class Song:
    def __init__(self):
        self.name = str()
        self.listened = int()

def get_doc(host, path):
#     global cookie
    global cookie_format
    try:
        header = {'Cookie':cookie_format.format(random_str(), random_str()), 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'}
        response = urllib2.urlopen(urllib2.Request('http://{0}{1}'.format(host, path), headers=header))
        doc = response.read().strip()
        return (doc, response.getcode())
    except:
        return (str(), 302)

def parse_doc(doc, artist):  # @ReservedAssignment
    has_more = True;
    names = []
    hots = []
    
    soup = BeautifulSoup(doc)

    name_tds = soup.findAll('td', {'class':'song_name'})
    hot_tds = soup.findAll('td', {'class':'song_hot'})
    
    for name_td in name_tds:
        names.append(name_td.a.attrs['title'])
    
    for hot_td in hot_tds:
        hots.append(int(hot_td.get_text()))
        
    name = str()    
    if soup.title != None:
        name = soup.title.get_text()[0:soup.title.get_text().find('的热门歌曲')]
    else:
        name = "未知歌手"
    artist.name = name
    
    for idx in range(1, len(names)):
        song = Song()
        song.name = names[idx]
        song.listened = hots[idx]
        if song.listened > filter_count:
            artist.hot_songs.append(song)
        else:
            has_more = False

    if len(names) < 20:
        has_more = False
    
    return (has_more, artist.name)

def write_log(artists, idx):
    fp = open('artists_{0}.txt'.format(idx), 'a')
    for (k, v) in artists.items():  # @UnusedVariable
        fp.write("{0}\t{1}\t{2}\r\n".format(k, v.name, len(v.hot_songs)))
        for song in v.hot_songs:
            fp.write("\t{0}\t{1}\r\n".format(song.name, song.listened))
    fp.close()
            
def parse_one_artist(artist_id, artists, interval):
    artist = Artist()
    artist.id = artist_id
    for page_idx in range(1, page_count + 1):
        result = get_doc('www.xiami.com', path_format.format(artist_id, page_idx))
        if result[1] != 200:
            print "########## Interrupt at {0} with status {1}! ##########".format(artist_id, result[1])
            return
        result = parse_doc(result[0], artist)
        if not result[0]:
            break
        else:
            time.sleep(interval)
    if len(artist.hot_songs) > 0:
        artists[artist.id] = artist
    print '[{0}] {1}\thas {2} hot songs'.format(artist.id, result[1], len(artist.hot_songs))

def parse_artists(thread_id, start, end, interval, proxy):
    urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': proxy})))
    artists = dict()
    for idx in range(start, end + 1):
        if idx % 10 == 0:
            write_log(artists, thread_id)
            artists = dict()
        parse_one_artist(idx, artists, interval)
        time.sleep(interval)
    write_log(artists, thread_id)

def test(idx):
    result = get_doc('www.xiami.com', '/artist/top/id/{0}/page/1'.format(idx))
    print result[1]
    print result[0]

interval = 1


def load_proxy():
    proxys = []
    fp = open('proxy', 'r')
    for line in fp.readlines():
        proxys.append(line)
    return proxys

def fetch_artist():
    urllib2.install_opener(urllib2.build_opener(urllib2.ProxyHandler({'http': '103.8.221.253:8080'})))
    fp = open('artists', 'r')
    for line in fp.readlines():
        parts = line.split('\t')
        id = parts[0]
        name = parts[1]
        (doc, status) = get_doc('www.xiami.com', '/artist/{0}'.format(id))
        if status != 200:
            print 'Refused {0}'.format(status)
        print '{0}\t{1}\t{2}'.format(id, name, BeautifulSoup(doc).findAll('td')[7].get_text())

fetch_artist()
# test(10253)

# parse_artists(0, 15108, 17000, interval, '202.98.123.126:8080') #done 5

# parse_artists(0, 23693, 26000, interval, '103.8.221.253:8080') #done 1
# parse_artists(0, 29913, 30000, interval, '115.236.22.226:9000') #done 7

# parse_artists(0, 34096, 38000, interval, '222.88.240.19:9999') #done 10


# parse_artists(1, 55278, 59000, interval, '60.222.224.135:8888') #done 2
# parse_artists(1, 59851, 65000, interval, '122.226.122.201:8080') #done 8

# parse_artists(1, 73856, 80000, interval, '61.174.9.96:8080') #done 11
# parse_artists(1, 80860, 86000, interval, '115.236.22.226:9000') #done 6

# parse_artists(2, 97203, 101000, interval, '119.188.46.42:8080') #done 3

# parse_artists(2, 108488, 112000, interval, '103.8.221.253:8080') #done 4

# parse_artists(2, 124155, 125000, interval, '119.188.46.42:8080') #done 12
# parse_artists(2, 125000, 127079, interval, '103.8.221.253:8080') #done 9
# parse_artists(1, 68695, 73000, interval, '202.98.123.126:8080') #done 13
# parse_artists(2, 118469, 120000, interval, '60.222.224.135:8888') #done14
# parse_artists(0, 42419, 43000, interval, '119.188.46.42:8080') #done 15
# parse_artists(1, 51064, 52000, interval, '116.112.66.102:808') #done 16
# parse_artists(0, 19260, 20000, interval, '222.88.240.19:9999') #done 17

# parse_artists(2, 107550, 107600, interval, '103.8.221.253:8080') #done 18
# parse_artists(2, 107901, 108000, interval, '103.8.221.253:8080') #done 19
# parse_artists(2, 107601, 107700, interval, '116.112.66.102:808') #done 20
# parse_artists(2, 107701, 107800, interval, '222.88.240.19:9999') #done 21
# parse_artists(2, 107847, 107900, interval, '222.88.240.19:9999')  # done 22

# parse_artists(0, 7404, 10000, interval, '218.29.90.30:9999')
