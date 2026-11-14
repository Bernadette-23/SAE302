"""
Module chargé de gérer l'enregistrement des événements
dans la base de données MariaDB du projet.
"""

import mariadb


# Configuration de la connexion à la base MariaDB sur la VM Debian
DB_HOST = "127.0.0.1"  # Utiliser l'adresse IP de la VM pour une connexion distante
DB_PORT = 3306
DB_USER = "bc"
DB_PASSWORD = "galactique"
DB_NAME = "sae302"


def enregistrer_evenement(
    type_evenement,
    depart,
    destination,
    chemin,
    cout,
    details
):
    """
    Enregistre un événement dans la base de données sae302 en utilisant
    les informations du trajet, puis indique si l'enregistrement a réussi.
    """
    connexion = None
    curseur = None

    try:
        # Connexion à la base de données MariaDB avec les paramètres définis
        connexion = mariadb.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Création du curseur pour exécuter les requêtes SQL
        curseur = connexion.cursor()

        # Préparation de la requête d'insertion d'un nouvel événement
        # La date et l'heure sont générées directement par MariaDB avec NOW()
        requete = """
            INSERT INTO evenements (
                date_heure,
                type_evenement,
                depart,
                destination,
                chemin,
                cout,
                details
            )
            VALUES (NOW(), ?, ?, ?, ?, ?, ?)
        """

        # Exécution de la requête avec les valeurs de l'événement
        curseur.execute(
            requete,
            (
                type_evenement,
                depart,
                destination,
                chemin,
                cout,
                details
            )
        )

        # Validation de l'insertion dans la base de données
        connexion.commit()
        print("[Base de données] Événement enregistré.")
        return True

    except mariadb.Error as erreur:
        # Affichage de l'erreur en cas d'échec de la connexion ou de l'insertion
        print(f"[Base de données] Erreur : {erreur}")
        return False

    finally:
        # Fermeture du curseur et de la connexion, même en cas d'erreur
        if curseur is not None:
            curseur.close()

        if connexion is not None:
            connexion.close()