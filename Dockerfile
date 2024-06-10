# python
FROM python:3.10.11

# 디렉토리
WORKDIR /app

# pip install
COPY requirements.txt /app/
RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev ffmpeg \
    && apt-get install -y gcc python3-dev musl-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn  # Add this line to install gunicorn


# 애플리케이션 코드 복사
COPY . .

# 포트
EXPOSE 8000

# 서버 실행
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--workers", "1", "--worker-class", "gevent", "--timeout", "120", "--preload", "WhateverSong.wsgi:application"]
