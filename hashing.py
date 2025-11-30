from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,     
    memory_cost=102400,  
    parallelism=2,    
    hash_len=32,      
    salt_len=16
)

class Hasher:


    @staticmethod
    def verify_password(hashed_password: str, plain_password: str) -> bool:
        return ph.verify(hashed_password, plain_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return ph.hash(password)

