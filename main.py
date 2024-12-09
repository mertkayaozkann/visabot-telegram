import requests
import time
import json
from datetime import datetime

API_URL = "https://api.schengenvisaappointments.com/api/visa-list/?format=json"  # API adresi
BOT_TOKEN = "******"  # Telegram bot tokeninizi buraya yazın
CHAT_ID = "*****"  # Telegram chat ID'nizi buraya yazın
LAST_CHECKED_FILE = "last_checked_appointments.json"  # Daha önce bildirilen randevuların saklanacağı dosya

def get_appointments():
    """API'den randevu bilgilerini alır."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Hata durumunda istisna fırlatır
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API'den veri alınırken hata oluştu: {e}")
        return []

def filter_appointments(data):
    """Sadece Türkiye'den açılan tüm ülkelerdeki randevuları filtreler."""
    return [
        record for record in data
        if record.get('source_country') == 'Turkiye'
    ]

def load_last_checked_appointments():
    """Daha önce bildirilen randevuları yükler."""
    try:
        with open(LAST_CHECKED_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_last_checked_appointments(appointments):
    """Daha önce bildirilen randevuları kaydeder."""
    with open(LAST_CHECKED_FILE, "w") as file:
        json.dump(appointments, file, indent=4)

def send_telegram_message(message):
    """Telegram'a mesaj gönderir."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Hata durumunda istisna fırlatır
        print("Mesaj gönderildi:", message)
    except requests.exceptions.RequestException as e:
        print(f"Telegram mesajı gönderilirken hata oluştu: {e}")

def main():
    """Ana fonksiyon: Randevuları kontrol eder ve uygun olanları bildirir."""
    last_checked_appointments = load_last_checked_appointments()  # Daha önce bildirilen randevuları yükle

    while True:
        print("API'den veriler alınıyor...")
        all_appointments = get_appointments()

        if not all_appointments:
            print("API'den alınan veri boş.")
        else:
            print(f"API'den alınan toplam kayıt sayısı: {len(all_appointments)}")

            # Sadece Türkiye'den açılan tüm ülkelerdeki randevuları filtrele
            filtered_appointments = filter_appointments(all_appointments)

            if filtered_appointments:
                for record in filtered_appointments:
                    appointment_date = record.get('appointment_date')

                    if appointment_date:  # Tarih varsa
                        # Randevu daha önce bildirilmiş mi?
                        record_id = f"{record['source_country']}_{record['mission_country']}_{appointment_date}"
                        if record_id not in last_checked_appointments:
                            message = (
                                f"Randevu bulundu!\n"
                                f"Ülke: {record['source_country']} -> {record['mission_country']}\n"
                                f"Kategori: {record['visa_category']}\n"
                                f"Alt Kategori: {record['visa_subcategory']}\n"
                                f"Merkez: {record['center_name']}\n"
                                f"Tarih: {appointment_date}\n"
                                f"Rezervasyon Linki: {record['book_now_link']}\n"
                            )
                            send_telegram_message(message)
                            last_checked_appointments[record_id] = datetime.now().isoformat()  # Kaydı ekle

            else:
                print("Türkiye'den açılan herhangi bir randevu bulunamadı.")

            # Kaydedilen randevuları dosyaya kaydet
            save_last_checked_appointments(last_checked_appointments)

        # Bir sonraki kontrol için 60 saniye bekle
        time.sleep(60)

if __name__ == "__main__":
    main()
