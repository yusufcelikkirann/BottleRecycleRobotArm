#include <Servo.h>

Servo x, y, z, t, p;
int width = 640, height = 480;  // video çözünürlüğü
int xpos = 60, ypos = 40, zpos = 140, tpos = 90, ppos = 20; // Servo başlangıç pozisyonları

void setup() {
  Serial.begin(9600);
  p.attach(11);
  delay(2000);
  x.attach(9);
  y.attach(10);
  z.attach(3);
  t.attach(4);
  
  x.write(xpos);
  y.write(ypos);
  z.write(zpos);
  t.write(tpos);
  p.write(ppos);
}

const int angle = 2; // derece artışı veya azalışı

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    if (input.startsWith("X")) {
      int x_mid = input.substring(1).toInt();  // x koordinatını al
      int x_center = width / 2;
      
      // Koordinatları kontrol et ve servo pozisyonlarını ayarla
      if (x_mid < x_center - 30)
        xpos += angle; // x servo hareketini ters yönde yap
      else if (x_mid > x_center + 30)
        xpos -= angle; // x servo hareketini ters yönde yap

      // Servo sınırlarını kontrol et
      xpos = constrain(xpos, 0, 180);

      // Servo pozisyonlarını güncelle
      x.write(xpos);
    } else if (input == "LOCKED") {
      // Su şişesi merkezde kilitlendiğinde işlemler
      delay(2000); // 2 saniye bekle

      // İkinci aşama, yeni açılara git
      p.write(100);
      delay(1000);
      xpos = 60;
      
      delay(1000);
      y.write(40);
      delay(1000);
      z.write(180);
      delay(1000);
      t.write(0);
      
      delay(2000); // 2 saniye bekle

      // Üçüncü aşama, p'yi 5 dereceye getir ve 2 saniye bekle
      p.write(5);
      delay(2000);

      // Diğer motorları başlangıç pozisyonlarına döndür (p hariç)
      xpos = 60;
    
      y.write(ypos);
      z.write(zpos);
      t.write(tpos);
      
      delay(2000); // 2 saniye bekle

      // Sonsuz döngüye gir, işlemi durdur
      while (true);
    }
  }
}
