FROM docker.io/python:3.11-slim
RUN apt update; apt install -y libx11-6 libxrandr2 libxrender1 libxext6 libxi6 libgl1 \
  libglu1-mesa libglib2.0-0 libsm6 libxfixes3 libxkbcommon0 libopencv-dev\
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /CGH /CGH/output
WORKDIR /CGH
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ /app

CMD ["python", "/app/main.py"]