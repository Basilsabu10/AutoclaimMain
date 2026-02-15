"""
Database models for the AutoClaim system.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    """User accounts for the insurance system."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # user, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User profile fields
    name = Column(String, nullable=True)
    policy_id = Column(String, nullable=True)
    vehicle_number = Column(String, nullable=True)
    
    # Relationships
    claims = relationship("Claim", back_populates="user")
    policies = relationship("Policy", back_populates="user")


class PolicyPlan(Base):
    """Insurance policy plans/templates."""
    __tablename__ = "policy_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    coverage_amount = Column(Integer, nullable=False)
    premium_monthly = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    policies = relationship("Policy", back_populates="plan")


class Policy(Base):
    """Active insurance policies for users."""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("policy_plans.id"), nullable=False)
    
    # Vehicle details
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_year = Column(Integer, nullable=True)
    vehicle_registration = Column(String, nullable=True)  # License plate
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default="active")  # active, expired, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="policies")
    plan = relationship("PolicyPlan", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")


class ForensicAnalysis(Base):
    """
    Comprehensive forensic analysis data for insurance claims.
    Stores results from EXIF extraction, OCR, YOLOv8, and Groq AI analysis.
    """
    __tablename__ = "forensic_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, unique=True)
    
    # ============================================================
    # EXIF METADATA
    # ============================================================
    exif_timestamp = Column(DateTime, nullable=True)
    exif_gps_lat = Column(Float, nullable=True)
    exif_gps_lon = Column(Float, nullable=True)
    exif_location_name = Column(String, nullable=True)
    exif_camera_make = Column(String, nullable=True)
    exif_camera_model = Column(String, nullable=True)
    
    # ============================================================
    # OCR RESULTS (Number Plate)
    # ============================================================
    ocr_plate_text = Column(String, nullable=True)
    ocr_plate_confidence = Column(Float, nullable=True)
    ocr_raw_texts = Column(JSON, default=list)
    
    # ============================================================
    # YOLO DAMAGE DETECTION (Self-hosted)
    # ============================================================
    yolo_damage_detected = Column(Boolean, default=False)
    yolo_detections = Column(JSON, default=list)  # Array of detection objects
    yolo_severity = Column(String, nullable=True)  # minor, moderate, severe
    yolo_summary = Column(Text, nullable=True)
    
    # ============================================================
    # FORENSIC ANALYSIS (Image Integrity)
    # ============================================================
    authenticity_score = Column(Float, nullable=True)  # 0-100
    forgery_detected = Column(Boolean, default=False)
    forgery_indicators = Column(JSON, default=list)  # Array of manipulation signs
    digital_manipulation_confidence = Column(Float, nullable=True)  # 0-100
    
    # ============================================================
    # VEHICLE IDENTIFICATION (Groq AI)
    # ============================================================
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_year = Column(String, nullable=True)
    vehicle_color = Column(String, nullable=True)
    vehicle_identification_confidence = Column(Float, nullable=True)
    
    # License Plate Details
    license_plate_detected = Column(Boolean, default=False)
    license_plate_text = Column(String, nullable=True)
    license_plate_confidence = Column(Float, nullable=True)
    license_plate_match_status = Column(String, nullable=True)  # MATCH, MISMATCH, UNKNOWN
    
    vin_detected = Column(Boolean, default=False)
    vin_number = Column(String, nullable=True)
    
    # ============================================================
    # DAMAGE ASSESSMENT (Comprehensive)
    # ============================================================
    ai_damage_detected = Column(Boolean, default=False)
    ai_damaged_panels = Column(JSON, default=list)  # Array of {panel, type, severity, confidence}
    ai_damage_type = Column(String, nullable=True)  # Primary damage type
    ai_severity = Column(String, nullable=True)  # overall: none, minor, moderate, severe, totaled
    ai_affected_parts = Column(JSON, default=list)  # List of panel names
    ai_structural_damage = Column(Boolean, default=False)
    ai_safety_concerns = Column(JSON, default=list)  # Array of safety issues
    
    # Cost Estimation
    ai_cost_min = Column(Integer, nullable=True)
    ai_cost_max = Column(Integer, nullable=True)
    ai_cost_confidence = Column(Float, nullable=True)
    
    # ============================================================
    # PRE-EXISTING DAMAGE DETECTION
    # ============================================================
    pre_existing_damage_detected = Column(Boolean, default=False)
    pre_existing_indicators = Column(JSON, default=list)  # rust, old_repair, weathering, etc
    pre_existing_description = Column(Text, nullable=True)
    pre_existing_confidence = Column(Float, nullable=True)
    
    # ============================================================
    # CONTEXTUAL ANALYSIS
    # ============================================================
    location_type = Column(String, nullable=True)  # STREET, PARKING_LOT, etc
    weather_conditions = Column(String, nullable=True)
    lighting_quality = Column(String, nullable=True)  # GOOD, FAIR, POOR
    photo_quality = Column(String, nullable=True)  # HIGH, MEDIUM, LOW
    consistent_with_narrative = Column(Boolean, nullable=True)
    
    # ============================================================
    # CROSS-VERIFICATION
    # ============================================================
    narrative_match = Column(Boolean, nullable=True)
    policy_match = Column(Boolean, nullable=True)
    timeline_consistent = Column(Boolean, nullable=True)
    verification_discrepancies = Column(JSON, default=list)  # List of inconsistencies
    
    # ============================================================
    # RISK ASSESSMENT & FLAGS
    # ============================================================
    ai_risk_flags = Column(JSON, default=list)  # Array of risk flag strings
    fraud_probability = Column(String, nullable=True)  # LOW, MEDIUM, HIGH
    
    # ============================================================
    # FINAL ASSESSMENT
    # ============================================================
    overall_confidence_score = Column(Float, nullable=True)  # 0-100
    ai_recommendation = Column(String, nullable=True)  # APPROVE, REVIEW, REJECT
    ai_reasoning = Column(Text, nullable=True)  # Decision reasoning
    human_review_priority = Column(String, nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_actions = Column(JSON, default=list)  # Next steps
    
    # ============================================================
    # METADATA & RAW DATA
    # ============================================================
    ai_raw_response = Column(JSON, nullable=True)  # Complete Groq JSON response
    ai_provider = Column(String, default="groq")  # groq, yolo, etc
    ai_model = Column(String, nullable=True)  # Model version used
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analysis_version = Column(String, default="2.0")  # Forensic analysis version
    
    # Relationship
    claim = relationship("Claim", back_populates="forensic_analysis")


class Claim(Base):
    """Insurance claim submitted by a user."""
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True)
    description = Column(Text, nullable=True)
    image_paths = Column(JSON, default=list)  # Damage images
    status = Column(String, default="pending")  # pending, processing, completed, approved, rejected, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Upload paths
    front_image_path = Column(String, nullable=True)
    estimate_bill_path = Column(String, nullable=True)
    
    # Quick access fields (denormalized for performance)
    vehicle_number_plate = Column(String, nullable=True)
    ai_recommendation = Column(String, nullable=True)
    estimated_cost_min = Column(Integer, nullable=True)
    estimated_cost_max = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    forensic_analysis = relationship("ForensicAnalysis", back_populates="claim", uselist=False)
