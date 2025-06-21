import sys
import xbmcplugin
import xbmcgui
import urllib.parse
import urllib.request
import re

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])

def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"

def get_south_africa_channels():
    m3u_url = "https://iptv-org.github.io/iptv/countries/za.m3u"
    try:
        with urllib.request.urlopen(m3u_url, timeout=10) as response:
            m3u = response.read().decode("utf-8")
    except Exception as e:
        xbmcgui.Dialog().ok("Error", f"Could not fetch channel list:\n{e}")
        return []

    # Parse all EXTINF and the following line (the stream URL)
    lines = m3u.splitlines()
    channels = []
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            # Extract channel name after comma
            name_match = re.search(r",(.+)", line)
            name = name_match.group(1).strip() if name_match else "Unknown"
            # Extract tvg-logo (if present)
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1) if logo_match else ""
            # The next line should be the stream URL
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and url.startswith("http"):
                    channels.append({"title": name, "url": url, "logo": logo})
    return channels

def list_channels():
    channels = get_south_africa_channels()
    if not channels:
        xbmcgui.Dialog().ok("No Channels", "No channels found in playlist.")
    for channel in channels:
        li = xbmcgui.ListItem(label=channel['title'])
        if channel.get('logo'):
            li.setArt({'icon': channel['logo'], 'thumb': channel['logo']})
        li.setProperty('IsPlayable', 'true')
        url = get_url(play=channel['url'])
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if 'play' in params:
        li = xbmcgui.ListItem(path=params['play'])
        xbmcplugin.setResolvedUrl(HANDLE, True, li)
    else:
        list_channels()

if __name__ == '__main__':
    router(sys.argv[2][1:])