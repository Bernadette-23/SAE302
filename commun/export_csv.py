"""
Module chargé d'exporter les événements enregistrés dans MariaDB
vers un fichier CSV et d'effectuer cet export automatiquement.
"""

import csv
import os
import mariadb
import time

from commun.base_donnees import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def exporter_evenements_csv():
    """
    Récupère les événements enregistrés dans MariaDB et les exporte
    dans un fichier CSV créé dans le dossier exports du projet.
    """
    connexion = None
    curseur = None

    try:
        # Connexion à la base de données MariaDB
        connexion = mariadb.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Création du curseur pour exécuter la requête SQL
        curseur = connexion.cursor()

        # Récupération de tous les événements, classés par identifiant
        curseur.execute("""
            SELECT id, date_heure, type_evenement,
                   depart, destination, chemin, cout, details
            FROM evenements
            ORDER BY id
        """)

        evenements = curseur.fetchall()

        # Détermination du chemin vers la racine du projet
        dossier_projet = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # Création du dossier exports s'il n'existe pas déjà
        dossier_exports = os.path.join(dossier_projet, "exports")
        os.makedirs(dossier_exports, exist_ok=True)

        # Définition du chemin du fichier CSV à générer
        chemin_csv = os.path.join(
            dossier_exports, "evenements.csv"
        )

        # Ouverture du fichier en écriture et génération du contenu CSV
        # L'encodage utf-8-sig facilite l'ouverture du fichier avec Excel
        with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as fichier:
            redacteur = csv.writer(fichier, delimiter=";")

            # Écriture des noms de colonnes dans la première ligne
            redacteur.writerow([
                "ID",
                "Date et heure",
                "Type événement",
                "Départ",
                "Destination",
                "Chemin",
                "Coût",
                "Détails"
            ])

            # Écriture des événements récupérés depuis MariaDB
            redacteur.writerows(evenements)

        print("[CSV] Export des événements terminé.")

    except mariadb.Error as erreur:
        # Affichage d'un message si une erreur MariaDB survient
        print(f"[CSV] Erreur MariaDB : {erreur}")

    except OSError as erreur:
        # Affichage d'un message si une erreur survient lors de la gestion du fichier
        print(f"[CSV] Erreur fichier : {erreur}")

    finally:
        # Fermeture du curseur et de la connexion à la base de données
        if curseur is not None:
            curseur.close()

        if connexion is not None:
            connexion.close()


def surveiller_evenements():
    """
    Lance une surveillance automatique qui réexporte les événements
    de MariaDB vers le fichier CSV toutes les cinq secondes.
    """
    print("[CSV] Surveillance automatique activée.")

    # Répétition de l'export à intervalle régulier
    while True:
        exporter_evenements_csv()
        time.sleep(5)