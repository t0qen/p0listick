import serial  # Bibliothèque pour la communication série avec l'Arduino
import time    # Bibliothèque pour les fonctions de temporisation
try:
    import readline  # Ajoute la gestion de l'historique des commandes (fonctionne sous Unix/Linux/MacOS)
except ImportError:
    try:
        import pyreadline as readline  # Alternative pour Windows
    except ImportError:
        print("Module readline non disponible. L'historique des commandes ne sera pas disponible.")

# Variable globale pour stocker l'objet de connexion série
ser = None

def connect_arduino(port='/dev/ttyACM0', baudrate=9600):
    """
    Établit une connexion avec l'Arduino via le port série.
    
    Args:
        port (str): Port série où l'Arduino est connecté (par défaut '/dev/ttyACM0' pour Linux)
                   Sous Windows, ce serait typiquement 'COM3' ou similaire
        baudrate (int): Vitesse de communication en bauds (doit correspondre à celle configurée sur l'Arduino)
    
    Returns:
        serial.Serial ou None: Objet de connexion ou None en cas d'échec
    """
    global ser  # Référence à la variable globale pour y accéder ailleurs dans le programme
    try:
        # Initialise la connexion série avec le délai d'attente de 1 seconde
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Pause de 2 secondes pour laisser le temps à l'Arduino de se réinitialiser après la connexion
        print("Arduino connecté avec succès")
        return ser
    except serial.SerialException as e:
        # Capture et affiche les erreurs de connexion (port incorrect, Arduino non connecté, etc.)
        print(f"Erreur de connexion: {e}")
        ser = None
        return None

def move_servos(servo_positions):
    """
    Envoie des commandes à l'Arduino pour positionner les servomoteurs.
    
    Args:
        servo_positions (dict): Dictionnaire avec les numéros de servo comme clés 
                                et les angles désirés comme valeurs
                                Exemple: {0: 45, 1: 90, 2: 120}
    """
    # Formatage de la commande sous forme de chaîne: "servo1, angle1, servo2, angle2, ..."
    command = ', '.join([f"{servo}, {angle}" for servo, angle in servo_positions.items()])
    
    try:
        # Ajout d'un saut de ligne pour indiquer la fin de la commande à l'Arduino
        full_command = command + '\n'
        # Encode et envoie la commande à l'Arduino
        ser.write(full_command.encode('utf-8'))
        # Attendre un moment pour que l'Arduino exécute la commande
        time.sleep(0.5)
        
        # Vérifier si l'Arduino a envoyé une réponse
        if ser.in_waiting:
            # Lecture et décodage de la réponse de l'Arduino
            response = ser.readline().decode('utf-8').strip()
            print(f"Réponse Arduino: {response}")
    
    except Exception as e:
        # Capture les erreurs potentielles lors de l'envoi des commandes
        print(f"Erreur lors de l'envoi à Arduino: {e}")

def reset_position():
    """
    Réinitialise tous les servos à la position centrale (90°).
    Cette fonction utilise move_servos() pour régler les 4 servos (0-3) à 90 degrés.
    """
    move_servos({0: 90, 1: 90, 2: 90, 3: 90})
    print("Position réinitialisée")

def mouvements_predefinis():
    """
    Fonction pour exécuter des séquences de mouvements prédéfinis.
    Cette fonction est un squelette destiné à être personnalisé avec des séquences
    spécifiques de mouvements pour le robot.
    """
    print("Mode mouvements prédéfinis activé")
    
    # Séquence d'initialisation - commence par mettre tous les servos en position neutre
    reset_position()
    time.sleep(1)  # Pause d'une seconde
    
    # TODO: Ajoutez vos séquences de mouvements prédéfinis ici
    # Exemple commenté montrant comment pourrait être implémentée une séquence "Salut":
    # print("Exécution de la séquence 1: Salut")
    # move_servos({0: 45})  # Déplace le servo 0 à 45 degrés
    # time.sleep(0.5)       # Pause de 0.5 seconde
    # move_servos({0: 135}) # Déplace le servo 0 à 135 degrés (mouvement opposé)
    # time.sleep(0.5)       # Pause de 0.5 seconde
    # move_servos({0: 90})  # Retour à la position neutre
    
    print("Fin des mouvements prédéfinis")

def mode_interpreteur():
    """
    Mode interactif permettant à l'utilisateur de contrôler les servomoteurs en direct
    en saisissant des commandes au format spécifique.
    Avec l'importation de readline, cette fonction prend en charge l'historique des commandes.
    """
    print("\n=== MODE INTERPRÉTEUR ===")
    print("Entrez les commandes au format: 'numéro_servo:angle, numéro_servo:angle, ...'")
    print("Par exemple: '0:45, 1:120, 3:30'")
    print("Commandes spéciales:")
    print("  'reset' pour réinitialiser tous les servos à 90°")
    print("  'exit' pour quitter le mode interpréteur")
    print("  Utilisez les flèches haut/bas pour naviguer dans l'historique des commandes")
    
    # Configuration de l'historique des commandes si readline est disponible
    history_file = ".servo_history"
    try:
        readline.read_history_file(history_file)
        # Limiter l'historique à 100 entrées
        readline.set_history_length(100)
    except (FileNotFoundError, NameError, AttributeError):
        # Fichier non trouvé (première exécution) ou readline non disponible
        pass
    
    while True:  # Boucle infinie pour continuer à recevoir des commandes
        try:
            # Demande à l'utilisateur de saisir une commande
            # La bibliothèque readline gère automatiquement l'historique des commandes
            cmd = input("\nCommande > ").strip()
            
            # Vérification des commandes spéciales
            if cmd.lower() == 'exit':
                print("Sortie du mode interpréteur")
                break  # Sort de la boucle while et retourne au menu principal
            
            if cmd.lower() == 'reset':
                reset_position()  # Réinitialise tous les servos
                continue  # Revient au début de la boucle pour demander une nouvelle commande
            
            # Parser la commande pour extraire les positions des servos
            servo_positions = {}  # Dictionnaire pour stocker les positions servo:angle
            for part in cmd.split(','):  # Divise la commande par les virgules
                part = part.strip()  # Supprime les espaces avant/après
                if ':' in part:
                    try:
                        # Divise chaque partie par les deux-points pour obtenir le numéro du servo et l'angle
                        servo, angle = part.split(':')
                        # Convertit les chaînes en entiers et les ajoute au dictionnaire
                        servo_positions[int(servo)] = int(angle)
                    except (ValueError, IndexError):
                        # Gère les erreurs de format ou de conversion
                        print(f"Format incorrect pour '{part}'. Utilisez 'numéro_servo:angle'")
            
            # Exécute le mouvement s'il y a des positions valides
            if servo_positions:
                print(f"Déplacement des servos: {servo_positions}")
                move_servos(servo_positions)  # Appel à la fonction qui envoie les commandes à l'Arduino
            else:
                print("Aucune position de servo valide trouvée dans la commande")
                
        except KeyboardInterrupt:
            # Permet de quitter proprement avec Ctrl+C
            print("\nInterruption clavier détectée")
            break
        except Exception as e:
            # Capture toute autre erreur inattendue
            print(f"Erreur: {e}")
    
    # Sauvegarde l'historique des commandes à la sortie
    try:
        readline.write_history_file(history_file)
    except (NameError, AttributeError):
        # readline n'est pas disponible
        pass
def main():
    """
    Fonction principale qui initialise le programme et présente le menu principal
    permettant de choisir entre les différents modes de fonctionnement.
    """
    # Tente d'établir une connexion avec l'Arduino
    arduino = connect_arduino()
    
    # Vérifie si la connexion a réussi
    if not ser:
        print("Impossible de se connecter à l'Arduino. Vérifiez la connexion.")
        return  # Sort de la fonction main si la connexion a échoué
    
    try:
        # Boucle principale du programme
        while True:
            # Affiche le menu des options disponibles
            print("\n=== MENU PRINCIPAL ===")
            print("1. Mode interpréteur de commandes")
            print("2. Mode mouvements prédéfinis")
            print("3. Quitter")
            
            # Demande à l'utilisateur de choisir une option
            choix = input("Choisissez un mode (1-3): ").strip()
            
            # Exécute l'action correspondant au choix de l'utilisateur
            if choix == '1':
                mode_interpreteur()  # Mode de contrôle interactif
            elif choix == '2':
                mouvements_predefinis()  # Mode séquences prédéfinies
            elif choix == '3':
                print("Fin du programme")
                break  # Sort de la boucle et termine le programme
            else:
                print("Choix invalide, veuillez réessayer")
    
    except KeyboardInterrupt:
        # Gère l'interruption par Ctrl+C pour terminer proprement le programme
        print("\nArrêt du programme")
    
    finally:
        # Ce bloc s'exécute toujours, que le programme se termine normalement ou avec une erreur
        if ser:
            ser.close()  # Ferme la connexion série avec l'Arduino
            print("Connexion Arduino fermée")

# Point d'entrée du programme
if __name__ == "__main__":
    # Cette condition assure que le code ne s'exécute que si le script est lancé directement
    # (et non s'il est importé comme module dans un autre script)
    main()

