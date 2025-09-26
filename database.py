import os
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
import json

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine and session with SSL configuration
engine = sa.create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class StudySession(Base):
    """Table to store study sessions"""
    __tablename__ = 'study_sessions'
    
    id = Column(Integer, primary_key=True)
    session_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatExchange(Base):
    """Table to store individual chat exchanges"""
    __tablename__ = 'chat_exchanges'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, sa.ForeignKey('study_sessions.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    subject_category = Column(String(100))  # For subject categorization
    rating = Column(Integer)  # 1-5 rating or -1/1 for thumbs down/up
    feedback = Column(Text)  # User feedback
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_database():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_db_session():
    """Get a database session"""
    return Session()

def create_study_session(session_name="Study Session"):
    """Create a new study session"""
    db = get_db_session()
    try:
        session = StudySession(session_name=session_name)
        db.add(session)
        db.commit()
        session_id = session.id
        db.refresh(session)
        return session_id
    finally:
        db.close()

def save_chat_exchange(session_id, question, answer, subject_category=None):
    """Save a chat exchange to the database"""
    db = get_db_session()
    try:
        exchange = ChatExchange(
            session_id=session_id,
            question=question,
            answer=answer,
            subject_category=subject_category
        )
        db.add(exchange)
        db.commit()
        return exchange.id
    finally:
        db.close()

def get_study_sessions():
    """Get all study sessions"""
    db = get_db_session()
    try:
        sessions = db.query(StudySession).order_by(StudySession.updated_at.desc()).all()
        return [{'id': s.id, 'name': s.session_name, 'created_at': s.created_at, 'updated_at': s.updated_at} for s in sessions]
    finally:
        db.close()

def get_chat_history(session_id):
    """Get chat history for a specific session"""
    db = get_db_session()
    try:
        exchanges = db.query(ChatExchange).filter(
            ChatExchange.session_id == session_id
        ).order_by(ChatExchange.timestamp.asc()).all()
        
        return [{
            'id': e.id,
            'question': e.question,
            'answer': e.answer,
            'subject_category': e.subject_category,
            'rating': e.rating,
            'feedback': e.feedback,
            'timestamp': e.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for e in exchanges]
    finally:
        db.close()

def update_exchange_rating(exchange_id, rating, feedback=None):
    """Update rating and feedback for a chat exchange"""
    db = get_db_session()
    try:
        exchange = db.query(ChatExchange).filter(ChatExchange.id == exchange_id).first()
        if exchange:
            exchange.rating = rating
            if feedback:
                exchange.feedback = feedback
            db.commit()
            return True
        return False
    finally:
        db.close()

def delete_study_session(session_id):
    """Delete a study session and all its exchanges"""
    db = get_db_session()
    try:
        # Delete all exchanges first
        db.query(ChatExchange).filter(ChatExchange.session_id == session_id).delete()
        # Delete the session
        db.query(StudySession).filter(StudySession.id == session_id).delete()
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def get_session_stats():
    """Get overall statistics"""
    db = get_db_session()
    try:
        total_sessions = db.query(StudySession).count()
        total_exchanges = db.query(ChatExchange).count()
        avg_rating = db.query(sa.func.avg(ChatExchange.rating)).filter(ChatExchange.rating.isnot(None)).scalar()
        
        return {
            'total_sessions': total_sessions,
            'total_exchanges': total_exchanges,
            'average_rating': round(avg_rating, 2) if avg_rating else None
        }
    finally:
        db.close()