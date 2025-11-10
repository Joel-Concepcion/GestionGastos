from werkzeug.security import generate_password_hash, check_password_hash

texto = "x?1_p-M.4!eM"

texto_encriptado = generate_password_hash(texto)
print(f"texto encriptado: {texto_encriptado}")

print(f"¿el texto es corecto? {check_password_hash(texto_encriptado, texto)}")