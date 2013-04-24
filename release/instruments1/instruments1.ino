const int NUMBER_OF_MARACAS = 2;
const int MARACAS_PINS[] = {6, 7};
const int MARACAS_DELAY = 5000;

int maracas_states[] = {-1,-1};
int maracas_delays[] = {0, 0};

void setup() {
  for (int i = 0; i < NUMBER_OF_MARACAS; i++) {
    pinMode(MARACAS_PINS[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  maracas();
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

void update_delays() {
  for (int i = 0; i < NUMBER_OF_MARACAS; i++) {
    if (maracas_delays[i] > 0) {
      maracas_delays[i] -= 1;
    }
  }
}
