from flask import Flask, url_for, render_template, request, flash, redirect, abort, session
from werkzeug.security import generate_password_hash, check_password_hash
from sendcode import envoicode
from datetime import datetime
import os
import requests
import random
import pyodbc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clés_flash'
DSN = 'Driver={SQL Server};Server=Impish_Boy;Database=OptimalMedical;'


@app.route('/monhopital')
def monhopital():
    if 'username' in session:
        lien=session.get('lien')
        idinformation=session.get('idinformation')
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT * FROM Nomservices 
        ''')
        nomservices = cursor.fetchall()

        cursor.execute('''
        SELECT * FROM commune 
        ''')
        communes = cursor.fetchall()

        cursor.execute('''
        SELECT * FROM region 
        ''')
        regions = cursor.fetchall()

        cursor.execute('''
        SELECT * FROM departement 
        ''')
        departements = cursor.fetchall()

        cursor.execute('''
        SELECT * FROM EtatPatient 
        ''')
        etats = cursor.fetchall()
        
        cursor.execute('''
                SELECT Services.idservice, Services.Nombreplace, NomServices.NomService,Services.placedisponible,
                Services.attente
                FROM services
                INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                where IdInformation = ?
                ''', idinformation)
        services = cursor.fetchall()
        conn.close()
        
        return render_template("./utilisateur/utilisateurhopital.html", etats=etats, nomservices=nomservices,
                               communes=communes, regions=regions, departements=departements, lien=lien,
                               services=services)
    else:
        return redirect(url_for('accueil'))


@app.route('/plus/<idservice>')    
def plus(idservice):
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM services 
        where idService= ?
        ''', idservice)
    services = cursor.fetchone()
    if services[2] > services[3]:
        ch = services[3]+1
        cursor.execute("UPDATE services SET placedisponible = ? WHERE idservice = ?", (ch, idservice))
        conn.commit()
        return redirect(url_for('monhopital'))
    else:
        ch = services[4]+1
        cursor.execute("UPDATE services SET attente = ? WHERE idservice = ?", (ch, idservice))
        conn.commit()
        return redirect(url_for('monhopital'))


@app.route('/moins/<idservice>')    
def moins(idservice):
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM services 
        where idService= ?
        ''', idservice)
    services = cursor.fetchone()
    if services[4] > 0:
        ch = services[4]-1
        cursor.execute("UPDATE services SET attente = ? WHERE idservice = ?", (ch, idservice))
        conn.commit()
        return redirect(url_for('monhopital'))
    elif services[3] > 0:
        ch = services[3]-1
        cursor.execute("UPDATE services SET placedisponible = ? WHERE idservice = ?", (ch, idservice))
        conn.commit()
        return redirect(url_for('monhopital'))
    else:
        return redirect(url_for('monhopital'))


@app.route('/transfertECR')
def transfertECR():
    lien = session.get('lien')
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM Nomservices 
    ''')
    services = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM commune 
    ''')
    communes = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM region 
    ''')
    regions = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM departement 
    ''')
    departements = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM EtatPatient 
    ''')
    etats = cursor.fetchall()
    conn.close()
    return render_template("./utilisateur/transfertECR.html", etats=etats, services=services, communes=communes,
                           regions=regions, departements=departements, lien=lien)


@app.route('/transferteffectué')
def transferteffectué():
    idinformation = session.get('idinformation')
    lien = session.get('lien')
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM Nomservices 
    ''')
    nomservices = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM commune 
    ''')
    communes = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM region 
    ''')
    regions = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM departement 
    ''')
    departements = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM EtatPatient 
    ''')
    etats = cursor.fetchall()
    
    cursor.execute('''
                SELECT Services.idservice, Services.Nombreplace, NomServices.NomService,Services.placedisponible,
                Services.attente
                FROM services
                INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                where IdInformation = ?
                ''', idinformation)
    services = cursor.fetchall()
    conn.close()
    return render_template("./utilisateur/transferteffectué.html", etats=etats, nomservices=nomservices,
                           communes=communes, regions=regions, departements=departements, services=services,
                           lien=lien)


@app.route('/transfert', methods=["GET", "POST"])
def transfert():
    lien = session.get('lien')
    idinformation = 2   # session.get('idinformation')
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM Nomservices 
    ''')
    nomservices = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM commune 
    ''')
    communes = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM region 
    ''')
    regions = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM departement 
    ''')
    departements = cursor.fetchall()
    
    cursor.execute('''
    SELECT * FROM informations
    where IdInformation != ?
    ''', idinformation)
    departements = cursor.fetchall()
    
    cursor.execute('''
                SELECT Services.idservice, Services.Nombreplace, NomServices.NomService, Services.placedisponible, 
                Services.attente
                FROM services
                INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                where IdInformation != ?
                ''', idinformation)
    services = cursor.fetchall()
    conn.close()

    return render_template("./utilisateur/utilisateurtransfert.html", nomservices=nomservices,
                           communes=communes, regions=regions, services=services, departements=departements, lien=lien)


@app.route('/validertransfert', methods=['POST'])
def validertransfert():
    selected_index = int(request.form['selectedService'])
    lien = session.get('lien')
    idinformation = 2  # session.get('idinformation')
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM EtatPatient
    ''')
    etatpatient = cursor.fetchall()
    
    cursor.execute('''
                SELECT Services.idservice, NomServices.NomService, users.NomUtilisateur
                FROM services
                INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                INNER JOIN NomUtilisateur ON Users.IdInformation = Services.IdInformation 
                where IdInformation != ?
                ''', idinformation)
    services = cursor.fetchall()
    transf = services[selected_index]
    if request.method == "POST": 
        tel = request.form['Tel']
        date = datetime.now().strftime("%Y-%m-%d"' '"%H:%M:%S")
    
    return render_template("./utilisateur/confirmetransfert.html", transf=transf, lien=lien, etatpatient=etatpatient)


@app.route('/monprofil')
def monprofil():

    return render_template("./utilisateur/utilisateurprofil.html")


@app.route('/inscriptioninfos', methods=["GET", "POST"])
def inscriptioninfos():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Region")
    Region = cursor.fetchall()
    cursor.execute("SELECT * FROM Departement")
    Departement = cursor.fetchall()
    cursor.execute("SELECT * FROM Commune")
    Commune = cursor.fetchall()
    conn.close()
    if request.method == "POST": 
        
        conn = pyodbc.connect(DSN) 
        cursor = conn.cursor() 
        
        nom = request.form['Nom'] 
        num = request.form['Num'] 
        tel = request.form['Tel']
        
        cursor.execute(''' SELECT * FROM Informations 
                            WHERE Nom = ?
                            ''', nom)
        a = cursor.fetchone()
        cursor.execute(''' SELECT * FROM Informations 
                            WHERE Matricule = ?
                            ''', num)
        b = cursor.fetchone()
        cursor.execute(''' SELECT * FROM Informations 
                            WHERE Telephone = ?
                            ''', tel)
        c = cursor.fetchone()
        if a:
            flash("Ce nom exist déjà!", 'info')
    
        elif b:
            flash("Matricule déjà existant!", 'info')
            
        elif c:
            flash(" déjà existant!", 'info')
            
        else:
            nCommune = request.form['selected_value3']
            ndepartement = request.form['selected_value2'] 
            nregion = request.form['selected_value1'] 
            if nCommune == 'option':
                flash("veillez choisir une commune!", 'info')
            elif ndepartement == 'option':
                flash("veillez choisir un departement!", 'info')
            elif nregion == 'option':
                flash("veillez choisir une region!", 'info')
            else:
                image = request.files['logo']
                if image.filename == '':
                    flash("Aucun fichier sélectionné !", 'info')
                else:
                    url = f'static/img/{nom}/'
                    if not os.path.exists(url):
                        os.makedirs(url)
                    image.save(url + image.filename)
                    
                    try:
                        response = requests.get('https://ipinfo.io/json')
                        data = response.json()
                        coordinates = data['loc'].split(',')
                        latitude = coordinates[0]
                        longitude = coordinates[1]
                    except Exception as e:
                        latitude = None
                        longitude = None
                        
                    localisation = latitude+' '+longitude
                    idadresse = tel[-10:]
                    cursor.execute('''insert into Adresses (idadresse,idCommune, idDepartement, idRegion,positiongeo) 
                                values(?,?,?,?,?)''', (idadresse, nCommune, ndepartement, nregion, localisation))
                    conn.commit() 
                    
                    cursor.execute('''INSERT INTO Informations (Nom, Matricule, Telephone, idadresse,lienimg)
                                VALUES (?, ?, ?,?,?)''', (nom, num, tel, idadresse, url + image.filename))
                    conn.commit()
                    
                    cursor.execute(''' SELECT * FROM Informations 
                                        WHERE Matricule = ?
                                        ''', num)
                    idinformation = cursor.fetchone()
                    session['idinformation'] = idinformation[0]
                    conn.close()
                    return redirect(url_for('listeservice'))
    return render_template("./inscription/inscriptioninfos.html", Region=Region,
                           Departement=Departement, Commune=Commune)


@app.route('/ListeService', methods=["GET", "POST"])
def listeservice():
    idiformation = session.get('idinformation')
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor()  
    cursor.execute("""
                SELECT Services.idservice, Services.Nombreplace, NomServices.NomService
                FROM services
                INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                WHERE IdInformation = ?
            """, idiformation)
    services = cursor.fetchall()
    conn.close()
    return render_template("./inscription/inscriptionservice.html ", services=services)


@app.route('/AjoutService', methods=["GET", "POST"])
def ajoutservice():
    conn = pyodbc.connect(DSN)
    cursor = conn.cursor() 
    cursor.execute('''
    SELECT * FROM Nomservices 
    ''')
    services = cursor.fetchall()
    if request.method == "POST":
        idinformation = session.get('idinformation')
        service = request.form['selected_value']
        capacite = request.form['capacite'] 
        disponible = 0
        attente = 0
        cursor.execute('''INSERT INTO services (idnomservice, Nombreplace, placedisponible, attente, idinformation)
                       VALUES (?, ?, ?, ?, ?)''', (service, capacite, disponible, attente, idinformation))
        conn.commit() 
        conn.close()
        return redirect(url_for('listeservice'))
    return render_template("./inscription/inscriptionservice0.html ", services=services)


@app.route('/inscriptionacces', methods=["GET", "POST"])
def inscriptionacces():
    if request.method == 'POST':
        idinformation = session.get('idinformation')
        user = request.form["username"]
        mail = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        
        cursor.execute(''' SELECT * FROM users 
                            WHERE NomUtilisateur = ?
                            ''', user)
        b = cursor.fetchone()
        
        cursor.execute(''' SELECT * FROM users 
                            WHERE email = ?
                            ''', mail)
        c = cursor.fetchone()
        
        if b:
            flash("NomUtilisateur déjà existant!", 'alert')
            
        elif c:
            flash("Email déjà existant!", 'alert')
        
        else:
            if len(password) < 8:
                flash("le mot de passe doit être superieur ou égal à 8 caractère!", 'alert')
            elif password != password1:
                flash("Repétez le même mot de passe!", 'alert')
            else:
                categorie = 'Attente'
                cursor.execute('''INSERT INTO users (nomutilisateur, email, password,idinformation,categorie)
                            VALUES (?, ?, ?,?,?)''', (user, mail, generate_password_hash(password),
                                                      idinformation, categorie))
                conn.commit() 
                conn.close()
                return redirect(url_for('connexion'))
    return render_template("./inscription/inscriptionacces.html")

#     connexion


@app.route("/", methods=["GET", "POST"])
def accueil():
    if 'username' in session:
        if session['username'] == 'admin':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for("monhopital"))
    return redirect(url_for('connexion'))


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == 'POST':
        user = request.form["identifiant"]
        password = request.form["password"]
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM Users 
        WHERE NomUtilisateur = ? OR email = ?
        ''', (user, user))
        user = cursor.fetchone()
        if user:
            pswd = user[3]
            if check_password_hash(pswd, password):
                cursor.execute('''
                            SELECT * FROM informations 
                            WHERE idinformation = ? 
                            ''', (user[4]))
                lien = cursor.fetchone()
                lien = lien[5][6:]
                session['loggedin'] = True
                session['username'] = user[1]
                session['lien'] = lien
                session['idinformation'] = user[4]
                return redirect(url_for('accueil'))
            else:
                flash("Mot de passe incorrect !", 'info')
        else:
            flash("Identifiant incorrect !", 'info')
    return render_template("./connexion/connexion.html")



@app.route('/pwdoublie', methods=["GET", "POST"])
def pwdoublie():
    if request.method == 'POST':
        user = request.form["text"]
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM Users 
        WHERE NomUtilisateur = ? OR Email = ?
        ''', (user, user))
        users = cursor.fetchone()
        conn.close()
        if users:
            code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            session['code'] = code
            session['email'] = users[2]
            envoicode(code, users[2])
            return redirect(url_for('pwdcode'))
        else:
            flash('le mail ou le nom d\'utilisateur n\'existe pas')
    return render_template("./connexion/pwdoublie.html")


@app.route('/pwdcode', methods=["GET", "POST"])
def pwdcode():
    code = session.get('code')
    if not code:
        flash('Code introuvable, veuillez demander un nouveau code')
        return redirect(url_for('pwdoublie'))
    if request.method == 'POST':
        codesaisir = request.form["code"]
        if codesaisir == code:
            return redirect(url_for('pwdreset'))
        else:
            flash('veillez saisir le bon code de validation')
    return render_template("./connexion/pwdcode.html")


@app.route('/pwdreset', methods=["GET", "POST"])
def pwdreset():
    email = session.get('email')
    if request.method == 'POST':
        password = request.form["password"]
        password1 = request.form["password"]
        if password1 == password:
            password = generate_password_hash(password)
            conn = pyodbc.connect(DSN)
            cursor = conn.cursor()
            cursor.execute(f'''
                        UPDATE users
                        SET Password = ?
                        WHERE  Email = ?
                        ''', (password, email))
            conn.commit()
            conn.close()
            flash('votre mot de passe à bien été modifié, connectez vous')
            return redirect(url_for('connexion'))
        else:
            flash('veillez saisir le même mot de passe dans les deux champs')
    return render_template("./connexion/pwdreset.html")

# ................yesufu route (Admin)#


@app.route('/admin')
def admin():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute(""" SELECT * FROM Informations """)
        inscrit = cursor.fetchall()
        nbrinscrit = len(inscrit)
        cursor.execute(""" SELECT * FROM Transfert """)
        transfert = cursor.fetchall()
        nbrtransfert = len(transfert)
        cursor.execute(""" SELECT * FROM Reclamation """)
        reclamation = cursor.fetchall()
        nbrreclamation = len(reclamation)
        cursor.execute(""" SELECT TOP 5 *
                        FROM Informations
                        ORDER BY IdInformation DESC """)
        inscritrec = cursor.fetchall()

        conn.close()
        return render_template("./admin/admin.html", nbrinscrit=nbrinscrit, nbrtransfert=nbrtransfert,
                               nbrreclamation=nbrreclamation, inscritrec=inscritrec)
    return redirect(url_for('connexion'))


@app.route('/historique')
def historique():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT InfoDep.Nom, InfoDes.Nom, NomServices.NomService, EtatPatient.Etat, Transfert.Dateheure
                    FROM Transfert 
                    INNER JOIN Users AS UsersDep ON Transfert.IdUserDep = UsersDep.IdUser
                    INNER JOIN Users AS UsersDes ON Transfert.IdUserDes = UsersDes.IdUser
                    INNER JOIN Informations AS InfoDep ON UsersDep.IdInformation = InfoDep.IdInformation
                    INNER JOIN Informations AS InfoDes ON UsersDes.IdInformation = InfoDes.IdInformation
                    INNER JOIN Services ON Transfert.IdNomService = Services.IdNomService
                    INNER JOIN NomServices ON NomServices.IdNomServices = Services.IdNomService
                    INNER JOIN EtatPatient ON Transfert.IdEtatPatient = EtatPatient.IdEtatPatient
                """)
        data = cursor.fetchall()
        conn.close()
        return render_template("./admin/historiqueadmin.html", data=data)
    return redirect(url_for('connexion'))


@app.route('/demande')
def demande():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Informations.Matricule, Informations.Nom, Users.email, Commune.NomCommune, Departement.NomDepartement
            , Region.NomRegion, Informations.Telephone
            FROM Informations, Users, Adresses, Commune, Departement, Region
            WHERE Informations.IdInformation = Users.IdInformation AND Informations.IdAdresse = Adresses.IdAdresse
            AND Adresses.IdCommune = Commune.IdCommune
            AND Adresses.IdDepartement = Departement.IdDepartement
            AND Adresses.IdRegion = Region.IdRegion
        """)
        data = cursor.fetchall()
        conn.close()
        return render_template("./admin/demandeadmin.html", data=data)
    return redirect(url_for('connexion'))


@app.route('/listeinscrit')
def listeinscrit():
    return render_template("./admin/listeinscrit.html")


@app.route("/deconnexion")
def deconnexion():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('connexion'))


# ................Fin yesufu route (Admin)#


if __name__ == "__main__":
    app.run(debug=True)
