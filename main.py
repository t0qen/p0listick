#!/usr/bin/env python3
# Cette ligne indique au système que ce fichier est un script Python exécutable
# La partie "#!/usr/bin/env python3" est ce qu'on appelle un "shebang" et permet d'exécuter le script directement sans taper "python" avant

# ===== IMPORTATION DES MODULES =====
# Les imports permettent d'utiliser du code déjà écrit par d'autres personnes
import readline  # Ce module permet d'avoir un historique de commandes (flèches haut/bas)
import re        # Module pour les expressions régulières (pour analyser les commandes)
import sys       # Donne accès à des fonctions liées au système
import time      # Permet d'utiliser des fonctions liées au temps (comme des pauses)
import os        # Permet d'interagir avec le système d'exploitation
from arduino_servo_controller import ArduinoServoController  # Importe notre classe spécifique qui communique avec l'Arduino

# ===== DÉTECTION DES CAPACITÉS DU SYSTÈME =====
# Cette partie essaie d'importer des modules pour la gestion du clavier
# Si ces modules ne sont pas disponibles (par exemple sur Windows), on désactive certaines fonctionnalités
try:
    # Ces modules sont nécessaires pour lire les touches du clavier en temps réel
    import termios    # Pour contrôler les paramètres du terminal
    import tty        # Pour mettre le terminal en mode "raw" (lire touches sans appuyer sur Entrée)
    import select     # Pour vérifier si une touche est disponible sans bloquer
    KEYBOARD_AVAILABLE = True  # Si tous les imports réussissent, on note que le clavier est disponible
except ImportError:
    # Si un des modules n'est pas disponible
    KEYBOARD_AVAILABLE = False  # On note que le clavier n'est pas totalement disponible
    print("Module termios non disponible. Le mode interactif pourrait ne pas fonctionner correctement.")
    # On informe l'utilisateur du problème potentiel

# ===== FONCTION POUR LIRE UNE TOUCHE =====
def getch():
    """Lit un seul caractère du clavier sans attendre la touche Entrée"""
    # Cette fonction lit une touche du clavier sans que l'utilisateur doive appuyer sur Entrée
    
    if not KEYBOARD_AVAILABLE:
        # Si les modules de gestion du clavier ne sont pas disponibles
        return input("Appuyez sur une touche > ")  # On utilise input() comme alternative
    
    # Si les modules sont disponibles, on utilise une méthode plus avancée
    fd = sys.stdin.fileno()  # Obtient l'identifiant du flux d'entrée standard (clavier)
    old_settings = termios.tcgetattr(fd)  # Sauvegarde les paramètres actuels du terminal
    try:
        tty.setraw(fd)  # Met le terminal en mode "raw" pour lire les touches directement
        # Vérifie si une touche est disponible dans les 0.1 secondes
        if select.select([sys.stdin], [], [], 0.1)[0]:
            ch = sys.stdin.read(1)  # Lit un caractère
        else:
            ch = None  # Aucune touche n'a été pressée
    finally:
        # Restaure les paramètres originaux du terminal, même si une erreur survient
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch  # Renvoie le caractère lu ou None

# ===== FONCTION POUR EFFACER L'ÉCRAN =====
def clear_screen():
    """Efface l'écran du terminal"""
    # Cette fonction efface tout le contenu du terminal pour avoir un affichage propre
    # Elle utilise la commande appropriée selon le système d'exploitation
    os.system('cls' if os.name == 'nt' else 'clear')
    # 'cls' est la commande pour Windows ('nt')
    # 'clear' est la commande pour Linux/Mac (systèmes Unix)

# ===== MODE INTERACTIF =====
#!/usr/bin/env python3
# Les imports et les fonctions précédentes restent inchangés
# Modification du mode interactif et du mode interpréteur

# ===== MODE INTERACTIF =====
def interactive_mode(controller):
    """Mode interactif utilisant les touches pour contrôler les servos"""
    
    # Tableau des angles des servos
    angles = [90, 90, 90, 90]  # Angles par défaut pour chaque servo (90° position centrale)
    step = 5  # Pas de modification d'angle (de combien de degrés on change à chaque touche)
    
    # Mapping des touches aux servos
    # Format: {touche: (numéro_servo, direction)}
    key_servo_mapping = {
        'l': (1, -1),  # Servo 1 (J/K) diminue
        'm': (1, 1),   # Servo 1 (J/K) augmente
        'j': (2, -1),  # Servo 2 (J/K) diminue
        'k': (2, 1),   # Servo 2 (J/K) augmente
        'u': (3, -1),  # Servo 3 (U/I) diminue
        'i': (3, 1),   # Servo 3 (U/I) augmente
        'o': (0, -1),  # Servo 4 (O/P) diminue
        'p': (0, 1)    # Servo 4 (O/P) augmente
    }
    
    # Initialiser tous les servos à 90 degrés (position centrale)
    for i in range(4):
        controller.set_servo_angle(i, angles[i])
        time.sleep(0.1)
    
    clear_screen()
    
    # Affichage des instructions
    print("=== Mode Interactif Avancé ===")
    print("Contrôle des servos :")
    print("  Servo 1 (L/M): Diminuer/Augmenter")
    print("  Servo 2 (J/K): Diminuer/Augmenter")
    print("  Servo 3 (U/I): Diminuer/Augmenter")
    print("  Servo 4 (O/P): Diminuer/Augmenter")
    print("  +/-: Modifier le pas de changement d'angle")
    print("  r: Réinitialiser tous les servos à 90°")
    print("  q: Quitter le mode interactif")
    
    # Boucle principale du mode interactif
    while True:
        # Afficher l'état actuel des servos
        print("\n" + "-" * 40)
        print(f"Pas de changement: {step}°")
        
        # Affichage des angles pour tous les servos
        print("Angles des servos:", end=" ")
        for i, angle in enumerate(angles):
            print(f"{i+1}:{angle}°", end=" ")
        print("\n" + "-" * 40)
        
        # Lire une touche du clavier
        key = getch()
        
        if not key:  # Si aucune touche n'a été pressée
            continue
            
        # Gestion des touches pressées
        if key in ['q', 'Q']:
            print("Sortie du mode interactif")
            break
        
        # Modification des servos
        if key in key_servo_mapping:
            servo, direction = key_servo_mapping[key]
            
            # Calculer le nouvel angle
            new_angle = angles[servo] + (step * direction)
            
            # S'assurer que l'angle reste entre 0 et 180
            new_angle = max(0, min(180, new_angle))
            
            # Mettre à jour l'angle
            angles[servo] = new_angle
            
            # Envoyer la commande au servo
            success, _ = controller.set_servo_angle(servo, new_angle)
            if not success:
                print(f"Erreur lors du réglage de l'angle du servo {servo+1}")
        
        # Modifier le pas de changement d'angle
        elif key == '+':
            step = min(20, step + 1)
            print(f"Pas modifié à {step}°")
        elif key == '-':
            step = max(1, step - 1)
            print(f"Pas modifié à {step}°")
        
        # Réinitialiser tous les servos à 90°
        elif key in ['r', 'R']:
            reset_angles = [90, 90, 90, 90]
            
            # Mettre à jour les angles stockés
            angles = reset_angles.copy()
            
            # Envoyer la commande à tous les servos en même temps
            success, responses = controller.set_servo_angle([0, 1, 2, 3], reset_angles, multi_servo=True)
            
            if success:
                print("Tous les servos réinitialisés à 90°")
            else:
                print("Erreur lors de la réinitialisation des servos")
        
        # Pause pour éviter de surcharger le port série
        time.sleep(0.05)
        
        # Effacer les lignes d'état pour la prochaine itération
        print("\033[3A", end="")  # Remonte le curseur de 3 lignes

# ===== MODE INTERPRÉTEUR =====
def interpreter_mode(controller):
    """Mode interpréteur de commandes"""
    
    # Affichage des instructions
    print("\n=== Mode Interpréteur ===")
    print("Exemples de commandes:")
    print("  a(0, 90)        - Positionne le servo 0 à 90 degrés")
    print("  a(1, 45, 2, 135) - Positionne les servos 1 et 2 simultanément")
    print("  a(0, 0, 1, 180, 2, 90, 3, 45) - Positionne 4 servos")
    print("  exit            - Quitter le programme")
    
    # Boucle principale d'interprétation des commandes
    while True:
        try:
            # Lecture d'une commande tapée par l'utilisateur
            command = input("\n> ").strip()
            
            # Vérification de la commande de sortie
            if command.lower() in ['exit', 'quit', 'q']:
                print("Fermeture du mode interpréteur...")
                break
            
            # Analyse de la commande avec une expression régulière
            pattern = r'a\(([^)]+)\)'
            match = re.match(pattern, command)
            
            if match:
                # Extraire les arguments
                args_str = match.group(1)
                
                # Diviser les arguments en couples (servo, angle)
                try:
                    # Convertir la chaîne d'arguments en liste d'entiers
                    args = [int(x.strip()) for x in args_str.split(',')]
                    
                    # Vérifier que le nombre d'arguments est pair 
                    # et que chaque paire correspond bien à (servo, angle)
                    if len(args) % 2 != 0 or len(args) > 8:
                        raise ValueError("Nombre incorrect d'arguments")
                    
                    # Séparer les servos et les angles
                    servos = args[::2]   # Arguments pairs (indices 0, 2, 4...)
                    angles = args[1::2]  # Arguments impairs (indices 1, 3, 5...)
                    
                    # Vérifier que tous les servos sont valides
                    if any(s < 0 or s > 3 for s in servos):
                        raise ValueError("Numéro de servo invalide")
                    
                    # Vérifier que tous les angles sont valides
                    if any(a < 0 or a > 180 for a in angles):
                        raise ValueError("Angle invalide")
                    
                    # Envoi de la commande au contrôleur
                    success, responses = controller.set_servo_angle(servos, angles, multi_servo=True)
                    
                    if success:
                        for response in responses:
                            print(f"Arduino: {response}")
                    else:
                        print(f"Erreur: {responses}")
                    
                except ValueError as e:
                    print(f"Erreur de format: {e}")
                    print("Format attendu: a(servo1, angle1, servo2, angle2, ...)")
            else:
                print("Commande non reconnue. Format attendu: a(servo1, angle1, servo2, angle2, ...)")
        
        except KeyboardInterrupt:
            print("\nFermeture du mode interpréteur...")
            break
        except Exception as e:
            print(f"Erreur: {e}")

# Le reste du code reste identique (main() et autres fonctions)


# ===== MODE SÉQUENCES PERSONNALISÉES =====
def custom_movements(controller):
    """
    Mode séquences personnalisées
    Cette fonction peut être modifiée pour inclure vos propres mouvements prédéfinis
    """
    # Cette fonction permet d'exécuter des séquences de mouvements préprogrammées
    
    # Affichage du menu des séquences
    print("\n=== Mode Séquences Personnalisées ===")
    print("Choisissez une séquence :")
    print("1. Séquence 1 (exemple)")
    print("2. Séquence 2 (exemple)")
    print("3. Retour au menu principal")
    
    # Demande du choix à l'utilisateur
    choice = input("Votre choix: ").strip()
    
    # Traitement du choix
    if choice == '1':
        print("Exécution de la séquence 1...")
        # EXEMPLE: Vous pouvez remplacer ce code par vos propres séquences
        sequence_1(controller)  # Appelle la fonction qui définit la séquence 1
    elif choice == '2':
        print("Exécution de la séquence 2...")
        # EXEMPLE: Vous pouvez remplacer ce code par vos propres séquences
        sequence_2(controller)  # Appelle la fonction qui définit la séquence 2
    elif choice == '3':
        return  # Retourne au menu principal
    else:
        print("Choix invalide.")  # Si l'utilisateur entre autre chose que 1, 2 ou 3
        
# ===== DÉFINITION DES SÉQUENCES =====
def sequence_1(controller):
    """
    Exemple de séquence 1
    À personnaliser selon vos besoins
    """
    # CETTE FONCTION EST À MODIFIER POUR VOTRE PROPRE SÉQUENCE
    print("Séquence 1 - Mouvement d'exemple")
    
    # Exemple de mouvements séquentiels (un après l'autre)
    controller.set_servo_angle(0, 0)    # Déplace le servo 0 à 0°
    time.sleep(0.5)                     # Attend 0.5 seconde
    controller.set_servo_angle(0, 180)  # Déplace le servo 0 à 180°
    time.sleep(0.5)                     # Attend 0.5 seconde
    controller.set_servo_angle(0, 90)   # Déplace le servo 0 à 90° (centre)
    time.sleep(0.5)                     # Attend 0.5 seconde
    
    print("Séquence 1 terminée. Appuyez sur Entrée pour continuer...")
    input()  # Attend que l'utilisateur appuie sur Entrée
    
def sequence_2(controller):
    """
    Exemple de séquence 2
    À personnaliser selon vos besoins
    """
    # CETTE FONCTION EST À MODIFIER POUR VOTRE PROPRE SÉQUENCE
    print("Séquence 2 - Mouvement d'exemple")
    
    # Exemple de mouvements coordonnés entre deux servos
    # Cette boucle va de 0 à 180 par pas de 10
    for angle in range(0, 181, 10):
        controller.set_servo_angle(1, angle)         # Servo 1: angle augmente de 0° à 180°
        controller.set_servo_angle(2, 180 - angle)   # Servo 2: angle diminue de 180° à 0°
        time.sleep(0.1)                              # Pause de 0.1 seconde entre chaque pas
    
    print("Séquence 2 terminée. Appuyez sur Entrée pour continuer...")
    input()  # Attend que l'utilisateur appuie sur Entrée

# ===== PROGRAMME PRINCIPAL =====
def main():
    """
    Programme principal qui utilise le module ArduinoServoController
    """
    print("=== Contrôleur de Servomoteurs Arduino ===")
    
    # Configuration du port série
    port = '/dev/ttyUSB0'  # Port par défaut (typique sur Linux)
    
    # Permettre la spécification d'un port différent via les arguments de ligne de commande
    if len(sys.argv) > 1:  # Si au moins un argument a été passé
        port = sys.argv[1]  # Le premier argument est considéré comme le port
    
    # Initialisation du contrôleur avec le port spécifié
    controller = ArduinoServoController(port=port)
    print(f"Connexion à l'Arduino sur {port}...")
    
    # Tentative de connexion à l'Arduino
    success, messages = controller.connect()
    if not success:  # Si la connexion a échoué
        print(f"Erreur de connexion: {messages}")
        return  # Quitte la fonction main()
    
    # Si la connexion a réussi
    print("Connexion établie!")
    for msg in messages:
        print(f"Arduino: {msg}")  # Affiche les messages de l'Arduino
    
    # ===== BOUCLE PRINCIPALE DU MENU =====
    while True:
        # Affichage du menu principal
        clear_screen()
        print("\n=== Menu Principal ===")
        print("Choisissez un mode:")
        print("1. Mode interactif (flèches et touches numériques)")
        print("2. Mode interpréteur (commandes textuelles)")
        print("3. Mode séquences personnalisées")
        print("4. Quitter le programme")
        
        # Demande du choix à l'utilisateur
        choice = input("Votre choix (1-4): ").strip()
        
        # Traitement du choix
        if choice == '1':  # Mode interactif
            # Vérification de la compatibilité (pour les systèmes autres que Windows)
            if not KEYBOARD_AVAILABLE and os.name != 'nt':
                print("Attention: Le mode interactif nécessite les modules termios, tty et select.")
                print("Ces modules peuvent ne pas être disponibles sur tous les systèmes.")
                confirm = input("Continuer quand même? (o/n): ").lower()
                if confirm != 'o':  # Si l'utilisateur ne confirme pas
                    continue  # Retourne au menu principal
            interactive_mode(controller)  # Lance le mode interactif
            
        elif choice == '2':  # Mode interpréteur
            interpreter_mode(controller)  # Lance le mode interpréteur
            
        elif choice == '3':  # Mode séquences personnalisées
            custom_movements(controller)  # Lance le mode séquences
            
        elif choice == '4':  # Quitter le programme
            print("Fermeture du programme...")
            break  # Quitte la boucle principale
            
        else:  # Si l'utilisateur entre autre chose que 1, 2, 3 ou 4
            print("Choix invalide. Veuillez entrer un nombre entre 1 et 4.")
            time.sleep(1)  # Pause d'1 seconde pour que l'utilisateur puisse lire le message
    
    # Fermeture propre de la connexion avant de quitter
    controller.disconnect()
    print("Connexion fermée. Merci d'avoir utilisé le contrôleur de servomoteurs!")

# ===== POINT D'ENTRÉE DU PROGRAMME =====
if __name__ == "__main__":
    # Cette condition vérifie si le script est exécuté directement (et non importé)
    # C'est une pratique standard en Python
    main()  # Si c'est le cas, on appelle la fonction principale
