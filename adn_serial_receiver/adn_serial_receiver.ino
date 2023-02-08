String InBytes

void setup() {
  // put your setup code here, to run once:
    Serial.begin(9600)
    pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
    if (Serial.available()>0){
      InBytes = Serial.read();
      if (InBytes == "on"){
        digitalWRite(LED_BUILTIN,HIGH)
        Serial.write("Led on");
      }
      if (InBytes == "off"){
        digitalWrite(LED_BUILTIN,LOW);
        Serial.write("Led off");
      }
      else{
        digitalWrite(LED_BUILTIN,HIGH)
        Serial.write("invalid input")
      }
    }

}
