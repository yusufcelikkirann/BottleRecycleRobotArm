import cv2
import numpy as np
import serial
import time

# Mavi renk aralığını tanımla (mavinin HSV değerleri)
lower_blue = np.array([90, 50, 50])
upper_blue = np.array([150, 255, 255])

# Kamera aygıtını başlat
cap = cv2.VideoCapture(0)

# Arduino'ya bağlan
ArduinoSerial = serial.Serial('COM12', 9600, timeout=1)
time.sleep(2)  # Arduino'nun başlaması için bekleme süresi

target_locked = False

# Pencereyi oluştur ve boyutunu ayarla
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Frame', 800, 600)  # Genişlik 800, Yükseklik 600

while True:
    # Kameradan bir kare al
    ret, frame = cap.read()
    if not ret:
        break

    # Kareyi HSV renk uzayına dönüştür
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Mavi renk bölgesini belirleme
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Gürültüyü azaltmak için biraz morfolojik işlem uygula
    blue_mask = cv2.erode(blue_mask, None, iterations=2)
    blue_mask = cv2.dilate(blue_mask, None, iterations=2)

    # Konturları bulma
    contours, _ = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Mavi renkli bir cisim algılandıysa işlemleri yap
    if contours:
        # Alanı en büyük olan konturu seç
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Cismin dış sınırlarını yakalama
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Cismin alanını hesapla
        area = cv2.contourArea(largest_contour)

        # Cisim alanı bir eşik değerden büyükse şişe olarak etiketle
        if area > 1000:
            # Cismin etrafına dikdörtgen çizme
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Cismin merkez koordinatlarını hesapla
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Cismin merkez koordinatlarını ekrana yazdırma
            print(f"Şişenin Konumu: ({center_x}, {center_y})")

            frame_center_x = frame.shape[1] // 2

            if abs(center_x - frame_center_x) < 30:
                if not target_locked:
                    target_locked = True
                    print("Hedef kilitlendi")
                    # Hedef kilitlendikten sonra Arduino'ya sinyal gönderme
                    ArduinoSerial.write(b'LOCKED\n')
                else:
                    # Hedef kilitliyse ve merkezde kalmaya devam ediyorsa başka bir şey yapma
                    pass
            else:
                # Hedef kilitlenmediği sürece x ekseninde hareket et
                target_locked = False
                string = 'X{0:d}\n'.format(center_x)
                ArduinoSerial.write(string.encode())

    # Görüntüyü ekranda gösterme
    cv2.imshow('Frame', frame)

    time.sleep(0.1)

    # Çıkış için 'q' tuşuna bas
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamera bağlantısını kapat
cap.release()
cv2.destroyAllWindows()
