// pattern : servo, angle, other servo, angle

#include <Servo.h>

Servo servo0;  
Servo servo1;  
Servo servo2;  
Servo servo3;  

void setup() {
  Serial.begin(9600);
  
  servo0.attach(3);
  servo1.attach(5);
  servo2.attach(6);
  servo3.attach(9);
  
  servo0.write(90);
  servo1.write(90);
  servo2.write(90);
  servo3.write(90);
}

void loop() {
  if (Serial.available()) {
    String input_string = Serial.readStringUntil('\n');
    
    input_string.trim();

    int values[8];
    int value_count = 0;

    for (int i = 0; i < input_string.length(); i++) {
      String current_value = "";
      
      while (i < input_string.length() && input_string[i] != ',') {
        if (input_string[i] != ' ') {
          current_value += input_string[i];
        }
        i++;
      }
      if (current_value.length() > 0) {
        values[value_count++] = current_value.toInt();
      }
    }

    if (value_count % 2 == 0 && value_count > 0) {
      Serial.println("Received");
      for (int i = 0; i < value_count; i += 2) {
        int servo_num = values[i];
        int angle = values[i+1];
        
        if (servo_num = 2 ||servo_num = 3) {
          angle = abs(angle - 180);
        }
        
        switch(servo_num) {
          case 0:
            servo0.write(angle);
            break;
          case 1:
            servo1.write(angle);
            break;
          case 2:
            servo2.write(angle);
            break;
          case 3:
            servo3.write(angle);
            break;
          default:
            break;
        }
      }
    }
  }
}

