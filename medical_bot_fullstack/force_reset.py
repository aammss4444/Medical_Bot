from database import engine
from sqlalchemy import text
import models

def force_reset():
    with engine.connect() as conn:
        # Disable foreign key checks momentarily if needed, or just use CASCADE
        conn.execute(text("DROP TABLE IF EXISTS chat_sessions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
    
    print("Tables dropped.")
    models.Base.metadata.create_all(bind=engine)
    print("Tables recreated.")

if __name__ == "__main__":
    force_reset()
