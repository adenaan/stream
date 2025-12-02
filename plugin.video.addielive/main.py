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

# Custom 24/7 loop channel group
CUSTOM_GROUP_NAME = "24/7"
CUSTOM_CHANNELS = [
    {
        "title": "Rick and Morty Live",
        "url": "https://adultswim-vodlive.cdn.turner.com/live/rick-and-morty/stream_7.m3u8",
        "logo": "https://raw.githubusercontent.com/adenaan/stream/refs/heads/main/art/rickmorty.png",
    }
]

def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"

def get_channels(m3u_url):
    # If m3u_url is None, return only custom channels (used for the 24/7 category)
    if m3u_url is None:
        return {CUSTOM_GROUP_NAME: CUSTOM_CHANNELS}

    try:
        with urllib.request.urlopen(m3u_url, timeout=10) as response:
            m3u = response.read().decode("utf-8")
    except Exception as e:
        xbmcgui.Dialog().ok("Error", f"Could not fetch channel list:\n{e}")
        # If loading playlist failed, still show custom channels under their own group
        return {CUSTOM_GROUP_NAME: CUSTOM_CHANNELS}

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
            group_field = group_match.group(1) if group_match else "Other"

            # Split on semicolons, clean, and create entries for each group
            group_list = [g.strip() for g in group_field.split(";") if g.strip()]
        elif line and line.startswith("http"):
            url = line.strip()
            for group in group_list if 'group_list' in locals() else ["Other"]:
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
        elif category == '247':
            # Special category for 24/7 loop channels
            m3u_url = None
        else:
            m3u_url = WORLD_M3U

        groups = get_channels(m3u_url)
        if not groups:
            xbmcgui.Dialog().ok("No Channels", "No channels found in playlist.")
            return
        # Show clean channel groups for the selected category
        for group in sorted(groups.keys()):
            # URL-encode the group name for safe navigation
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
            m3u_url = None
        else:
            m3u_url = WORLD_M3U

        groups = get_channels(m3u_url)
        # URL-decode the group name from the params
        group = urllib.parse.unquote_plus(params['group'])
        channels = groups.get(group, [])
        # If user selected the custom 24/7 group and no channels were found in the fetched playlist,
        # serve the custom channels explicitly.
        if not channels and group == CUSTOM_GROUP_NAME and m3u_url is None:
            channels = CUSTOM_CHANNELS
        list_channels(channels)
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:])