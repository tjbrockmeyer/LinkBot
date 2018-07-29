import requests
from GoogleAPI.Classes import *


GOOGLE_API_URL_BASE = 'https://www.googleapis.com/'
YOUTUBE_API_URL_EXT = 'youtube/v3/'
CUSTOM_SEARCH_URL_EXT = 'customsearch/v1'
CUSTOM_SEARCH_ENGINE_ID = '004172756766271708899:qagcvrjb2kc'


class GoogleAPIError(Exception):
    def __init__(self, request, message='API Error'):
        Exception.__init__(self, message)
        self.url = request.url
        self.json = request.json
        self.status_code = request.status_code


class APIRequest:
    def __init__(self, request):
        self.url = request.url
        self.json = request.json()
        self.status_code = request.status_code
        if request.status_code != 200:
            raise GoogleAPIError(self)


class Client:
    def __init__(self, youtube_api_key):
        self.api_key = youtube_api_key
        self.yt_safe_search = 'moderate'
        self.custom_search_safe = 'medium'

    def set_safe_search(self, set_on):
        if set_on:
            self.yt_safe_search = 'moderate'
            self.custom_search_safe = 'medium'
        else:
            self.yt_safe_search = 'none'
            self.custom_search_safe = 'off'

    @staticmethod
    def base_yt_url():
        return GOOGLE_API_URL_BASE + YOUTUBE_API_URL_EXT

    def get_video_search_results(self, query, max_results=5):
        request = requests.get(
            self.base_yt_url() + 'search', params={
            'part': 'snippet',
            'q': str(query),
            'type': 'video',
            'safeSearch': self.yt_safe_search,
            'maxResults': str(max_results),
            'key': self.api_key
        })
        if 'items' not in request.json():
            return []
        try:
            return [Video(v) for v in request.json()['items']]
        except KeyError as e:
            raise GoogleAPIError(request, "Could not find {} in json.".format(e))


    @staticmethod
    def base_google_search_url():
        return GOOGLE_API_URL_BASE + CUSTOM_SEARCH_URL_EXT

    def get_image_search_results(self, query):
        request = requests.get(self.base_google_search_url(), params={
            'q'         : str(query),
            'cx'        : CUSTOM_SEARCH_ENGINE_ID,
            'safe'      : self.custom_search_safe,
            'searchType': 'image',
            'key'       : self.api_key
        })
        if 'items' not in request.json():
            return []
        try:
            return [Image(i) for i in request.json()['items']]
        except KeyError as e:
            raise GoogleAPIError(request, "Could not find {} in json.".format(e))
