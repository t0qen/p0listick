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
        self.current_angles = [90, 90, 90, 90]  # Angles actuels des servos
        
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
    
    def set_servo_angle(self, servo_num, angle, multi_servo=False):
        """
        Définit l'angle d'un ou plusieurs servomoteurs
        
        Args:
            servo_num (int or list): Numéro du servomoteur ou liste de numéros
            angle (int or list): Angle désiré ou liste d'angles
            multi_servo (bool): Si True, permet de mettre à jour plusieurs servos simultanément
            
        Returns:
            tuple: (bool, str) - Succès et message associé
        """
        if not self.connected:
            return False, "Non connecté à l'Arduino"
        
        # Convertir les entrées en listes si ce ne sont pas déjà des listes
        if not isinstance(servo_num, list):
            servo_num = [servo_num]
        if not isinstance(angle, list):
            angle = [angle]
        
        # Vérification des valeurs
        for s, a in zip(servo_num, angle):
            if not (0 <= s <= 3):
                return False, f"Le numéro de servo {s} doit être entre 0 et 3"
            
            if not (0 <= a <= 180):
                return False, f"L'angle {a} doit être entre 0 et 180 degrés"
        
        # Préparer la commande
        if multi_servo:
            # Format de commande : "servo1,angle1;servo2,angle2;servo3,angle3;servo4,angle4"
            command = ";".join([f"{s},{a}" for s, a in zip(servo_num, angle)]) + "\n"
        else:
            # Si pas multi_servo, n'envoie qu'un seul servo à la fois
            command = f"{servo_num[0]},{angle[0]}\n"
        
        # Envoi de la commande à l'Arduino
        self.serial.write(command.encode('utf-8'))
        
        # Mettre à jour les angles actuels
        for s, a in zip(servo_num, angle):
            self.current_angles[s] = a
        
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
            
        # Test simple de contrôle multiple
        success, responses = controller.set_servo_angle([0, 1, 2, 3], [45, 90, 135, 180], multi_servo=True)
        for response in responses:
            print(f"Arduino: {response}")
            
        controller.disconnect()
        print("Connexion fermée")
    else:
        print(f"Erreur de connexion: {messages}")

