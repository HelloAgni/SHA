"""
Скрипт с асинхронными задачами.

Скачивающий содержимое HEAD репозитория
https://gitea.radium.group/radium/project-configuration
во временную папку temp.
"""
import asyncio
import hashlib
import logging
import pathlib
import shutil
import sys
import time

import aiofiles
import aiohttp
from tqdm.asyncio import tqdm_asyncio

MAIN_URL = 'https://gitea.radium.group/api/v1/' \
           'repos/radium/project-configuration/contents'
TEMP_ROOT = ''.join((str(pathlib.Path(__file__).parent), '/temp/'))

file_handler = logging.FileHandler(filename='info.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO,
    handlers=handlers,
)


async def download_file(session, url, name, temp_root=TEMP_ROOT):
    """
    Загрузка файла в папку temp.

    Args:
        session: ClientSession
        url: str
        name: str
        temp_root: str
    """
    async with aiofiles.open(f'{temp_root}{name}', 'wb') as new_file:
        async with session.get(url) as dl:
            async for file_data in dl.content.iter_any():
                await new_file.write(file_data)


async def task_from_req(file_data, session, url=MAIN_URL):
    """
    Получение url и имя файла для загрузки.

    Args:
        file_data: dict
        session: ClientSession
        url: str
    """
    if file_data.get('type') == 'file':
        await download_file(
            session, file_data.get('download_url'), file_data.get('name'),
        )
    if file_data.get('type') == 'dir':
        dir_name = file_data.get('name')
        async with session.get(f'{url}/{dir_name}') as response:
            to_json = await response.json()
            for dir_file in to_json:
                if dir_file.get('type') == 'file':
                    await download_file(
                        session,
                        dir_file.get('download_url'),
                        dir_file.get('name'),
                    )


async def async_execute():
    """Запуск цикла событий."""
    async with aiohttp.ClientSession() as session:
        res = await session.get(MAIN_URL)
        tasks = [
            task_from_req(file_data, session) for file_data in await res.json()
        ]
        await tqdm_asyncio.gather(*tasks, desc='Downloading...')


def sha(temp_root=TEMP_ROOT):
    """Открытие, чтение файлов, получение хэша.

    Args:
        temp_root: str

    Returns:
        return: list

    """
    list_results = []
    dir_files_name = [
        # str(files).split('/')[-1]
        files.name
        for files in pathlib.Path(temp_root).iterdir()
        # for files in pathlib.Path(temp_root).glob('*')
        if files.is_file()
    ]
    try:
        for files in dir_files_name:
            with open(
                f'{temp_root}{files}',
            ) as any_file:
                file_str = any_file.read()
                hash_sum = hashlib.sha256(file_str.encode('utf-8')).hexdigest()
                list_results.append(hash_sum)
                logging.info(f'{files} - {hash_sum}')
    except NameError as error:
        logging.error(f'Проблема с файлом - {error}')
    return list_results


if __name__ == '__main__':
    start = time.perf_counter()
    pathlib.Path(TEMP_ROOT).mkdir(parents=True, exist_ok=True)

    if sys.platform == 'win32':  # Checking OS, if Windows use asyncio Fix
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    asyncio.run(async_execute())
    sha()

    shutil.rmtree(TEMP_ROOT, ignore_errors=True)
    end = time.perf_counter()
    logging.info(f'Execution time: {round(end-start, 7)} second(s).\n')
