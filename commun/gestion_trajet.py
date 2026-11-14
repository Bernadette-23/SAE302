"""
Module contenant le graphe des intersections et l'algorithme
permettant de calculer le trajet le plus court entre deux points.
"""

# Représentation du réseau routier sous forme de graphe.
# Chaque intersection est un nœud et chaque route indique un voisin
# ainsi que le coût associé au déplacement entre les deux intersections.
routes = {
    "A": [("B", 5)],
    "B": [("A", 5), ("C", 4), ("D", 6), ("E", 3)],
    "C": [("B", 4), ("F", 2), ("J", 5)],
    "D": [("B", 6)],
    "E": [("B", 3), ("F", 5), ("G", 2), ("H", 6)],
    "F": [("E", 5), ("I", 5), ("C", 2)],
    "G": [("E", 2)],
    "H": [("E", 6)],
    "I": [("F", 5)],
    "J": [("C", 5)]
}


def dijkstra(graphe, depart, destination):
    """
    Calcule le trajet de coût minimal entre deux intersections à partir
    d'un graphe pondéré et retourne le chemin ainsi que son coût total.
    """
    # Vérification de l'existence des intersections dans le graphe
    if depart not in graphe or destination not in graphe:
        return [], float("inf")

    # Initialisation des distances et des prédécesseurs de chaque nœud
    distances = {n: float("inf") for n in graphe}
    precedents = {n: None for n in graphe}
    visites = []

    # Le coût pour atteindre le point de départ est nul
    distances[depart] = 0

    # Parcours du graphe jusqu'à ce que tous les nœuds soient visités
    while len(visites) < len(graphe):
        noeud = None

        # Recherche du nœud non visité ayant la distance la plus faible
        for candidat in graphe:
            if candidat not in visites:
                if noeud is None or distances[candidat] < distances[noeud]:
                    noeud = candidat

        # Arrêt si aucun nœud accessible ne reste à visiter
        if noeud is None or distances[noeud] == float("inf"):
            break

        visites.append(noeud)

        # Mise à jour des distances des intersections voisines
        for voisin, cout in graphe[noeud]:
            nouvelle_distance = distances[noeud] + cout

            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = noeud

    # Vérification de l'accessibilité de la destination
    if distances[destination] == float("inf"):
        return [], float("inf")

    # Reconstruction du chemin à partir des prédécesseurs
    chemin = []
    noeud = destination

    while noeud is not None:
        chemin.append(noeud)
        noeud = precedents[noeud]

    # Inversion pour obtenir le chemin dans le sens départ-destination
    chemin.reverse()

    return chemin, distances[destination]