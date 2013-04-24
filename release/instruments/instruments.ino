const int NUMBER_OF_MARACAS = 2;
const int MARACAS_PINS[] = {6, 7};
const int MARACAS_DELAY = 5000;

const int NUMBER_OF_DRUMS= 4;
const int DRUM_PINS[] = {8, 9, 10, 11};
const int DRUM_DELAY = 2500;

const int GUITAR_THRESHOLD = 20;
const int GUITAR_PIN = A0;
const int GUITAR_DELAY = 5000;

int maracas_states[] = {-1,-1};
int maracas_delays[] = {0, 0};

int drum_delays[] = {0, 0, 0, 0};

int guitar_delay = 0;

void setup() {
  for (int i = 0; i < NUMBER_OF_MARACAS; i++) {
    pinMode(MARACAS_PINS[i], INPUT);
  }
  for (int i = 0; i < NUMBER_OF_DRUMS; i++) {
    pinMode(DRUM_PINS[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  maracas();
  drums();
  guitar();
  update_delays();  
}


void maracas() {
  for (int i = 0; i < NUMBER_OF_MARACAS; i++) {
    int newState = digitalRead(MARACAS_PINS[i]);
    if (newState != maracas_states[i] && maracas_delays[i] < 1) {
      Serial.print("maracas,");
      Serial.print(i);
      Serial.println();
      maracas_states[i] = newState;
      maracas_delays[i] = MARACAS_DELAY;
    }
  }
}

void drums() {
  for (int i = 0; i < NUMBER_OF_DRUMS; i++) {
    if (digitalRead(DRUM_PINS[i]) == HIGH && drum_delays[i] < 1) {
      Serial.print("drum,");
      Serial.print(i);
      Serial.println();
      drum_delays[i] = DRUM_DELAY;
    }
  }
}

void guitar() {
  int pitch = analogRead(GUITAR_PIN);
  if (pitch >= GUITAR_THRESHOLD && guitar_delay < 1) {
    Serial.print("guitar,");
    Serial.print(pitch);
    Serial.println();
    guitar_delay = GUITAR_DELAY;
  }
}

void update_delays() {
  for (int i = 0; i < NUMBER_OF_MARACAS; i++) {
    if (maracas_delays[i] > 0) {
      maracas_delays[i] -= 1;
    }
  }
  for (int i = 0; i < NUMBER_OF_DRUMS; i++) {
    if (drum_delays[i] > 0) {
      drum_delays[i] -= 1;
    }
  }
  if (guitar_delay > 0) {
    guitar_delay -= 1;
  }
}
