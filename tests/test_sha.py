"""Tests."""
import hashlib
import os
from unittest.mock import MagicMock, patch

import aiohttp
import pytest

from sha_asyncio import async_execute, download_file, sha


def test_sha_with_wrong_path():
    """Тест пути к директории."""
    with pytest.raises(FileNotFoundError):
        sha('wrong_root/')


def test_sha():
    """Тест функции sha() возвращает верный sha256."""
    temp_dir = 'temp_test_dir/'
    os.makedirs(temp_dir, exist_ok=True)
    file1 = os.path.join(temp_dir, 'file1.txt')
    file2 = os.path.join(temp_dir, 'file2.txt')
    content_1 = 'Any file 1'
    content_2 = 'Any file 2'
    with open(file1, 'w') as f:
        f.write(content_1)
    with open(file2, 'w') as f:
        f.write(content_2)

    expected_hash = [
        hashlib.sha256(content.encode('utf-8')).hexdigest()
        for content in [content_1, content_2]
    ]
    hash_sums = sha(temp_dir)

    assert hash_sums == expected_hash
    os.remove(file1)
    os.remove(file2)
    os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_download_file(tmp_path):
    """Тест скачивание файла."""
    url = 'https://example.com/file.txt'
    name = 'file.txt'
    temp_root = str(tmp_path) + '/'
    async with aiohttp.ClientSession() as session:
        await download_file(session, url, name, temp_root)
        assert (tmp_path / name).exists()



@pytest.fixture
def mock_session():
    session = MagicMock()
    return session


@pytest.mark.asyncio
async def test_async_execute(mock_session):
    with patch('tqdm.asyncio.tqdm_asyncio.gather') as mock_gather:
        await async_execute()
        mock_gather.assert_called_once()
