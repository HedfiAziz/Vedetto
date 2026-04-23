# ⚽ Complexe Sportif VEDETTO - Système de Réservation

![Vedetto Banner](https://images.unsplash.com/photo-1551958219-acbc608c6377?q=80&w=1200&auto=format&fit=crop)

Une plateforme web complète et responsive (optimisée pour mobile) permettant de gérer les réservations de terrains de football pour le **Complexe Sportif VEDETTO** situé à Fouchana, Tunisie. 

L'application est divisée en deux parties : une interface client pour la réservation rapide et un tableau de bord administrateur sécurisé pour la gestion du planning.

---

## ✨ Fonctionnalités

### 👤 Côté Client
* **Réservation en ligne facile :** Formulaire intuitif pour réserver un créneau en quelques secondes.
* **Disponibilités en temps réel :** Affichage dynamique des heures disponibles selon le terrain et la date choisis.
* **Interface Responsive :** Design moderne et fluide, parfaitement adapté aux smartphones et ordinateurs.
* **Lien Direct WhatsApp :** Bouton pour contacter rapidement l'administration.

### 🛡️ Côté Administrateur
* **Tableau de bord (Dashboard) :** Statistiques globales (réservations du jour, total).
* **Planning Hebdomadaire Dynamique :** Vue visuelle claire des matchs prévus sur toute la semaine pour les différents terrains.
* **Gestion des réservations :** Liste détaillée avec option de recherche, filtre par client/téléphone, et possibilité de supprimer des créneaux.
* **Sécurité :** Accès protégé par mot de passe.

---

## 🛠️ Technologies Utilisées

* **Backend :** Python, Flask
* **Base de données :** SQLite (`vedetto.db`)
* **Frontend :** HTML5, CSS3 (Custom responsive design), Vanilla JavaScript
* **Bibliothèques externes :** * [Flatpickr](https://flatpickr.js.org/) (Sélection de dates)
  * [FontAwesome](https://fontawesome.com/) (Icônes)
* **Hébergement :** Déployé en continu via [Render](https://render.com/)

---

## 📂 Structure du Projet

```text
Vedetto/
│
├── app.py                 # Script principal (Backend Flask)
├── vedetto.db             # Base de données SQLite (générée automatiquement)
├── requirements.txt       # Liste des dépendances Python
│
├── templates/             # Fichiers HTML
│   ├── index.html         # Page d'accueil et réservation client
│   ├── admin.html         # Tableau de bord administrateur
│   ├── login.html         # Page de connexion admin
│   └── succes.html        # Page de confirmation de réservation
│
└── static/                # Fichiers statiques
    ├── style.css          # Feuille de style principale
    └── image/
        └── logo.png       # Logo officiel du complexe
