import sys
import xbmcplugin
import xbmcgui
import urllib.parse

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])

# Sample video links (replace or scrape as needed)
CATEGORIES = {
    "Soccer": [
        {"title": "Soccer Highlights 1", "url": "https://www.sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"},
        {"title": "Soccer Highlights 2", "url": "https://www.sample-videos.com/video123/mp4/720/big_buck_bunny_720p_10mb.mp4"},
    ],
    "Cricket": [
        {"title": "Cricket Match 1", "url": "https://www.sample-videos.com/video123/mp4/480/asdasdas.mp4"},
        {"title": "Cricket Match 2", "url": "https://www.sample-videos.com/video123/mp4/480/big_buck_bunny_480p_5mb.mp4"},
    ],
    "Rugby": [
        {"title": "Rugby Action 1", "url": "https://www.sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"},
        {"title": "Rugby Action 2", "url": "https://www.sample-videos.com/video123/mp4/240/big_buck_bunny_240p_5mb.mp4"},
    ],
}

def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"

def list_categories():
    for category in CATEGORIES:
        url = get_url(category=category)
        li = xbmcgui.ListItem(label=category)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_videos(category):
    videos = CATEGORIES.get(category, [])
    for video in videos:
        li = xbmcgui.ListItem(label=video['title'])
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=video['url'], listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if 'category' in params:
        list_videos(params['category'])
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])