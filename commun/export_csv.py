
import csv
import os
import mariadb
import time

from commun.base_donnees import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def exporter_evenements_csv():

    connexion = None
    curseur = None

    try:
        connexion = mariadb.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        curseur = connexion.cursor()

        curseur.execute("""
            SELECT id, date_heure, type_evenement,
                   depart, destination, chemin, cout, details
            FROM evenements
            ORDER BY id
        """)

        evenements = curseur.fetchall()

        # Créer le dossier exports à la racine du projet
        dossier_projet = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        dossier_exports = os.path.join(dossier_projet, "exports")
        os.makedirs(dossier_exports, exist_ok=True)

        chemin_csv = os.path.join(
            dossier_exports, "evenements.csv"
        )

        # Réécrire le CSV avec les données de MariaDB
        with open(chemin_csv, "w", newline="", encoding="utf-8-sig") as fichier:
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
        if curseur is not None:
            curseur.close()

        if connexion is not None:
            connexion.close()

def surveiller_evenements():
    print("[CSV] Surveillance automatique activée.")

    while True:
        exporter_evenements_csv()
        time.sleep(5)