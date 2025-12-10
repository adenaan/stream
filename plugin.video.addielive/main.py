import sys
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib.parse
import urllib.request
import re
from collections import defaultdict

BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])

# Base playlists
SA_M3U = "https://iptv-org.github.io/iptv/countries/za.m3u"
WORLD_M3U = "https://iptv-org.github.io/iptv/index.m3u"

# 24/7 main (your original one – keep using what works)
LOOP_M3U = "https://hostingfree.co.za/streams/247.m3u8"

# Sports playlist
SPORTS_M3U = "https://hostingfree.co.za/streams/Sport.m3u8"

# 24/7 / Movies playlists
MOVIES_SERIES_247_M3U = "https://hostingfree.co.za/streams/24-7_MOVIES_SERIES.m3u8"
EXTRA_247_M3U = "https://hostingfree.co.za/streams/24-7A.m3u8"
MOVIESCORD_M3U = "https://hostingfree.co.za/streams/MOVIEScord.m3u8"

# New playlists
COUNTRIES_M3U = "https://hostingfree.co.za/streams/country_channels_all.m3u8"
KIDS_M3U = "https://hostingfree.co.za/streams/kids_zone.m3u8"
MOVIE_NETWORKS_M3U = "https://hostingfree.co.za/streams/movie_networks.m3u8"
SERIES_M3U = "https://hostingfree.co.za/streams/series.m3u8"
RADIO_M3U = "https://hostingfree.co.za/streams/radio_stations.m3u8"


def get_url(**kwargs):
    return f"{BASE_URL}?{urllib.parse.urlencode(kwargs)}"


def get_channels(m3u_url, default_group="Other"):
    try:
        # IMPORTANT: use a browser-like User-Agent to avoid 403
        req = urllib.request.Request(
            m3u_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            m3u = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        xbmcgui.Dialog().ok("Error", f"Could not fetch channel list:\n{e}")
        return {}

    lines = m3u.splitlines()
    groups = defaultdict(list)
    title, logo, url = '', '', ''

    # default group if no group-title= in the playlist
    group_list = [default_group]

    for line in lines:
        if line.startswith("#EXTINF"):
            name_match = re.search(r",(.+)", line)
            title = name_match.group(1).strip() if name_match else "Unknown"

            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1) if logo_match else ""

            group_match = re.search(r'group-title="([^"]+)"', line)
            group_field = group_match.group(1) if group_match else default_group

            group_list = [g.strip() for g in group_field.split(";") if g.strip()]

        elif line and line.startswith("http"):
            url = line.strip()
            for group in group_list:
                groups[group].append({"title": title, "url": url, "logo": logo})

    return groups


def list_categories():
    xbmcplugin.setPluginCategory(HANDLE, "Categories")

    # Category URLs
    sa_url = get_url(category="sa")
    world_url = get_url(category="world")
    loop_url = get_url(category="247")
    sports_url = get_url(category="sports")
    movies_series_url = get_url(category="247_movies_series")
    extra_247_url = get_url(category="247a")
    moviescord_url = get_url(category="moviescord")

    countries_url = get_url(category="countries")
    kids_url = get_url(category="kids")
    movie_networks_url = get_url(category="movie_networks")
    series_url = get_url(category="series")
    radio_url = get_url(category="radio")

    # Make the home page prettier with color & bold + emojis
    sa_li = xbmcgui.ListItem("[COLOR lightblue][B]🇿🇦 South Africa[/B][/COLOR]")
    world_li = xbmcgui.ListItem("[COLOR lightblue][B]🌍 World[/B][/COLOR]")
    loop_li = xbmcgui.ListItem("[COLOR gold][B]⏱ 24/7 Main[/B][/COLOR]")
    movies_series_li = xbmcgui.ListItem("[COLOR gold]🎬 24/7 Movies & Series[/COLOR]")
    extra_247_li = xbmcgui.ListItem("[COLOR gold]📺 24/7 A Mix[/COLOR]")
    moviescord_li = xbmcgui.ListItem("[COLOR orange]🎥 Movies[/COLOR]")
    sports_li = xbmcgui.ListItem("[COLOR lawngreen][B]🏆 Sports[/B][/COLOR]")

    countries_li = xbmcgui.ListItem("[COLOR deepskyblue][B]🌐 Countries[/B][/COLOR]")
    kids_li = xbmcgui.ListItem("[COLOR fuchsia][B]🧒 Kids Zone[/B][/COLOR]")
    movie_networks_li = xbmcgui.ListItem("[COLOR orange][B]🎞 Movie Networks[/B][/COLOR]")
    series_li = xbmcgui.ListItem("[COLOR cyan][B]📺 Series[/B][/COLOR]")
    radio_li = xbmcgui.ListItem("[COLOR yellow][B]📻 Radio Stations[/B][/COLOR]")

    # Add main categories
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sa_url, listitem=sa_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=world_url, listitem=world_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=loop_url, listitem=loop_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=movies_series_url, listitem=movies_series_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=extra_247_url, listitem=extra_247_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=moviescord_url, listitem=moviescord_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sports_url, listitem=sports_li, isFolder=True)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=countries_url, listitem=countries_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=kids_url, listitem=kids_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=movie_networks_url, listitem=movie_networks_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=series_url, listitem=series_li, isFolder=True)
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=radio_url, listitem=radio_li, isFolder=True)

    # Clear cache button at bottom
    clear_url = get_url(action="clear_cache")
    clear_li = xbmcgui.ListItem("[B][COLOR gold]🧹 Clear Addon Cache[/COLOR][/B]")
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=clear_url, listitem=clear_li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE)


def list_channels(channels):
    xbmcplugin.setContent(HANDLE, "videos")
    for channel in channels:
        li = xbmcgui.ListItem(label=channel['title'])
        if channel.get('logo'):
            li.setArt({'icon': channel['logo'], 'thumb': channel['logo']})
        li.setProperty('IsPlayable', 'true')
        url = get_url(play=channel['url'])
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE)


def clear_cache():
    """
    Clear this addon's data/cache folder and show a popup.
    """
    addon = xbmcaddon.Addon()
    profile_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))

    try:
        if os.path.exists(profile_path):
            # Walk through profile folder and delete files/directories
            for root, dirs, files in os.walk(profile_path, topdown=False):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except Exception:
                        pass

        xbmcgui.Dialog().ok("Addie Streams", "Addon cache has been cleared.")
    except Exception as e:
        xbmcgui.Dialog().ok("Addie Streams", f"Error clearing cache:\n{e}")


def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))

    if 'play' in params:
        li = xbmcgui.ListItem(path=params['play'])
        xbmcplugin.setResolvedUrl(HANDLE, True, li)

    elif 'action' in params:
        if params['action'] == "clear_cache":
            clear_cache()
        # After clearing (or failing), show main menu again
        list_categories()

    elif 'category' in params and 'group' not in params:
        category = params['category']

        if category == 'sa':
            m3u_url = SA_M3U
            default_group = "South Africa"
        elif category == 'world':
            m3u_url = WORLD_M3U
            default_group = "World"
        elif category == '247':
            m3u_url = LOOP_M3U
            default_group = "24/7"
        elif category == 'sports':
            m3u_url = SPORTS_M3U
            default_group = "Sports"
        elif category == '247_movies_series':
            m3u_url = MOVIES_SERIES_247_M3U
            default_group = "24/7 Movies & Series"
        elif category == '247a':
            m3u_url = EXTRA_247_M3U
            default_group = "24/7 A Mix"
        elif category == 'moviescord':
            m3u_url = MOVIESCORD_M3U
            default_group = "Movies"
        elif category == 'countries':
            m3u_url = COUNTRIES_M3U
            default_group = "Countries"
        elif category == 'kids':
            m3u_url = KIDS_M3U
            default_group = "Kids Zone"
        elif category == 'movie_networks':
            m3u_url = MOVIE_NETWORKS_M3U
            default_group = "Movie Networks"
        elif category == 'series':
            m3u_url = SERIES_M3U
            default_group = "Series"
        elif category == 'radio':
            m3u_url = RADIO_M3U
            default_group = "Radio Stations"
        else:
            m3u_url = WORLD_M3U
            default_group = "Other"

        groups = get_channels(m3u_url, default_group=default_group)
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
            default_group = "South Africa"
        elif category == 'world':
            m3u_url = WORLD_M3U
            default_group = "World"
        elif category == '247':
            m3u_url = LOOP_M3U
            default_group = "24/7"
        elif category == 'sports':
            m3u_url = SPORTS_M3U
            default_group = "Sports"
        elif category == '247_movies_series':
            m3u_url = MOVIES_SERIES_247_M3U
            default_group = "24/7 Movies & Series"
        elif category == '247a':
            m3u_url = EXTRA_247_M3U
            default_group = "24/7 A Mix"
        elif category == 'moviescord':
            m3u_url = MOVIESCORD_M3U
            default_group = "Movies"
        elif category == 'countries':
            m3u_url = COUNTRIES_M3U
            default_group = "Countries"
        elif category == 'kids':
            m3u_url = KIDS_M3U
            default_group = "Kids Zone"
        elif category == 'movie_networks':
            m3u_url = MOVIE_NETWORKS_M3U
            default_group = "Movie Networks"
        elif category == 'series':
            m3u_url = SERIES_M3U
            default_group = "Series"
        elif category == 'radio':
            m3u_url = RADIO_M3U
            default_group = "Radio Stations"
        else:
            m3u_url = WORLD_M3U
            default_group = "Other"

        groups = get_channels(m3u_url, default_group=default_group)
        group = urllib.parse.unquote_plus(params['group'])
        channels = groups.get(group, [])
        list_channels(channels)

    else:
        list_categories()


if __name__ == '__main__':
    router(sys.argv[2][1:])
