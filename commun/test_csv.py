
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

        curseur = connexion.cursor()

        # Récupération de tous les événements
        curseur.execute("""
            SELECT id, date_heure, type_evenement,
                   depart, destination, chemin, cout, details
            FROM evenements
            ORDER BY id
        """)

        evenements = curseur.fetchall()

        # Détermination de la racine du projet
        dossier_projet = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # Création du dossier exports s'il n'existe pas
        dossier_exports = os.path.join(dossier_projet, "exports")
        os.makedirs(dossier_exports, exist_ok=True)

        chemin_csv = os.path.join(
            dossier_exports, "../exports/evenements.csv"
        )

        # Écriture du fichier CSV
        with open(
            chemin_csv, "w", newline="", encoding="utf-8-sig"
        ) as fichier:

            redacteur = csv.writer(fichier, delimiter=";")

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

            redacteur.writerows(evenements)

        print("[CSV] Export des événements terminé.")

    except mariadb.Error as erreur:
        print(f"[CSV] Erreur MariaDB : {erreur}")

    except OSError as erreur:
        print(f"[CSV] Erreur fichier : {erreur}")

    finally:
        # Fermeture des ressources
        if curseur is not None:
            curseur.close()

        if connexion is not None:
            connexion.close()


def surveiller_evenements():
    """
    Réexporte automatiquement les événements de MariaDB
    dans le fichier CSV toutes les cinq secondes.
    """
    print("[CSV] Surveillance automatique activée.")

    while True:
        exporter_evenements_csv()
        time.sleep(5)
