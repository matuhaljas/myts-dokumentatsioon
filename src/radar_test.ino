/*
  Projekt Müts – prototüübi test.
  Servo pühib 15°–165° sammuga 2°, igas asendis mõõdetakse HC-SR04-ga kaugus
  ja jadaporti saadetakse rida "nurk,kaugus_cm" (0 = kaja ei tulnud).
*/
#include <Servo.h>

// === PINID (TinkerKit: O3 = D6, O2 = D9, O1 = D10) ===
const int SERVO_PIN = 6;
const int TRIG_PIN  = 9;
const int ECHO_PIN  = 10;

// === KALIBREERIMINE – muuda testimise käigus ===
const int  NURK_MIN   = 15;     // pühkimise algus (kraadi)
const int  NURK_MAX   = 165;    // pühkimise lõpp (kraadi)
const int  SAMM       = 2;      // nurga samm (kraadi)
const int  OOTUS_MS   = 40;     // servo liikumise ja kaja sumbumise aeg
const long TIMEOUT_US = 25000;  // kaja ootamise piir (~4 m)
const int  JAGAJA     = 58;     // µs ühe cm kohta edasi-tagasi (temperatuuriga muutub veidi)

Servo servo;
int nurk = NURK_MIN;
int suund = SAMM;

// mõõdab kauguse sentimeetrites, 0 kui kaja ei tulnud
int moodaKaugus() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);   // 10 µs impulss käivitab mõõtmise
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long kestus = pulseIn(ECHO_PIN, HIGH, TIMEOUT_US);  // 0 kui aeg sai otsa
  return kestus / JAGAJA;
}

void setup() {
  Serial.begin(115200);           // jadaport arvutiga
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  servo.attach(SERVO_PIN);        // servo signaal viigul D6
  servo.write(nurk);
  delay(500);                     // servo jõuab algasendisse
}

void loop() {
  servo.write(nurk);              // keera andur uude asendisse
  delay(OOTUS_MS);                // oota, kuni servo on kohal

  Serial.print(nurk);             // saada "nurk,kaugus_cm"
  Serial.print(',');
  Serial.println(moodaKaugus());

  // piiril pööra suund ümber
  if (nurk + suund > NURK_MAX || nurk + suund < NURK_MIN) suund = -suund;
  nurk += suund;
}
