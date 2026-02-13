from database import SessionLocal, engine
import models

# Ensure tables exist
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
conversations = db.query(models.Conversation).order_by(models.Conversation.created_at).all()
print(f"Total conversations: {len(conversations)}")
for c in conversations:
    print(f"{c.role}: {c.content}")
db.close()
