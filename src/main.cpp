#include <Arduino.h>

// --- Hardware Pins ---
#define POT_ON_1      PA0 
#define POT_OFF_1     PA1 
#define POT_ON_2      PA2 
#define POT_OFF_2     PA3 

#define POWER_LED     PB5 
#define SEC_1_ON_LED  PB9 
#define SEC_1_OFF_LED PB8 
#define SEC_2_ON_LED  PB7 
#define SEC_2_OFF_LED PB6 

// --- Constants & Settings ---
const float alpha = 0.1;           // Filter smoothing (0.0 to 1.0)
unsigned long sendInterval = 1000;  // Default: 1 message per second (1Hz)

// --- Global Variables ---
float f_On1, f_Off1, f_On2, f_Off2; // Filtered floats
uint8_t ledStatusByte = 0;          // LED bitmask
unsigned long lastSerialTime = 0;   // Timer for data sending
unsigned long lastBlinkTime = 0;    // Timer for 2Hz blink
bool powerLedState = false;         // Toggle state for blink

// --- Prototypes ---
void updateFilter();
void handleSerialCommands();
void updateLEDs();

void setup() {
  // Serial1 Setup (PA9=TX, PA10=RX)
  Serial1.setRx(PA10);
  Serial1.setTx(PA9);
  Serial1.begin(115200);

  // ADC Setup: Using 12-bit internally for filter precision
  analogReadResolution(12);

  // Pin Modes
  pinMode(POWER_LED, OUTPUT);
  pinMode(SEC_1_ON_LED, OUTPUT);
  pinMode(SEC_1_OFF_LED, OUTPUT);
  pinMode(SEC_2_ON_LED, OUTPUT);
  pinMode(SEC_2_OFF_LED, OUTPUT);

  // Initialize Filter Seeds
  f_On1 = analogRead(POT_ON_1);
  f_Off1 = analogRead(POT_OFF_1);
  f_On2 = analogRead(POT_ON_2);
  f_Off2 = analogRead(POT_OFF_2);
}

void loop() {
  updateFilter();          // Run filter as fast as possible
  handleSerialCommands();  // Check for master instructions
  updateLEDs();            // Handle blinking and static LEDs

  // Non-blocking timer for sending data
  if (millis() - lastSerialTime >= sendInterval) {
    lastSerialTime = millis();

    // Convert 12-bit filtered values to stable 10-bit (0-1023)
    /*int p1 = (int)f_On1 >> 2;
    int p2 = (int)f_Off1 >> 2;
    int p3 = (int)f_On2 >> 2;
    int p4 = (int)f_Off2 >> 2;*/

    int p1 = (int)f_On1 ;
    int p2 = (int)f_Off1 ;
    int p3 = (int)f_On2 ;
    int p4 = (int)f_Off2;

    // Send: A,p1,p2,p3,p4
    char buffer[40];
    sprintf(buffer, "A,%04d,%04d,%04d,%04d", p1, p2, p3, p4);
    Serial1.println(buffer);
  }
}

// Low-Pass Filter: Exponential Moving Average
void updateFilter() {
  f_On1  = (analogRead(POT_ON_1)  * alpha) + (f_On1  * (1.0 - alpha));
  f_Off1 = (analogRead(POT_OFF_1) * alpha) + (f_Off1 * (1.0 - alpha));
  f_On2  = (analogRead(POT_ON_2)  * alpha) + (f_On2  * (1.0 - alpha));
  f_Off2 = (analogRead(POT_OFF_2) * alpha) + (f_Off2 * (1.0 - alpha));
}

// Parses: "SET,LED_BYTE,HZ" (Example: SET,255,10)
void handleSerialCommands() {
  if (Serial1.available() > 0) {
    String input = Serial1.readStringUntil('\n');
    input.trim();

    if (input.startsWith("SET,")) {
      int firstComma = input.indexOf(',');
      int secondComma = input.indexOf(',', firstComma + 1);

      if (secondComma != -1) {
        // Parse LED Byte
        String ledPart = input.substring(firstComma + 1, secondComma);
        ledStatusByte = (uint8_t)ledPart.toInt();

        // Parse Frequency
        String hzPart = input.substring(secondComma + 1);
        int hz = hzPart.toInt();

        // Safety: Prevent 0Hz (division by zero)
        if (hz <= 0) hz = 1;
        sendInterval = 1000 / hz;
      }
    }
  }
}

// Controls LEDs and 2Hz Blink logic
void updateLEDs() {
  // Bits 0-3 for Secondary LEDs
  digitalWrite(SEC_2_OFF_LED, (ledStatusByte & 0x01) ? HIGH : LOW); 
  digitalWrite(SEC_2_ON_LED,  (ledStatusByte & 0x02) ? HIGH : LOW); 
  digitalWrite(SEC_1_OFF_LED, (ledStatusByte & 0x04) ? HIGH : LOW); 
  digitalWrite(SEC_1_ON_LED,  (ledStatusByte & 0x08) ? HIGH : LOW); 

  // Bit 5 (decimal 32) triggers 2Hz blink (250ms on, 250ms off)
  if (ledStatusByte & 0x20) { 
    if (millis() - lastBlinkTime >= 250) { 
      lastBlinkTime = millis();
      powerLedState = !powerLedState;
      digitalWrite(POWER_LED, powerLedState);
    }
  } else {
    // If bit 5 is off, bit 4 (decimal 16) is steady ON
    digitalWrite(POWER_LED, (ledStatusByte & 0x10) ? HIGH : LOW);
  }
}