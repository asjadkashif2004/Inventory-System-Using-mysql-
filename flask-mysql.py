from flask import Flask 
from flask_mysqldb import MySQL
app = Flask(__name__)

# Correct MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskapp'  # Your actual database name
app.config['MYSQL_PORT'] = 3307  # Add this line for the custom port

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM user')  # Ensure 'users' table exists
    data = cur.fetchall()
    cur.close()
    return str(data)

if __name__ == '__main__':
    app.run(debug=True)
