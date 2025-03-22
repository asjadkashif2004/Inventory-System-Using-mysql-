from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3307  # XAMPP's default
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store data into database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html', user=user)
            
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

# ---------------- CRUD Operations for Products ----------------

@app.route('/products')
def products():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO products (name, price, category, stock) VALUES (%s, %s, %s, %s)", (name, price, category, stock))
        mysql.connection.commit()
        cursor.close()

        flash("Product added successfully!")
        return redirect(url_for('products'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        stock = request.form['stock']

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE products SET name=%s, price=%s, category=%s, stock=%s WHERE id=%s",
                       (name, price, category, stock, id))
        mysql.connection.commit()
        cursor.close()

        flash("Product updated successfully!")
        return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()

    flash("Product deleted successfully!")
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)
