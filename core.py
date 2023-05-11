import vk_api
from config import *
from vk_api.exceptions import ApiError
from operator import itemgetter


class VkTools():

    def __init__(self, acces_token):
        self.ext_api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):

        try:
            info = self.ext_api.method('users.get',
                                       {'user_id': user_id,
                                        'fields': 'city,bdate,sex,relation,home_town'
                                        }
                                       )
            # user_info = {'name': info['first_name'] + ' ' + info['last_name'],
            #              'id': info['id'],
            #              'bdate': info['bdate'] if 'bdate' in info else None,
            #              'home_town': info['home_town'],
            #              'sex': info['sex'],
            #              'city': info['city']['id']
            #              }
            # return user_info
            return info
        except ApiError:
            return





    def user_serch(self, city_id, age_from, age_to, sex, relation, offset=None):
        try:
            profiles = self.ext_api.method('users.search',
                                           {'city_id': city_id,
                                            'age_from': age_from,
                                            'age_to': age_to,
                                            'sex': sex,
                                            'status': relation,
                                            'count': 10,
                                            'offset': offset

                                            })

        except ApiError:
            return
        profiles = profiles['items']

        result = []
        for profile in profiles:
            if profile['is_closed'] == False:
                result.append({'name': profile['first_name'] + ' ' + profile['last_name'],
                           'id': profile['id']
                           })

        return result

    def photos_get(self, user_id):
        photos = self.ext_api.method('photos.get',
                                     {'album_id': 'profile',
                                      'owner_id': user_id,
                                      'extended': 1
                                      }
                                     )
        try:
            photos = photos['items']
        except KeyError:
            return

        result = []
        for num, photo in enumerate(photos):
            result.append({'owner_id': photo['owner_id'],
                           'id': photo['id'],
                           'likes_comments': photo['likes'].get('count') + photo['comments'].get('count'),
                           })
        result = sorted(result, key=itemgetter('likes_comments'), reverse=True)
        result = result[0:3]
        return result


tools = VkTools(acces_token)


