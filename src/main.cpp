
#include <Arduino.h>

//--------------------------------------------------------------

#define POT_ON_TIME_1 PA0  // Analog input
#define POT_OFF_TIME_1 PA1  // Analog input
#define POT_ON_TIME_2 PA2  // Analog input
#define POT_OFF_TIME_2 PA3  // Analog input

#define POWER_LED PB5 // Digital output
#define SEC_1_ON_LED PB9 // Digital output
#define SEC_1_OFF_LED PB8 // Digital output
#define SEC_2_ON_LED PB7 // Digital output
#define SEC_2_OFF_LED PB6 // Digital output

int16_t OnTime1Value = 100;
int16_t OffTime1Value = 0;
int16_t OnTime2Value = 0;
int16_t OffTime2Value = 0;
//--------------------------------------------------------------
// ------------------- Function prototypes -------------------
void setup();
void sampleAdc();



void loop() {
  sampleAdc();

  delay(1000); 

}

// Sample all ADC channels
void sampleAdc() {
  OnTime1Value = analogRead(POT_ON_TIME_1);
  OffTime1Value = analogRead(POT_OFF_TIME_1);
  OnTime2Value = analogRead(POT_ON_TIME_2);
  OffTime2Value = analogRead(POT_OFF_TIME_2);  
  Serial1.println("Reading potentiometers...");
  Serial1.print(OnTime1Value); Serial1.print(", ");
  Serial1.print(OffTime1Value); Serial1.print(", "); 
  Serial1.print(OnTime2Value); Serial1.print(", ");
  Serial1.println(OffTime2Value);
}
// Setup function
void setup() {
  Serial1.setRx(PA10);
  Serial1.setTx(PA9);
  Serial1.begin(115200);
  while (!Serial1)
  delay(10);
  
Serial.println("\nStarting up...");
  //analogReadResolution(12);
  pinMode(POT_ON_TIME_1, INPUT_ANALOG);
  pinMode(POT_OFF_TIME_1, INPUT_ANALOG);
  pinMode(POT_ON_TIME_2, INPUT_ANALOG);
  pinMode(POT_OFF_TIME_2, INPUT_ANALOG);

  pinMode(POWER_LED, OUTPUT);
  digitalWrite(POWER_LED, LOW);
  pinMode(SEC_1_ON_LED, OUTPUT);
  digitalWrite(SEC_1_ON_LED, LOW);
  pinMode(SEC_1_OFF_LED, OUTPUT);
  digitalWrite(SEC_1_OFF_LED, LOW);
  pinMode(SEC_2_ON_LED, OUTPUT);
  digitalWrite(SEC_2_ON_LED, LOW);
  pinMode(SEC_2_OFF_LED, OUTPUT); 
  digitalWrite(SEC_2_OFF_LED, LOW); 
}