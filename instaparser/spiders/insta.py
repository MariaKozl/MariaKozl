import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from instaparser.items import InstaparserItem
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'mash_inps'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1638996210:AYlQAFeqH3OjShX3uOGw1+zLHNHi0ZkxeZLOIXMWxxUZOwIKAKWCX93xx/INXw1mUc9Wj3ycfHgQC5AVU8Bkx/t16UcEoezxps5ZSWWP6SOAaO+DELQRxR/NFEowbTo+xbLrl/CwG9DfwdOGCGq3'
    users = ['samofoto_2018', 'babymarket.pro']
    inst_friendship = 'https://www.instagram.com/api/v1/friendships/'


    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pwd},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(
                    f'/{user}',
                    callback=self.parse_links,
                    cb_kwargs={'username': user}
                )

    def parse_links(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        #Собираем ссылки на подписчиков
        variables_followers = {'count': 12, 'search_surface': 'follow_list_page'}
        url_followers = f'{self.inst_friendship}{user_id}/followers/?{urlencode(variables_followers)}'

        yield response.follow(
            url_followers,
            callback=self.parse_followers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_followers)}
        )
        #Собираем ссылки на подписки
        variables_following = {'count': 12}
        url_following = f'{self.inst_friendship}{user_id}/following/?{urlencode(variables_following)}'

        yield response.follow(
            url_following,
            callback=self.parse_following,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables_following)}
        )

    #Собираем информацию о подсписчиках
    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        if 'next_max_id' in j_data:
            variables['max_id'] = j_data['next_max_id']
            url_followers = f'{self.inst_friendship}{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.parse_followers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_data.get('users')
        for follower in followers:
            item = InstaparserItem(
                user_id = user_id,
                username = username,
                friend_type = 'follower',
                follower_id = follower['pk'],
                follower_name = follower['full_name'],
                follower_login = follower['username'],
                follower_photo_link = follower['profile_pic_url']
            )
            yield item

    #Собираем информацию о подписках
    def parse_following(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        if 'next_max_id' in j_data:
            variables['max_id'] = j_data['next_max_id']
            url_followers = f'{self.inst_friendship}{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(
                url_following,
                callback=self.parse_following,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followings = j_data.get('users')
        for following in followings:
            item = InstaparserItem(
                user_id = user_id,
                username = username,
                friend_type = 'following',
                following_id = following['pk'],
                following_name = following['full_name'],
                following_login = following['username'],
                following_photo_link = following['profile_pic_url']
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
