from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pypyodbc as odbc

app = Flask(__name__)
app.secret_key = 'alabalaportocala'  # Înlocuiește cu o cheie secretă sigură
CORS(app, supports_credentials=True)


# Configurarea conexiunii la baza de date
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'DESKTOP-E3R755C\\SQLEXPRESS'  # Înlocuiește cu serverul tău
DATABASE_NAME = 'RezervariBilete'  # Înlocuiește cu baza de date dorită

connection_string = f"""
    DRIVER={{SQL Server}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

def check_login(username, password):
    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()
        query = "SELECT Password FROM Utilizatori WHERE Username = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        
        if row and row[0] == password:
            return True
        else:
            return False
    
    except Exception as e:
        print("Eroare la autentificare:", e)
        return False
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        # Verifică username și password
        query = "SELECT ClientID, Password FROM Utilizatori WHERE Username = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row and row[1] == password:
            session['username'] = username
            session['client_id'] = row[0]  # Salvează ClientID în sesiune
            return jsonify({"message": "Autentificare reușită!"}), 200
        else:
            return jsonify({"message": "Username sau parola incorecte"}), 401
    except Exception as e:
        print("Eroare la autentificare:", e)
        return jsonify({"message": "Eroare la autentificare"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        # Verifică dacă utilizatorul există deja
        cursor.execute("SELECT COUNT(*) FROM Utilizatori WHERE Username = ?", (username,))
        user_exists = cursor.fetchone()[0]
        if user_exists:
            return jsonify({"message": "Utilizatorul există deja."}), 409

        # Creează o înregistrare nouă în tabelul Client
        cursor.execute("INSERT INTO Client DEFAULT VALUES")

        # Obține ClientID generat automat
        cursor.execute("SELECT SCOPE_IDENTITY()")
        new_client_id = cursor.fetchone()[0]

        if not new_client_id:
            raise Exception("Nu s-a generat un ClientID.")

        # Creează o înregistrare în tabelul Utilizatori folosind ClientID generat
        cursor.execute(
            "INSERT INTO Utilizatori (ClientID, Username, Password) VALUES (?, ?, ?)",
            (new_client_id, username, password)
        )

        # Confirmă modificările în baza de date
        conn.commit()

        return jsonify({"message": "Client și utilizator înregistrați cu succes"}), 201

    except Exception as e:
        print("Eroare la înregistrare:", e)
        return jsonify({"message": str(e)}), 400

    finally:
        cursor.close()
        conn.close()


@app.route('/spectacole', methods=['GET'])
def get_spectacole():
    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()
        query = """
        SELECT 
            s.SpectacolID,
            s.Nume_spectacol,
            s.Tip_spectacol,
            sala.Nume_sala,
            sala.Capacitate,
            sala.Tip_sala,
            ds.Ziua_spectacolului,
            ds.Data,
            ds.Ora
        FROM Spectacol s
        JOIN Sala sala ON s.SalaID = sala.SalaID
        JOIN Detalii_Spectacol ds ON s.SpectacolID = ds.SpectacolID
        """
        cursor.execute(query)
        spectacole = cursor.fetchall()
    except Exception as e:
        print("Eroare la obținerea spectacolelor:", e)
        return jsonify({"message": "Eroare la obținerea spectacolelor"}), 500
    finally:
        cursor.close()
        conn.close()

    # Transformăm datele într-un format JSON-friendly
    spectacole_data = [
        {
            'SpectacolID': spectacol[0],
            'Nume_spectacol': spectacol[1],
            'Tip_spectacol': spectacol[2],
            'Nume_sala': spectacol[3],
            'Capacitate': spectacol[4],
            'Tip_sala': spectacol[5],
            'Ziua_spectacolului': spectacol[6],
            'Data': spectacol[7],
            'Ora': spectacol[8]
        }
        for spectacol in spectacole
    ]

    return jsonify(spectacole_data)

@app.route('/user-details', methods=['GET'])
def get_user_details():
    # Simulează obținerea detaliilor utilizatorului autentificat
    username = "denisa.badara"  # Trebuie să fie legat de sesiune
    password = "denisa"

    return jsonify({"username": username, "password": password})


@app.route('/update-user', methods=['POST'])
def update_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Adaugă logica pentru identificarea utilizatorului conectat
    client_id = 1  # Exemplu: obține ID-ul utilizatorului conectat (trebuie adaptat)

    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        # Actualizează detaliile utilizatorului în baza de date
        query = "UPDATE Utilizatori SET Username = ?, Password = ? WHERE ClientID = ?"
        cursor.execute(query, (username, password, client_id))

        conn.commit()
        return jsonify({"message": "Detaliile au fost actualizate cu succes"}), 200

    except Exception as e:
        print("Eroare la actualizare:", e)
        return jsonify({"message": "Eroare la actualizare"}), 400

    finally:
        cursor.close()
        conn.close()


@app.route('/rezervare', methods=['POST'])
def rezervare():
    data = request.json
    spectacol_id = data.get('spectacolId')
    nume = data.get('nume')
    prenume = data.get('prenume')
    numar_telefon = data.get('numar_telefon')
    email = data.get('email')
    cantitate_bilete = data.get('cantitate_bilete')

    # Obține ClientID-ul utilizatorului conectat
    client_id = session.get('client_id')  # ClientID ar trebui salvat în sesiune la login
    if not client_id:
        return jsonify({"message": "Utilizator neautentificat"}), 401

    try:
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        # Actualizează informațiile clientului
        update_client_query = """
            UPDATE Client
            SET Nume = ?, Prenume = ?, Numar_telefon = ?, Email = ?
            WHERE ClientID = ?
        """
        cursor.execute(update_client_query, (nume, prenume, numar_telefon, email, client_id))

        # Inserează rezervarea în tabelul `Rezervare`
        rezervare_query = """
            INSERT INTO Rezervare (ClientID, SpectacolID, Data_rezervare, Ora_rezervare)
            VALUES (?, ?, CAST(GETDATE() AS DATE), CURRENT_TIMESTAMP)
        """
        cursor.execute(rezervare_query, (client_id, spectacol_id))
        
        # Confirmă modificările în baza de date
        conn.commit()

        return jsonify({"message": "Rezervare realizată cu succes"}), 201

    except Exception as e:
        print("Eroare la rezervare:", e)
        return jsonify({"message": "Eroare la rezervare"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
