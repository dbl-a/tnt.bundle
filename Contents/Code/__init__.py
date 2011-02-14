# PMS plugin framework

##################################################################################################TNT
VIDEO_PREFIX  = "/video/TNT"
NAME          = L('Title')

TNT_ROOT      = "http://www.tnt.tv/"
SHOW_LIST     = "http://www.tnt.tv/content/services/getCollections.do?id=58127"
AUTH_URL      = "http://www.tnt.tv/processors/services/token.do"

ART           = "art-default.jpg"
THUMB         = "icon-default.jpg"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, 'TNT', THUMB, ART)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  
  MediaContainer.art        = R(ART)
  MediaContainer.title1     = NAME
  DirectoryItem.thumb       = R(THUMB)

####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    content = XML.ElementFromURL(SHOW_LIST)
    for item in content.xpath('//collection[name="Full Episodes"]//subcollection'):
        showId = item.xpath('./@id')[0]
        title = item.xpath('.//name')[0].text
        title = title.split(" -")[0]
        dir.Append(Function(DirectoryItem(VideoPage, title=title), showId=showId))
    return dir 

####################################################################################################
def VideoPage(sender, showId):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
  link = "http://www.tnt.tv/processors/services/getCollectionByContentId.do?site=true&offset=0&sort=&limit=200&id=" + showId
  shows = XML.ElementFromURL(link).xpath('//episode')
  for show in shows:
    videoId = show.xpath('./@id')[0]
    Log(videoId)
    title = show.xpath('./title')[0].text
    Log(title)
    thumb = show.xpath('./thumbnailUrl')[0].text
    summary = show.xpath('./description')[0].text
    #duration = show.xpath('./duration')          ###NEEDS WORK
    #clip = "http://www.tnt.tv/dramavision/index.jsp?oid=" + videoId     ###SAVE THIS IN CASE RTMP BRAKES
    #Log("link: " + clip)   
    #dir.Append(WebVideoItem(clip, title=title, thumb=thumb, summary=summary))
    #Log("epID: " + epID + " | title: " + title + " | thumb: " + thumb + " | Description: " + summary)
    dir.Append(Function(VideoItem(VideoPlayer, title=title, thumb=thumb, summary=summary), videoId=videoId))
  return dir

####################################################################################################
def VideoPlayer(sender, videoId):
    dir = MediaContainer(title2=sender.itemTitle)
    postData = {}
    streamInfo = "http://www.tnt.tv/video_cvp/cvp/videoData/?id=" + videoId
    showLinks = XML.ElementFromURL(streamInfo)
    clip = showLinks.xpath('//video/files/file[@type="hd"]')[0].text   ###ALL LINKS APPEAR TO BE THE SAME, NEED TO PREVENT ERROR IN CASE THERE IS NO "HD" ITEM
    clip = clip.replace("/mp4:", "").replace(".mp4", "")
    player = showLinks.xpath('//akamai/src')[0].text
    player = "rtmp:" + player.split(":")[1]
    postData['authTokenType'] = showLinks.xpath('//akamai/authTokenType')[0].text
    postData['window'] = showLinks.xpath('//akamai/window')[0].text
    postData['aifp'] = showLinks.xpath('//akamai/aifp')[0].text
    postData['path'] = clip
    postData['videoId'] = videoId
    postData['profile'] = "tnt"
    authString = XML.ElementFromURL(AUTH_URL, values=postData).xpath('token')[0].text
    player = player + "?" + authString
    clip = "mp4:" + clip
    #Log(player)
    #Log(clip)
    return Redirect(RTMPVideoItem(player, clip))

