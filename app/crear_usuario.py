import bcrypt
from app.database import SessionLocal, Usuario, inicializar_base_datos

def registrar_usuario(username, password):
    # Asegurar que las tablas existan
    inicializar_base_datos()
    
    db = SessionLocal()
    try:
        # 1. Verificar si el usuario ya existe
        usuario_existente = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario_existente:
            print(f"❌ Error: El usuario '{username}' ya está registrado.")
            return

        # 2. Encriptar la contraseña con bcrypt
        # Generamos la sal (salt) y hasheamos la contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Convertimos el hash a string para guardarlo en la base de datos
        password_hash_str = hashed_password.decode('utf-8')

        # 3. Crear el nuevo registro
        nuevo_usuario = Usuario(username=username, password_hash=password_hash_str)
        db.add(nuevo_usuario)
        db.commit()
        
        print(f"✅ ¡Usuario '{username}' creado con éxito en MySQL!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ocurrió un error al registrar el usuario: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- Creador de Usuarios para Streamlit ---")
    # Puedes cambiar estos valores por el usuario y contraseña que quieras
    nuevo_user = input("Introduce el nombre de usuario: ")
    nueva_pass = input("Introduce la contraseña: ")
    
    if nuevo_user and nueva_pass:
        registrar_usuario(nuevo_user, nueva_pass)
    else:
        print("❌ El usuario y la contraseña no pueden estar vacíos.")

