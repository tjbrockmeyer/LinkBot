

class Thumbnail:
    def __init__(self, data):
        self.height = data['height']
        self.width = data['width']
        self.url = data['url']


class Video:
    def __init__(self, data):
        snippet = data['snippet']
        self.video_id = data['id']['videoId']
        self.url = "http://youtube.com/watch?v=" + self.video_id
        self.title = snippet['title']
        self.description = snippet['description']
        self.channel = snippet['channelTitle']
        self.channel_id = snippet['channelId']
        self.date = snippet['publishedAt']
        self.thumbnails = {k: Thumbnail(v) for k, v in snippet['thumbnails'].items()}

class Image:
    def __init__(self, data):
        img = data['image']
        self.url = data['link']
        self.title = data['title']
        self.context_url = img['contextLink']
        self.height = img['height']
        self.width = img['width']
        self.thumbnail_url = img['thumbnailLink']
        self.thumbnail_height = img['thumbnailHeight']
        self.thumbnail_width = img['thumbnailWidth']