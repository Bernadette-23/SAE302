import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QPushButton, QComboBox, QVBoxLayout
)

from client.client import envoyer_demande


class InterfaceUrgence(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des urgences")
        self.setMinimumWidth(380)

        titre = QLabel("Demande d'urgence")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.depart = QComboBox()
        self.depart.addItems(list("ABCDEFGHIJ"))

        self.destination = QComboBox()
        self.destination.addItems(list("ABCDEFGHIJ"))
        self.destination.setCurrentText("H")

        self.bouton = QPushButton("Calculer le trajet")
        self.resultat = QLabel("Choisis un départ et une destination.")
        self.resultat.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(titre)
        layout.addWidget(QLabel("Carrefour de départ :"))
        layout.addWidget(self.depart)
        layout.addWidget(QLabel("Carrefour d'arrivée :"))
        layout.addWidget(self.destination)
        layout.addWidget(self.bouton)
        layout.addWidget(self.resultat)

        self.setLayout(layout)

        self.bouton.clicked.connect(self.demander_trajet)

    def demander_trajet(self):
        depart = self.depart.currentText()
        destination = self.destination.currentText()

        if depart == destination:
            self.resultat.setText(
                "Choisis deux carrefours différents."
            )
            return

        self.bouton.setEnabled(False)
        self.resultat.setText("Calcul du trajet en cours...")

        try:
            reponse = envoyer_demande(depart, destination)

            if "erreur" in reponse:
                self.resultat.setText(reponse["erreur"])
            elif reponse["cout"] is None:
                self.resultat.setText("Aucun trajet possible.")
            else:
                chemin = " → ".join(reponse["chemin"])
                cout = reponse["cout"]
                nombre_feux = reponse["nombre_de_feux"]

                self.resultat.setText(
                    f"Trajet : {chemin}\n"
                    f"Coût total : {cout}\n"
                    f"Feux concernés : {nombre_feux}"
                )

        except (OSError, ValueError) as erreur:
            self.resultat.setText(
                f"Impossible de contacter le serveur : {erreur}"
            )

        finally:
            self.bouton.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = InterfaceUrgence()
    fenetre.show()
    sys.exit(app.exec())