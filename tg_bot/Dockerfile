FROM python:3.10

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /code

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]