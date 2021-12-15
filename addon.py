import streamlink
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import re
import requests
import urllib
from bs4 import BeautifulSoup

# https://forum.kodi.tv/showthread.php?tid=324570

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
}

addon = xbmcaddon.Addon()

_pid = sys.argv[0]
_handle = int(sys.argv[1])


def add_directory_menu(data, _isPlayable, _isFolder):
  if ('link' in data and data['link'].startswith("//")):
    data['link'] = "https:" + data['link']

  videoItem = xbmcgui.ListItem(data['title'])
  videoItem.setInfo('video', {'title': data['title'], 'mediatype': 'video'})
  videoItem.setProperty('IsPlayable', _isPlayable)
  xbmcplugin.addDirectoryItem(handle=_handle, url='{0}?{1}'.format(_pid, urllib.parse.urlencode(data)), listitem=videoItem, isFolder=_isFolder)
  xbmc.log(" ".join(data), xbmc.LOGINFO)


def list_categories():
  xbmcplugin.setPluginCategory(_handle, 'UK TV')
  xbmcplugin.setContent(_handle, 'videos')

  add_directory_menu({"action": "list_channels_filmon", "title": "FilmON"}, 'false', True)
  add_directory_menu({"action": "list_channels_uktvinspain", "title": "UK TV in Spain"}, 'false', True)

  xbmcplugin.endOfDirectory(_handle)


def list_channels_filmon():
  html = requests.get("https://www.filmon.com/tv/", headers=headers).text
  #xbmc.log(html, xbmc.LOGINFO)

  jjs = re.search(r'var\sgroups\s*=\s*(\[.*\]);', html)
  if jjs:
    jjt = jjs.group(1)
    xbmc.log(jjt, xbmc.LOGINFO)
    jj = json.loads(jjt)
    for o in jj:
      if (o['alias'] == 'uk-live-tv'):
        for c in o['channels']:
          add_directory_menu({"action": "play_video_filmon", "title": c['title'], "link" : "https://www.filmon.com/tv/channel/export?channel_id={0}&autoPlay=1".format(c['id'])}, 'true', False)

  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_TITLE)
  xbmcplugin.endOfDirectory(_handle)


def play_video_filmon(params):
  streams = streamlink.streams(params['link'][0])
  xbmcplugin.setResolvedUrl(_handle, True, listitem=xbmcgui.ListItem(path=streams['best'].to_url()))


def list_channels_uktvinspain():
  xbmcplugin.setPluginCategory(_handle, 'UK TV')
  xbmcplugin.setContent(_handle, 'videos')

  channels_list = [
      {"title": "BBC One", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-one-live-stream-bbc-one-live-streaming-bbc-one-online/"},
      {"title": "BBC Two", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-two-live-stream-bbc-two-live-streaming/"},
      {"title": "BBC Four", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-four-live-stream-bbc-four-live-streaming/"},
      {"title": "BBC News", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/bbc-news-live-stream-bbc-news-live-streaming/"},
      {"title": "Cbeebies", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/bbc-live-streams/cbeebies-live-stream-cbeebies-live-streaming/"},
      {"title": "ITV One", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-one-live-stream-itv-one-live-streaming/"},
      {"title": "ITV Two", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-two-live-stream-itv-two-live-streaming/"},
      {"title": "ITV Three", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-three-live-stream-itv-three-live-streaming/"},
      {"title": "ITV Four", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/itv-live-streams/itv-four-live-stream-itv-four-live-streaming/"},
      {"title": "Channel 4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/channel-four-live-stream/"},
      {"title": "Channel E4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/e4-live-stream/"},
      {"title": "Channel M4", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-four-live-streams/more-4-live-stream/"},
      {"title": "Channel 5", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-five-live-streams/channel-five-live-stream/"},
      {"title": "Channel 5 USA", "link": "https://uktvinspain.com/index.php/live-uk-tv-streams/channel-five-live-streams/channel-five-usa-live-stream/"}
      ]

  for channel in channels_list:
    add_directory_menu({"action": "play_video_uktvinspain", "title": channel['title'], "link" : channel['link']}, 'true', False)

  xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
  xbmcplugin.endOfDirectory(_handle)


def play_video_uktvinspain(params):
  html = requests.get(params['link'][0], headers=headers).content
  #xbmc.log(html, xbmc.LOGINFO)
  soup = BeautifulSoup(html, 'html.parser')

  link = soup.find('iframe')
  link_strip = link.get('src').strip()

  streams = streamlink.streams(link_strip)
  xbmcplugin.setResolvedUrl(_handle, True, listitem=xbmcgui.ListItem(path=streams['best'].to_url()))


xbmc.log(" ".join(sys.argv), xbmc.LOGINFO)


def router(paramstring):
  try:
    xbmc.log("paramstring: {0}".format(paramstring), xbmc.LOGINFO)
    params = urllib.parse.parse_qs(paramstring)
  except Exception as e:
    xbmc.log("type error: " + str(e), xbmc.LOGERROR)
    params = False

  xbmc.log("params: {0}".format(params), xbmc.LOGINFO)

  if params:
    if params['action'][0] == '':
      list_categories()
    elif params['action'][0] == 'list_channels_filmon':
      list_channels_filmon()
    elif params['action'][0] == 'list_channels_uktvinspain':
      list_channels_uktvinspain()
    elif params['action'][0] == 'play_video_filmon':
      play_video_filmon(params)
    elif params['action'][0] == 'play_video_uktvinspain':
      play_video_uktvinspain(params)
    else:
      list_categories()

  else:
    list_categories()

if __name__ == '__main__':
  router(sys.argv[2][1:])
