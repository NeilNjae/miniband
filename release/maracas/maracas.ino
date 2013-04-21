int newState;
int states[] = {-1,-1};
const int pins[] = {6, 7};
const int wait = 500;

void setup() {
  for (int i = 0; i < 2; i++) {
    pinMode(pins[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  for (int i = 0; i < 2; i++) {
    newState = digitalRead(pins[i]);
    if (newState != states[i]) {
      Serial.print("maracas,");
      Serial.print(i);
      Serial.println();
      states[i] = newState;
      delay(wait);
    }
  }
}

