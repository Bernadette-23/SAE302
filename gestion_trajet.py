
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
    if depart not in graphe or destination not in graphe:
        return [], float("inf")

    distances = {n: float("inf") for n in graphe}
    precedents = {n: None for n in graphe}
    visites = []

    distances[depart] = 0

    while len(visites) < len(graphe):
        noeud = None

        for candidat in graphe:
            if candidat not in visites:
                if noeud is None or distances[candidat] < distances[noeud]:
                    noeud = candidat

        if noeud is None or distances[noeud] == float("inf"):
            break

        visites.append(noeud)

        for voisin, cout in graphe[noeud]:
            nouvelle_distance = distances[noeud] + cout

            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = noeud

    if distances[destination] == float("inf"):
        return [], float("inf")

    chemin = []
    noeud = destination

    while noeud is not None:
        chemin.append(noeud)
        noeud = precedents[noeud]

    chemin.reverse()

    return chemin, distances[destination]
