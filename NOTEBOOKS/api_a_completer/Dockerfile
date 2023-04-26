FROM python:3.8-slim

# Installation de Git pour récupérer le code source de YoloV5
RUN apt-get update -qq && \
    apt-get install -y git ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Mise à jour de pip3
RUN pip install --no-cache-dir --upgrade pip -q

# Création du dossier de l'application
RUN mkdir /app
WORKDIR /app

# Récupération du YoloV5
RUN git clone https://github.com/rkuo2000/yolov5
# Installation des dépendances YoloV5
RUN pip install --no-cache-dir -q -r yolov5/requirements.txt

COPY requirements.txt /app/

# Installation des dépendances de l'API
RUN pip install --no-cache-dir -q -r requirements.txt
RUN pip install --no-cache-dir -q gunicorn

COPY app.py /app/
COPY data/ /app/data/
COPY src/ /app/src/

# On ouvre et expose le port 8080
EXPOSE 8080

# Lancement de l'API
# Attention : ne pas lancer an daemon !
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "-w", "2"]
