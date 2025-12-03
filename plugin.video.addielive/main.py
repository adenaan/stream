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
LOOP_M3U = "https://raw.githubusercontent.com/adenaan/stream/main/files/247.m3u8"  # Update this if needed

def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"

def get_channels(m3u_url):
    try:
        with urllib.request.urlopen(m3u_url, timeout=10) as response:
            m3u = response.read().decode("utf-8")
    except Exception as e:
        xbmcgui.Dialog().ok("Error", f"Could not fetch channel list:\n{e}")
        return {}

    lines = m3u.splitlines()
    groups = defaultdict(list)
    title, logo, group, url = '', '', '', ''
    # Set default group for 24/7 to "24/7"
    group_list = ["24/7"]
    for i, line in enumerate(lines):
        if line.startswith("#EXTINF"):
            name_match = re.search(r",(.+)", line)
            title = name_match.group(1).strip() if name_match else "Unknown"
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1) if logo_match else ""
            group_match = re.search(r'group-title="([^"]+)"', line)
            group_field = group_match.group(1) if group_match else "24/7"

            # You can add smarter grouping logic if your playlist is grouped by something else
            group_list = [g.strip() for g in group_field.split(";") if g.strip()]
        elif line and line.startswith("http"):
            url = line.strip()
            for group in group_list if 'group_list' in locals() else ["24/7"]:
                groups[group].append({"title": title, "url": url, "logo": logo})
    return groups

def list_categories():
    xbmcplugin.setPluginCategory(HANDLE, "Categories")
    sa_url = get_url(category="sa")
    world_url = get_url(category="world")
    loop_url = get_url(category="247")
    sa_li = xbmcgui.ListItem("South Africa")
    world_li = xbmcgui.ListItem("World")
    loop_li = xbmcgui.ListItem("24/7")
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sa_url, listitem=sa_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=world_url, listitem=world_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=loop_url, listitem=loop_li, isFolder=True)
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
    elif 'category' in params and 'group' not in params:
        category = params['category']
        if category == 'sa':
            m3u_url = SA_M3U
        elif category == 'world':
            m3u_url = WORLD_M3U
        elif category == '247':  # For your 24/7 category
            m3u_url = LOOP_M3U
        else:
            m3u_url = WORLD_M3U

        groups = get_channels(m3u_url)
        if not groups:
            xbmcgui.Dialog().ok("No Channels", "No channels found in playlist.")
            return
        for group in sorted(groups.keys()):
            encoded_group = urllib.parse.quote_plus(group)
            url = get_url(category=params['category'], group=encoded_group)
            li = xbmcgui.ListItem(group)
            xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=True)
        xbmcplugin.endOfDirectory(HANDLE)
    elif 'group' in params and 'category' in params:
        category = params['category']
        if category == 'sa':
            m3u_url = SA_M3U
        elif category == 'world':
            m3u_url = WORLD_M3U
        elif category == '247':
            m3u_url = LOOP_M3U
        else:
            m3u_url = WORLD_M3U

        groups = get_channels(m3u_url)
        group = urllib.parse.unquote_plus(params['group'])
        channels = groups.get(group, [])
        list_channels(channels)
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])