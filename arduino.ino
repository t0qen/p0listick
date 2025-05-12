#include <Servo.h>

// Créer un tableau d'objets Servo
Servo servos[4];

// Broches des servomoteurs
const int SERVO_PINS[4] = {3, 5, 6, 9};

void setup() {
  // Initialiser la communication série
  Serial.begin(9600);
  
  // Attacher les servos aux broches correspondantes
  for (int i = 0; i < 4; i++) {
    servos[i].attach(SERVO_PINS[i]);
    // Initialiser tous les servos à la position centrale
    servos[i].write(90);
  }
  
  // Message d'initialisation
  Serial.println("Servos initialisés - Prêt à recevoir des commandes");
}

void loop() {
  // Vérifier si des données sont disponibles sur le port série
  if (Serial.available() > 0) {
    // Lire la ligne complète
    String data = Serial.readStringUntil('\n');
    
    // Variables pour stocker les informations
    int servos_to_update[4] = {-1, -1, -1, -1};
    int angles[4] = {-1, -1, -1, -1};
    
    // Analyser la chaîne de données
    int index = 0;
    char* command = strtok((char*)data.c_str(), ";");
    while (command != NULL && index < 4) {
      // Convertir la commande en numéro de servo et angle
      int servo, angle;
      if (sscanf(command, "%d,%d", &servo, &angle) == 2) {
        // Vérifier que le servo et l'angle sont dans les plages valides
        if (servo >= 0 && servo < 4 && angle >= 0 && angle <= 180) {
          servos_to_update[index] = servo;
          angles[index] = angle;
          index++;
        }
      }
      command = strtok(NULL, ";");
    }
    
    // Mettre à jour les servos spécifiés
    for (int i = 0; i < 4; i++) {
      if (servos_to_update[i] != -1) {
        servos[servos_to_update[i]].write(angles[i]);
        
        // Confirmation de l'action
        Serial.print("Servo ");
        Serial.print(servos_to_update[i]);
        Serial.print(" positionné à ");
        Serial.print(angles[i]);
        Serial.println(" degrés");
      }
    }
  }
}

