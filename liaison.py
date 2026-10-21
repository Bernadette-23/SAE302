def rechercher_feux_du_trajet(chemin, carrefours):
    feux_trouves = []

    for i in range(len(chemin) - 1):
        depart = chemin[i]
        arrivee = chemin[i + 1]

        position = depart + "-" + arrivee

        for carrefour in carrefours:
            feu = carrefour.rechercher_feu(position)

            if feu is not None and feu not in feux_trouves:
                feux_trouves.append(feu)

    return feux_trouves

def traiter_urgence(vehicule, depart, destination, routes, carrefours):

    chemin, cout = calculer_trajet_vehicule(
        vehicule, depart, destination, routes
    )

    if not chemin or cout == float("inf"):
        print("Aucun trajet possible.")
        return [], cout, []

    feux = rechercher_feux_du_trajet(chemin, carrefours)

    print("Feux trouvés sur le trajet :")
    for feu in feux:
        print(feu)

    # 3. Passer les feux trouvés au vert
    print("\nActivation des feux :")

    for feu in feux:
        feu.passer_au_vert()
        print(feu)

    # 4. Afficher le trajet
    print("\nTrajet :", " -> ".join(chemin))
    print("Coût total :", cout)

    # 5. Retourner les résultats
    return chemin, cout, feux

def terminer_urgence(feux):
    print("\nFin de la demande d'urgence :")

    for feu in feux:
        feu.passer_au_rouge()
        print(feu)


carrefours = [carrefourE, carrefourB, carrefourC, carrefourF]

chemin, cout, feux = traiter_urgence(
    ambulance, "A", "H", routes, carrefours
)

terminer_urgence(feux)
