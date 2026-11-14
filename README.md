# SAE302 – Développer une application communicante

## 1. Présentation du projet

Ce projet a été réalisé dans le cadre de la SAE 3.02.

Il consiste à simuler la gestion de carrefours connectés afin de faciliter le déplacement des véhicules d'urgence. L'application utilise une interface graphique Python, une communication client-serveur par sockets TCP et une base de données MariaDB permettant d'enregistrer les événements.

## 2. Membres du groupe

- **Nom du groupe :** BC Galactique
- **Étudiante 1 :** DAYA Chloé
- **Étudiante 2 :** LAFAGE Bernadette

## 3. Installation et déploiement

### 3.1. Prérequis

Le projet est déployé sur une machine virtuelle Debian.

Les outils nécessaires sont :
- Git
- Python 3
- pip
- venv
- PyQt6
- MariaDB

### 3.2. Installation des paquets

Ouvrir un terminal et passer en administrateur :

```bash
su 
```

Mettre à jour la liste des paquets :

```bash
apt update
```

Installer les outils nécessaires :

```bash
apt install git python3 python3-pip python3-venv
apt install python3-pyqt6
apt install mariadb-server
```

### 3.3. Récupération du projet

Revenir sur le compte utilisateur normal, puis cloner le dépôt GitHub :

```bash
git clone https://github.com/Bernadette-23/SAE302.git
```

Accéder au dossier du projet :

```bash
cd SAE302
```

### 3.4. Création de l'environnement virtuel

Créer l'environnement virtuel Python :

```bash
python3 -m venv venv
```

L'activer :

```bash
source venv/bin/activate
```

Mettre pip à jour :

```bash
python -m pip install --upgrade pip
```

Installer les dépendances du projet :

```bash
pip install -r requirements.txt
```

Vérifier les paquets installés :

```bash
pip list
```

### 3.5. Initialisation de la base de données

Vérifier que le service MariaDB fonctionne :

```bash
systemctl status mariadb
```

Importer le fichier SQL fourni avec le projet :

```bash
mariadb < database/sae302.sql
```

**Configuration :** vérifier les paramètres de connexion à la base de données dans `commun/base_donnees.py` (adresse IP, port, utilisateur, mot de passe et nom de la base).

## 4. Utilisation de l'application

L'application nécessite deux terminaux ouverts simultanément.

### 4.1. Démarrage du serveur

Dans un premier terminal, se placer à la racine du projet et activer l'environnement virtuel :

```bash
cd SAE302
source venv/bin/activate
```

Lancer le serveur :

```bash
python -m serveur.serveur
```

Le serveur est alors en attente de demandes des clients.

### 4.2. Démarrage de l'interface graphique

Dans un deuxième terminal, se placer à la racine du projet et activer l'environnement virtuel :

```bash
cd SAE302
source venv/bin/activate
```

Lancer l'application :

```bash
python main.py
```

L'interface graphique permet ensuite d'utiliser la simulation et d'envoyer des demandes de trajet pour les véhicules d'urgence.

### 4.3. Exemple d'utilisation de l'interface graphique

Une fois l'interface graphique ouverte et le serveur démarré, il est possible de simuler le trajet d'une ambulance en suivant les étapes ci-dessous.

#### Étape 1 : choisir le départ et la destination de l'ambulance

Dans la zone **Gestion des ambulances**, sélectionner le point de départ et le point d'arrivée à l'aide des deux menus déroulants.

![etape_1.png](etape_1.png)

#### Étape 2 : ajouter l'ambulance

Cliquer sur le bouton **« Ajouter une ambulance »**. L'ambulance sélectionnée est alors ajoutée à la liste des ambulances en attente de simulation.

![etape_2.png](etape_2.png)

#### Étape 3 : calculer le trajet et démarrer la simulation

Cliquer sur le bouton **« Calculer et démarrer »**. La demande est transmise au serveur, qui calcule le trajet. La simulation peut ensuite démarrer avec le trajet obtenu.

![etape_3.png](etape_3.png)




### 5. Arrêt de l'application

Fermer l'interface graphique.

Pour arrêter le serveur, revenir dans le terminal où il est lancé et utiliser `Ctrl + C`.

## 6. Arborescence du projet

```text
SAE302/
├── client/
│   ├── __init__.py
│   └── client.py
├── commun/
│   ├── __init__.py
│   ├── base_donnees.py
│   └── protocole.py
├── database/
│   └── sae302.sql
├── serveur/
│   ├── __init__.py
│   └── serveur.py
├── gestion_trajet.py
├── main.py
├── requirements.txt
└── README.md
```
