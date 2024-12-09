# Ubuntu temel imajını kullanıyoruz
FROM ubuntu:latest

# Çalışma dizinini belirliyoruz ve /telegrambot dizini oluşturulacak
WORKDIR /telegrambot

# Ubuntu paket yöneticisini güncelliyoruz ve Python, pip gibi gerekli araçları yüklüyoruz
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv

# Proje dosyalarını container'a kopyalıyoruz
COPY . /telegrambot

# Sanal ortam oluşturuyoruz
RUN python3 -m venv /telegrambot/venv

# Sanal ortamı etkinleştiriyoruz ve bağımlılıkları yüklüyoruz
RUN /telegrambot/venv/bin/pip install --no-cache-dir -r /telegrambot/requirements.txt

# Uygulamanın ana komutunu çalıştırıyoruz
CMD ["/telegrambot/venv/bin/python", "/telegrambot/main.py"]
