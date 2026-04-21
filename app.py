import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
app = Flask(__name__)
app.secret_key = 'vedetto_super_secret_key_2026' # Obligatoire pour utiliser les sessions
from datetime import datetime, timedelta
ADMIN_USER = "ramzi"
ADMIN_PASS = "vedetto2026"
RESERVATIONS_FILE = 'reservations.json'


def get_db_connection():
    conn = sqlite3.connect('vedetto.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS terrains (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY AUTOINCREMENT, terrain_id INTEGER, nom_client TEXT NOT NULL, telephone TEXT NOT NULL, date TEXT NOT NULL, heure TEXT NOT NULL, FOREIGN KEY (terrain_id) REFERENCES terrains (id))''')
    nb_terrains = cursor.execute('SELECT COUNT(*) FROM terrains').fetchone()[0]
    if nb_terrains == 0:
        cursor.execute("INSERT INTO terrains (nom) VALUES ('Terrain 1 - Synthétique')")
        cursor.execute("INSERT INTO terrains (nom) VALUES ('Terrain 2 - Synthétique')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def accueil():
    conn = get_db_connection()
    terrains = conn.execute('SELECT * FROM terrains').fetchall()
    conn.close()
    return render_template('index.html', terrains=terrains)

# NOUVEAU : La route qui reçoit les données du formulaire
@app.route('/reserver', methods=['POST'])
def reserver():
    nom_client = request.form['nom_client']
    telephone = request.form['telephone']
    terrain_id = request.form['terrain_id']
    date = request.form['date']
    heure = request.form['heure']

    conn = get_db_connection()
    
    # 1. VÉRIFICATION : Est-ce que le créneau est déjà pris ?
    deja_reserve = conn.execute(
        'SELECT * FROM reservations WHERE terrain_id = ? AND date = ? AND heure = ?', 
        (terrain_id, date, heure)
    ).fetchone()
    
    if deja_reserve:
        # SI OUI : On récupère les terrains et on recharge l'accueil avec un message d'erreur
        terrains = conn.execute('SELECT * FROM terrains').fetchall()
        conn.close()
        erreur_msg = "Désolé, ce terrain est déjà réservé à cette date et cette heure. Veuillez choisir un autre créneau."
        return render_template('index.html', terrains=terrains, erreur=erreur_msg)
    
    # 2. SI NON (c'est libre) : On enregistre la réservation
    conn.execute('INSERT INTO reservations (terrain_id, nom_client, telephone, date, heure) VALUES (?, ?, ?, ?, ?)',
                 (terrain_id, nom_client, telephone, date, heure))
    conn.commit()
    conn.close()

    # 3. On redirige vers une belle page de succès avec le nom du joueur
    return render_template('succes.html', nom=nom_client, date=date, heure=heure)

# --- NOUVEAU : API pour les disponibilités ---
# On définit les horaires d'ouverture de Ramzi (exemple : de 16h à 23h)
CRENEAUX = ['16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']

@app.route('/api/disponibilites')
def disponibilites():
    terrain_id = request.args.get('terrain_id')
    date = request.args.get('date')

    if not terrain_id or not date:
        return jsonify([]) # Si on n'a pas encore choisi de date/terrain, on renvoie du vide

    conn = get_db_connection()
    # On cherche les heures déjà réservées ce jour-là sur ce terrain
    reservations = conn.execute(
        'SELECT heure FROM reservations WHERE terrain_id = ? AND date = ?', 
        (terrain_id, date)
    ).fetchall()
    conn.close()

    # On transforme ça en une liste simple d'heures (ex: ['18:00', '20:00'])
    heures_reservees = [res['heure'] for res in reservations]

    # La magie : On garde uniquement les créneaux qui NE SONT PAS dans les heures réservées
    heures_dispos = [h for h in CRENEAUX if h not in heures_reservees]

    # MODIFICATION ICI : On renvoie les heures réservées pour que le JavaScript les mette en rouge,
    # tout en gardant la variable heures_dispos juste au-dessus !
    return jsonify(heures_reservees)

# --- ROUTE DE CONNEXION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            erreur = "Identifiants incorrects. Veuillez réessayer."
            
    return render_template('login.html', erreur=erreur)

# --- ROUTE DU TABLEAU DE BORD (SÉCURISÉE) ---
from datetime import date # Ajoute cet import en haut du fichier







from datetime import date # Assure-toi que c'est bien présent en haut du fichier

from datetime import datetime, date

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    aujourdhui_str = date.today().isoformat()
    # Nettoyage automatique des dates anciennes
    conn.execute("DELETE FROM reservations WHERE date < ?", (aujourdhui_str,))
    conn.commit()

    reservations_db = conn.execute('SELECT * FROM reservations').fetchall()
    reservations = [dict(row) for row in reservations_db]
    conn.close()
    
    # --- LA MAGIE DES SEMAINES EST ICI ---
    # 1. On regarde si on a cliqué sur "Semaine Suivante" (week=1, week=2...)
    week_offset = int(request.args.get('week', 0))
    
    # 2. On calcule la date du Lundi et du Dimanche de la semaine affichée
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # 3. On filtre le planning
    planning_data = {i: {} for i in range(7)} 
    for res in reservations:
        try:
            date_obj = datetime.strptime(res['date'], '%Y-%m-%d').date()
            
            # LE CORRECTIF : On vérifie que la date est BIEN dans la semaine qu'on regarde !
            if start_of_week <= date_obj <= end_of_week:
                jour_index = date_obj.weekday() # 0=Lundi, 6=Dimanche
                h = res['heure']
                if h not in planning_data[jour_index]:
                    planning_data[jour_index][h] = []
                planning_data[jour_index][h].append(res)
        except: continue

    res_aujourdhui = [r for r in reservations if r['date'] == aujourdhui_str]
    reservations_avec_index = [(res['id'], res) for res in reservations]
    reservations_avec_index.reverse() 

    # On formate les dates pour les afficher joliment (ex: 16/04/2026)
    start_str = start_of_week.strftime("%d/%m/%Y")
    end_str = end_of_week.strftime("%d/%m/%Y")

    return render_template('admin.html', 
                           reservations=reservations_avec_index, 
                           total=len(reservations), 
                           today_count=len(res_aujourdhui),
                           planning=planning_data,
                           week_offset=week_offset, # <--- Nouveau
                           start_week=start_str,    # <--- Nouveau
                           end_week=end_str)        # <--- Nouveau

# --- ROUTE POUR SE DÉCONNECTER ---
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# --- ROUTE POUR SUPPRIMER UNE RÉSERVATION ---
@app.route('/admin/delete/<int:index>')
def delete_reservation(index):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    # MODIFICATION : Ton ancien code JSON est conservé mais désactivé
    # if os.path.exists(RESERVATIONS_FILE):
    #     with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
    #         reservations = json.load(f)
    #     
    #     # On supprime l'élément (attention, l'index doit correspondre à la liste inversée ou originale)
    #     # Ici on travaille sur la liste originale
    #     if 0 <= index < len(reservations):
    #         reservations.pop(index)
    #         
    #         with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
    #             json.dump(reservations, f, indent=4, ensure_ascii=False)
                
    # MODIFICATION : Nouveau code qui supprime dans la base de données SQLite
    conn = get_db_connection()
    conn.execute('DELETE FROM reservations WHERE id = ?', (index,))
    conn.commit()
    conn.close()
                
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)