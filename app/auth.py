import bcrypt
from database import SessionLocal, Usuario


def verificar_usuario(username: str, password: str) -> bool:
    if not username or not password:
        return False
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.username == username).first()
        if usuario is None:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), usuario.password_hash.encode("utf-8")
        )
    finally:
        db.close()