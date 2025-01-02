from flask import Flask, request, jsonify
from flask_cors import CORS
import pypyodbc as odbc

app = Flask(__name__)
CORS(app)  # Asigură că toate răspunsurile includ header-ele CORS necesare

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

    if check_login(username, password):
        return jsonify({"message": "Autentificare reușită!"})
    else:
        return jsonify({"message": "Username sau parola incorecte"}), 401

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

        # Obține cel mai mare ClientID și generează următorul
        cursor.execute("SELECT ISNULL(MAX(ClientID), 0) + 1 FROM Utilizatori")
        next_client_id = cursor.fetchone()[0]

        # Inserează utilizatorul nou
        query = "INSERT INTO Utilizatori (ClientID, Username, Password) VALUES (?, ?, ?)"
        cursor.execute(query, (next_client_id, username, password))
        conn.commit()

        return jsonify({"message": "Utilizator înregistrat cu succes"}), 201

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
