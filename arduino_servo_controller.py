#!/usr/bin/env python3
import serial
import time

class ArduinoServoController:
    """
    Classe pour contrôler les servomoteurs via l'Arduino
    """
    
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600):
        """
        Initialise la connexion avec l'Arduino
        
        Args:
            port (str): Port série de l'Arduino
            baud_rate (int): Vitesse de transmission
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.connected = False
        
    def connect(self):
        """
        Établit la connexion avec l'Arduino
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            # Attendre que la connexion Arduino soit prête
            time.sleep(2)
            
            # Lire et retourner les messages d'initialisation
            messages = []
            while self.serial.in_waiting:
                message = self.serial.readline().decode('utf-8').strip()
                messages.append(message)
                
            self.connected = True
            return True, messages
            
        except serial.SerialException as e:
            return False, str(e)
            
    def disconnect(self):
        """
        Ferme la connexion avec l'Arduino
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.connected = False
            return True
        return False
    
    def set_servo_angle(self, servo_num, angle):
        """
        Définit l'angle d'un servomoteur
        
        Args:
            servo_num (int): Numéro du servomoteur (0-3)
            angle (int): Angle désiré (0-180)
            
        Returns:
            tuple: (bool, str) - Succès et message associé
        """
        if not self.connected:
            return False, "Non connecté à l'Arduino"
            
        # Vérification des valeurs
        if not (0 <= servo_num <= 3):
            return False, "Le numéro de servo doit être entre 0 et 3"
        
        if not (0 <= angle <= 180):
            return False, "L'angle doit être entre 0 et 180 degrés"
        
        # Envoi de la commande à l'Arduino
        self.serial.write(f"{servo_num},{angle}\n".encode('utf-8'))
        
        # Attente et lecture de la réponse
        time.sleep(0.1)
        responses = []
        while self.serial.in_waiting:
            response = self.serial.readline().decode('utf-8').strip()
            responses.append(response)
            
        return True, responses
    
    def is_connected(self):
        """
        Vérifie si la connexion est active
        
        Returns:
            bool: État de la connexion
        """
        return self.connected

# Exemple d'utilisation simple si le fichier est exécuté directement
if __name__ == "__main__":
    controller = ArduinoServoController()
    success, messages = controller.connect()
    
    if success:
        print(f"Connexion établie sur {controller.port}")
        for msg in messages:
            print(f"Arduino: {msg}")
            
        # Test simple
        success, responses = controller.set_servo_angle(0, 90)
        for response in responses:
            print(f"Arduino: {response}")
            
        controller.disconnect()
        print("Connexion fermée")
    else:
        print(f"Erreur de connexion: {messages}")
