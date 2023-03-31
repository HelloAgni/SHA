**A script that asynchronously downloads files and calculates the hash sum of the files.**
***
**Скрипт, скачивающий содержимое репозитория во временную папку.**
- После выполнения всех асинхронных задач скрипт считает sha256
хэши от каждого файла.  
- Результаты выводятся в терминал и записываются в файл info.log  

***How to start***  
```bash
git clone <project>
cd <project>

python -m venv venv
# Windows
. venv/scripts/activate 
# Linux
. venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

python sha_asyncio.py
#info.log
```