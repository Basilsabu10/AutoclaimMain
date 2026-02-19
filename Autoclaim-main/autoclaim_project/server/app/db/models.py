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
    # FORENSIC ANALYSIS (Image Integrity - AI Extracted)
    # ============================================================
    is_screen_recapture = Column(Boolean, default=False)
    has_ui_elements = Column(Boolean, default=False)
    has_watermarks = Column(Boolean, default=False)
    image_quality = Column(String, nullable=True)  # high|medium|low
    is_blurry = Column(Boolean, default=False)
    multiple_light_sources = Column(Boolean, default=False)
    shadows_inconsistent = Column(Boolean, default=False)
    
    # Legacy fields (computed from extracted data)
    authenticity_score = Column(Float, nullable=True)  # 0-100 (computed)
    forgery_detected = Column(Boolean, default=False)  # computed
    forgery_indicators = Column(JSON, default=list)  # Array of manipulation signs
    
    # ============================================================
    # VEHICLE IDENTIFICATION (Groq AI - Identity Extraction)
    # ============================================================
    detected_objects = Column(JSON, default=list)  # ["car", "damage_area"]
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_year = Column(String, nullable=True)
    vehicle_color = Column(String, nullable=True)
    
    # License Plate Details
    license_plate_detected = Column(Boolean, default=False)
    license_plate_text = Column(String, nullable=True)
    license_plate_match_status = Column(String, nullable=True)  # MATCH, MISMATCH, UNKNOWN
    license_plate_visible = Column(Boolean, default=False)
    license_plate_obscured = Column(Boolean, default=False)
    
    
    # ============================================================
    # DAMAGE ASSESSMENT (AI Extraction + Computed)
    # ============================================================
    ai_damage_detected = Column(Boolean, default=False)
    ai_damaged_panels = Column(JSON, default=list)  # Array of panel names from AI
    ai_damage_type = Column(String, nullable=True)  # dent|scratch|crack|shatter|crush|tear|missing
    damage_severity_score = Column(Float, nullable=True)  # 0.00-1.00 from AI extraction
    ai_severity = Column(String, nullable=True)  # Computed: none, minor, moderate, severe, totaled
    ai_affected_parts = Column(JSON, default=list)  # List of panel names (deprecated, use ai_damaged_panels)
    impact_point = Column(String, nullable=True)  # front_center|front_left|front_right|side_left|side_right|rear_center|multiple
    
    # Specific Damage Indicators (Extracted)
    paint_damage = Column(Boolean, default=False)
    glass_damage = Column(Boolean, default=False)
    is_rust_present = Column(Boolean, default=False)
    rust_locations = Column(JSON, default=list)
    is_dirt_in_damage = Column(Boolean, default=False)
    is_paint_faded_around_damage = Column(Boolean, default=False)
    airbags_deployed = Column(Boolean, default=False)
    fluid_leaks_visible = Column(Boolean, default=False)
    parts_missing = Column(Boolean, default=False)
    ai_structural_damage = Column(Boolean, default=False)  # Computed: True if severe/totaled
    
    
    # Cost Estimation
    ai_cost_min = Column(Integer, nullable=True)
    ai_cost_max = Column(Integer, nullable=True)
    repair_cost_breakdown = Column(JSON, nullable=True)  # Part-by-part breakdown [{part, inr_min, inr_max, ...}]
    
    # ============================================================
    # PRE-EXISTING DAMAGE DETECTION (Computed from extracted indicators)
    # ============================================================
    pre_existing_damage_detected = Column(Boolean, default=False)  # Computed
    pre_existing_indicators = Column(JSON, default=list)  # Computed from rust, dirt, faded paint
    pre_existing_description = Column(Text, nullable=True)  # Computed
    pre_existing_confidence = Column(Float, nullable=True)  # Computed
    
    # ============================================================
    # CONTEXTUAL ANALYSIS (Scene Extraction)
    # ============================================================
    location_type = Column(String, nullable=True)  # street|parking_lot|garage|highway|residential
    time_of_day = Column(String, nullable=True)  # day|night|dusk|unknown
    weather_visible = Column(String, nullable=True)  # clear|rain|snow|fog|unknown
    weather_conditions = Column(String, nullable=True)  # alias for weather_visible
    debris_visible = Column(Boolean, default=False)
    other_vehicles_visible = Column(Boolean, default=False)
    is_moving_traffic = Column(Boolean, default=False)
    
    lighting_quality = Column(String, nullable=True)  # good|poor
    photo_quality = Column(String, nullable=True)  # Same as image_quality
    consistent_with_narrative = Column(Boolean, nullable=True)  # Computed
    

    # ============================================================
    # RISK ASSESSMENT & FLAGS (Rule-Based Computed)
    # ============================================================
    ai_risk_flags = Column(JSON, default=list)  # Array of risk flag strings (COMPUTED)
    fraud_probability = Column(String, nullable=True)  # VERY_LOW, LOW, MEDIUM, HIGH (COMPUTED)
    fraud_score = Column(Float, nullable=True)  # 0.0-1.0 (COMPUTED)
    
    # ============================================================
    # FINAL ASSESSMENT (Rule-Based Computed)
    # ============================================================
    overall_confidence_score = Column(Float, nullable=True)  # 0-100 (COMPUTED)
    ai_recommendation = Column(String, nullable=True)  # APPROVE, REVIEW, REJECT (COMPUTED)
    ai_reasoning = Column(Text, nullable=True)  # Decision reasoning (COMPUTED)
    human_review_priority = Column(String, nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL (COMPUTED)
    
    # ============================================================
    # METADATA & RAW DATA
    # ============================================================
    ai_raw_response = Column(JSON, nullable=True)  # Complete Groq JSON response
    ai_provider = Column(String, default="groq")  # groq, yolo, etc
    ai_model = Column(String, nullable=True)  # Model version used
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analysis_version = Column(String, default="3.0")  # v3.0: Pure extraction + rule-based decisions
    
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
