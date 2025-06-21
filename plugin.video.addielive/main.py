import sys
import xbmcplugin
import xbmcgui
import urllib.parse
import urllib.request
import re
from collections import defaultdict

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])

SA_M3U = "https://iptv-org.github.io/iptv/countries/za.m3u"
WORLD_M3U = "https://iptv-org.github.io/iptv/index.m3u"

def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"

def get_channels(m3u_url):
    try:
        with urllib.request.urlopen(m3u_url, timeout=10) as response:
            m3u = response.read().decode("utf-8")
    except Exception as e:
        xbmcgui.Dialog().ok("Error", f"Could not fetch channel list:\n{e}")
        return {}

    # Parse all EXTINF and the following line (the stream URL)
    lines = m3u.splitlines()
    groups = defaultdict(list)
    title, logo, group, url = '', '', '', ''
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name_match = re.search(r",(.+)", line)
            title = name_match.group(1).strip() if name_match else "Unknown"
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1) if logo_match else ""
            group_match = re.search(r'group-title="([^"]+)"', line)
            group = group_match.group(1) if group_match else "Other"
        elif line and line.startswith("http"):
            url = line.strip()
            groups[group].append({"title": title, "url": url, "logo": logo})
    return groups

def list_categories():
    xbmcplugin.setPluginCategory(HANDLE, "Categories")
    sa_url = get_url(category="sa")
    world_url = get_url(category="world")
    sa_li = xbmcgui.ListItem("South Africa")
    world_li = xbmcgui.ListItem("World")
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sa_url, listitem=sa_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=world_url, listitem=world_li, isFolder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_channels(channels):
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
    elif 'category' in params:
        m3u_url = SA_M3U if params['category'] == 'sa' else WORLD_M3U
        groups = get_channels(m3u_url)
        if not groups:
            xbmcgui.Dialog().ok("No Channels", "No channels found in playlist.")
            return
        # Show channel groups for the selected category
        for group in sorted(groups.keys()):
            url = get_url(category=params['category'], group=group)
            li = xbmcgui.ListItem(group)
            xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif 'group' in params and 'category' in params:
        m3u_url = SA_M3U if params['category'] == 'sa' else WORLD_M3U
        groups = get_channels(m3u_url)
        channels = groups.get(params['group'], [])
        list_channels(channels)
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])