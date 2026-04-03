void setup() {
  Serial.begin(9600);
  pinMode(8, OUTPUT);
  digitalWrite(8, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      digitalWrite(8, HIGH);
      delay(1500);
      digitalWrite(8, LOW);
    }
  }
}