from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

password_plano = "mi_contraseña_secreta" 
hashed_password = bcrypt.generate_password_hash(password_plano).decode('utf-8')
print("Contraseña Hasheada:", hashed_password)