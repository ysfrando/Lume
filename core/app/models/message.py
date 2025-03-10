# models/message.py
from app.database import db
from datetime import datetime, timedelta
import uuid

class Message(db.Model):
    __tablename__ = 'message'
    
    # Define a proper primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    encrypted_content = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(24), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    max_views = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    @classmethod
    def create_message(cls, encrypted_content, iv, expiry_hours=24, max_views=1):
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        message = cls(
            id=str(uuid.uuid4()),  # Explicitly set the ID
            encrypted_content=encrypted_content,
            iv=iv,
            expires_at=expires_at,
            max_views=max_views
        )
        db.session.add(message)
        db.session.commit()
        return message.id
    
    @classmethod
    def get_message(cls, message_id):
        message = cls.query.filter_by(id=message_id, is_active=True).first()
        if not message:
            return None
            
        # Check if expired
        if datetime.utcnow() > message.expires_at:
            message.is_active = False
            db.session.commit()
            return None
            
        # Update view count
        message.view_count += 1
        
        # Check if max views reached
        if message.view_count >= message.max_views:
            message.is_active = False
            
        db.session.commit()
        return message.encrypted_content
    
    @classmethod
    def cleanup_expired(cls):
        expired = cls.query.filter(
            (cls.expires_at < datetime.utcnow()) | 
            (cls.view_count >= cls.max_views)
        ).update({'is_active': False})
        db.session.commit()
        return expired