import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database path in data/
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/neuro_enterprise.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# RELATIONAL MODELS / SCHEMAS
# ==========================================

class ClaimRecord(Base):
    """Main transactional table storing every processed dispute case."""
    __tablename__ = "claims"

    case_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    order_id = Column(String, index=True)
    claim_amount = Column(Float)
    claim_description = Column(Text)
    image_path = Column(String, nullable=True)
    
    # AI Evaluation Metrics
    fraud_score = Column(Float, default=0.0)
    proposed_action = Column(String)
    confidence = Column(Float)
    
    # Escalation & Resolution
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    status = Column(String, default="PROCESSED")  # AUTO_APPROVED, ESCALATED_PENDING, MANUALLY_APPROVED, MANUALLY_REJECTED
    
    # Audit Trail JSON Array & Execution Result
    trail = Column(JSON)
    execution_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Creates database tables on startup."""
    Base.metadata.create_all(bind=engine)
    print("✅ [Database] SQLite Relational Schema initialized successfully!")

# Initialize schema on module load
init_db()


def get_db_session():
    """Helper to get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session managed by caller