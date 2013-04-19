
const int THRESHOLD = 10;
const int GUITAR_PIN = A0;
const int PINLIMIT = 5000;

int val;
int pinDelay;

void setup() {
  Serial.begin(57600);
}

void loop() {
  val = analogRead(GUITAR_PIN);
  
  if (val >= THRESHOLD && pinDelay < 1) {
    Serial.print("guitar,");
    Serial.println(val);
    pinDelay = PINLIMIT;
  }
    
  if (pinDelay > 0) {
    pinDelay = pinDelay - 1;
  }
}
  
