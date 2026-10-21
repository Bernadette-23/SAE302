import mariadb


# Configuration de la base MariaDB sur la VM Debian
DB_HOST = "172.20.10.3"
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
    """Enregistre un événement dans la base sae302."""

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

        connexion.commit()
        print("[Base de données] Événement enregistré.")
        return True

    except mariadb.Error as erreur:
        print(f"[Base de données] Erreur : {erreur}")
        return False

    finally:
        if curseur is not None:
            curseur.close()

        if connexion is not None:
            connexion.close()
