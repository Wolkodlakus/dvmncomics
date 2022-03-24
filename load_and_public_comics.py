import os
from os.path import splitext
from pathlib import Path
import requests
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv
import random
import shutil
import logging


class VKAPIError(Exception):
    def __init__(self, * args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'VKAPIError, {0}'.format(self.message)
        else:
            return 'VKAPIError has been raised'


def get_current_comics_amount():
    """Даёт номер последнего коммента, т.е. их количество"""
    url_comic = f'https://xkcd.com/info.0.json'
    response = requests.get(url_comic)
    response.raise_for_status()
    num_comics = response.json()["num"]
    logging.info(f'На сегодня {num_comics} комиксов на XKCD')
    return num_comics


def download_image_from_web(dir, url_img, name_img, params=''):
    """Загружает картинку/файл с указанного url """
    response = requests.get(url_img, params=params)
    response.raise_for_status()
    with open(Path(dir, name_img), 'wb') as file:
        file.write(response.content)
        logging.info(f'Изображение скачано и записано в файл')


def find_filename_in_url(url_string):
    """Поиск имени файла в url"""
    filepath = urlparse(unquote(url_string)).path
    _, filename = os.path.split(filepath)
    return filename


def give_file_extension(url_string):
    """Возвращает разрешение файла"""
    return splitext(find_filename_in_url(url_string))[-1]


def download_random_comic(dir, comic_number):
    """Скачивает в локальное хранилище случайный комикс xkcd"""
    url_comic = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url_comic)
    response.raise_for_status()
    comic_info = response.json()
    comment = comic_info['alt']
    url_img = comic_info['img']
    response = requests.get(url_img)
    response.raise_for_status()
    with open(Path(dir, find_filename_in_url(url_img)), 'wb') as file:
        file.write(response.content)
        logging.info(f'Комикс {comic_number} скачан и записан в файл')
        return comment


def load_vk_info(vk_token):
    """Возвращает стандартные параметры api VK"""
    url_vk = f'https://api.vk.com/method/'
    params = {
        'access_token': vk_token,
        'v': 5.131,
    }
    return url_vk, params


def load_vk_groups(vk_token):
    """Загрузка списка групп пользователя по его токену"""
    url_vk, params = load_vk_info(vk_token)
    url = f'{url_vk}groups.get'
    response = requests.get(url, params)
    response.raise_for_status()
    check_answer_vk_api(response)
    return response.text


def get_vk_wall_upload_server(vk_token, group_id):
    """Даёт адрес сервера для загрузки в vk"""
    url_vk, params = load_vk_info(vk_token)
    url = f'{url_vk}photos.getWallUploadServer'
    params['group_id'] = group_id
    response = requests.get(url, params)
    response.raise_for_status()
    check_answer_vk_api(response)
    return response.json()['response']


def save_photo_vk_wall(upload_url, dir):
    """Загружает все файлы из директории на сервер вк"""
    photos_server = []
    for dirpath, dirnames, filenames in os.walk(dir):
        filepaths = [os.path.join(dirpath, filename) for filename in filenames]
        for filepath in filepaths:
            with open(filepath, 'rb') as img_file:
                files = {
                    'photo': img_file,
                }
                response = requests.post(upload_url, files=files)
                response.raise_for_status()
                check_answer_vk_api(response)
                photos_server.append(response.json())
    logging.info(f'Файлы из временного хранилища записаны на сервер VK')
    return photos_server


def public_photo_wall(owner_id, message, attachments, friends_only=0, from_group=1, signed=0):
    """Публикует загруженный файл с комментарием"""
    url_vk, params = load_vk_info(vk_token)
    url = f'{url_vk}wall.post'
    params_add = {
        'owner_id': f'-{owner_id}',
        'message': message,
        'attachments': attachments,
        'friends_only': friends_only,
        'from_group': from_group,
        'signed': signed,
    }
    params.update(params_add)
    response = requests.post(url, params=params)
    response.raise_for_status()
    check_answer_vk_api(response)
    logging.info(f'Загруженные файлы опубликованы')


def upload_photo_wall(photos_server, group_id):
    """Загружает фото в буфер группы"""
    url_vk, params = load_vk_info(vk_token)
    url = f'{url_vk}photos.saveWallPhoto'
    upload_photos = []
    for item in photos_server:
        params['hash'] = item['hash']
        params['photo'] = item['photo']
        params['server'] = item['server']
        params['group_id'] = group_id
        response = requests.post(url, params)
        response.raise_for_status()
        check_answer_vk_api(response)
        upload_photos.append(response.json()['response'])
    logging.info(f'Загруженные файлы перенесены в буфер группы')
    return upload_photos


def post_comic_in_group(dir, vk_token, group_id, comment):
    """Постит комикс в группу"""
    vk_wall_info = get_vk_wall_upload_server(vk_token, group_id)
    photos_server = save_photo_vk_wall(vk_wall_info['upload_url'], dir)
    upload_photos = upload_photo_wall(photos_server, group_id)
    attachments = f'photo{upload_photos[0][0]["owner_id"]}_{upload_photos[0][0]["id"]}'
    public_photo_wall(group_id, comment, attachments)


def check_answer_vk_api(response):
    answer = response.json()
    if not answer.get('error'):
        return
    raise VKAPIError(f"Код ошибки {answer['error']['error_code']} "
                     f"Текст ошибки {answer['error']['error_msg']}")


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    group_id = os.getenv('GROUP_ID')
    dir = 'files'
    os.makedirs(dir, exist_ok=True)

    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s"
    )

    try:
        comics_amount = get_current_comics_amount()
        comic_number = random.randint(1, comics_amount)
        comment = download_random_comic(dir, comic_number)
        post_comic_in_group(dir, vk_token, group_id, comment)
    except VKAPIError as vkerror:
        logging.error(f'Ошибка API VK {vkerror.message}')
    finally:
        shutil.rmtree(dir)
