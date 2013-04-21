
const int NUMBER_OF_DRUMS = 4;
const int DELAY = 500;

const int PINS[4] = { 8, 9, 10, 11 };
int pinDelays[4] = { 0, 0, 0, 0 };

void setup() {
  for (int i = 0; i < NUMBER_OF_DRUMS; i++) {
    pinMode(PINS[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  for (int i = 0; i < NUMBER_OF_DRUMS; i++) {
    if (digitalRead(PINS[i]) == HIGH && pinDelays[i] < 1) {
      Serial.print("drum,");
      Serial.println(i);
      pinDelays[i] = DELAY;
    }
    if (pinDelays[i] > 0) {
      pinDelays[i] -= 1;
    }
  }
}

