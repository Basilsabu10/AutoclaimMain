"""
Rule-Based Verification Engine for AutoClaim — v2.0
Deterministic decision logic for claim approval / flagging / rejection.

DESIGN PRINCIPLES
-----------------
1. AI only extracts structured facts — it NEVER makes decisions.
2. Every decision is auditable: rule ID, reason, severity, score.
3. Rules are grouped into phases matching the SRS (FR-2.x).
4. New rules added in v2.0 are clearly marked with # NEW.
5. Thresholds live in RuleConfig so they can be tuned without touching logic.

DECISION MATRIX
---------------
APPROVED     → no failures, OR only LOW severity (score < FLAG_THRESHOLD)
FLAGGED      → score >= FLAG_THRESHOLD but < REJECT_THRESHOLD
REJECTED     → any CRITICAL failure, OR score >= REJECT_THRESHOLD
MONITORED    → approved with only LOW issues (score 1 – FLAG_THRESHOLD-1)

v2.0 additions vs v1.x
-----------------------
• CHECK 9  – Image Quality Gate            (blocks blurry/screen-recaptures early)
• CHECK 10 – YOLO Damage Corroboration     (cross-validates AI vs rule-based)
• CHECK 11 – Damage-Severity vs Cost Sanity (catches inflated estimates)
• CHECK 12 – Multi-Image Consistency       (detects mixed-incident photos)
• CHECK 13 – Policy Active & Coverage Gate (verifies policy is valid/covers event)
• CHECK 14 – Airbag/Fluid Totalled-Vehicle (flags totalled claims missing markers)
• CHECK 15 – Duplicate / Repeat-Claim Guard (fraud ring detection)
• Refined scoring: compounding multiplier for correlated failures
• Weighted confidence score (0-100) returned alongside binary decision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import math


# ===========================================================================
# CONFIGURATION
# ===========================================================================

@dataclass
class RuleConfig:
    """
    All numeric thresholds in a single place.
    Change here — logic picks them up automatically.
    """

    # ── Amount threshold ────────────────────────────────────────────────────
    AUTO_APPROVAL_AMOUNT_THRESHOLD: int = 20_000   # ₹ 20,000

    # ── Confidence thresholds ───────────────────────────────────────────────
    MIN_VEHICLE_DETECTION_CONFIDENCE: float = 0.85
    MIN_OCR_PLATE_CONFIDENCE: float = 0.80
    MIN_CHASE_NUMBER_CONFIDENCE: float = 0.75
    MIN_OVERALL_IMAGE_QUALITY_SCORE: float = 0.40  # NEW: below = reject image

    # ── Severity weights ────────────────────────────────────────────────────
    SEVERITY_WEIGHTS: Dict[str, int] = field(default_factory=lambda: {
        "CRITICAL": 10,
        "HIGH":      5,
        "MEDIUM":    2,
        "LOW":       1,
    })

    # ── Decision thresholds ─────────────────────────────────────────────────
    AUTO_REJECT_SCORE_THRESHOLD: int = 10   # score >= 10 → REJECTED
    FLAG_FOR_REVIEW_SCORE_THRESHOLD: int = 2  # score >= 2  → FLAGGED

    # ── Stock-photo ─────────────────────────────────────────────────────────
    STOCK_PHOTO_REJECT_LEVELS: List[str] = field(
        default_factory=lambda: ["high", "very_high"]
    )

    # ── Damage–cost sanity ──────────────────────────────────────────────────
    # NEW: maximum ₹ per panel per damage type before flagging as inflated
    COST_PER_PANEL_LIMITS: Dict[str, int] = field(default_factory=lambda: {
        "none":     0,
        "minor":    15_000,
        "moderate": 60_000,
        "severe":   1_50_000,
        "totaled":  10_00_000,
    })
    # NEW: maximum allowed ratio of claim_amount / AI estimated max before flag
    MAX_CLAIM_TO_ESTIMATE_RATIO: float = 2.0

    # ── Severity corroboration ──────────────────────────────────────────────
    # NEW: YOLO and AI must agree on severity; weight of disagreement
    YOLO_AI_SEVERITY_MISMATCH_PENALTY: int = 3   # added directly to score

    # ── Duplicate guard ─────────────────────────────────────────────────────
    # NEW: within how many days the same plate + user triggers duplication flag
    DUPLICATE_CLAIM_WINDOW_DAYS: int = 30

    # ── Compounding multiplier ──────────────────────────────────────────────
    # NEW: if >= N distinct HIGH/CRITICAL failures, multiply score
    COMPOUND_FAILURE_THRESHOLD: int = 3
    COMPOUND_MULTIPLIER: float = 1.5


# ===========================================================================
# RESULT TYPES
# ===========================================================================

@dataclass
class FailedRule:
    rule_id: str
    rule_name: str
    reason: str
    severity: str       # CRITICAL | HIGH | MEDIUM | LOW
    phase: str          # A | B | C | D | E


@dataclass
class VerificationResult:
    status: str                          # APPROVED | FLAGGED | REJECTED
    decision_reason: str
    confidence_level: str                # HIGH | MEDIUM | LOW
    confidence_score: float              # 0 – 100 (weighted)
    auto_approved: bool
    requires_human_review: bool
    requires_monitoring: bool
    severity_score: float
    passed_checks: List[str]
    failed_checks: List[FailedRule]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "decision_reason": self.decision_reason,
            "confidence_level": self.confidence_level,
            "confidence_score": round(self.confidence_score, 2),
            "auto_approved": self.auto_approved,
            "requires_human_review": self.requires_human_review,
            "requires_monitoring": self.requires_monitoring,
            "passed_checks_count": len(self.passed_checks),
            "failed_checks_count": len(self.failed_checks),
            "severity_score": round(self.severity_score, 2),
            "passed_checks": self.passed_checks,
            "failed_checks": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "reason": r.reason,
                    "severity": r.severity,
                    "phase": r.phase,
                }
                for r in self.failed_checks
            ],
            "timestamp": self.timestamp,
        }


# ===========================================================================
# MAIN ENGINE
# ===========================================================================

class VerificationRules:
    """
    Rule-based verification engine for AutoClaim.

    Usage
    -----
    engine = VerificationRules()
    result = engine.verify_claim(
        claim_amount=18000,
        ai_analysis=groq_output,
        policy_data=policy_row,
        history=past_claims_list,      # NEW: list of prior claim dicts
    )
    print(result.to_dict())
    """

    def __init__(self, config: Optional[RuleConfig] = None) -> None:
        self.config = config or RuleConfig()
        self._reset()

    # ── Public API ───────────────────────────────────────────────────────────

    def verify_claim(
        self,
        claim_amount: int,
        ai_analysis: Dict[str, Any],
        policy_data: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        weather_data: Optional[Dict[str, Any]] = None,   # kept for compat
    ) -> VerificationResult:
        """
        Run all verification checks and return a VerificationResult.

        Parameters
        ----------
        claim_amount : int
            Claimed repair/loss amount in ₹.
        ai_analysis : dict
            Structured output from the Groq / YOLO / OCR / EXIF pipeline.
            Expected top-level keys — see _ai() helper for schema.
        policy_data : dict
            Policy row from DB (vehicle_make, vehicle_model,
            vehicle_registration, chase_number, status, plan_coverage,
            location, start_date, end_date, …).
        history : list[dict], optional
            Prior claims for the same user (used for duplicate detection).
        weather_data : dict, optional
            Deprecated — not used; kept for backward compatibility.
        """
        self._reset()

        # ── PHASE A: Integrity & Source Checks ───────────────────────────
        self._check_1_image_quality_gate(ai_analysis)        # NEW (must run first)
        self._check_2_metadata_verification(ai_analysis, policy_data)
        self._check_3_reverse_image_search(ai_analysis)
        self._check_4_digital_forgery(ai_analysis)

        # ── PHASE B: Vehicle & Damage Verification ────────────────────────
        self._check_5_vehicle_match(ai_analysis, policy_data)
        self._check_6_license_plate_match(ai_analysis, policy_data)
        self._check_7_chase_number_match(ai_analysis, policy_data)
        self._check_8_pre_existing_damage(ai_analysis)
        self._check_9_yolo_damage_corroboration(ai_analysis)   # NEW
        self._check_10_totalled_vehicle_markers(ai_analysis)   # NEW

        # ── PHASE C: Contextual Consistency ──────────────────────────────
        self._check_11_narrative_consistency(ai_analysis)
        self._check_12_multi_image_consistency(ai_analysis)    # NEW

        # ── PHASE D: Financial Sanity ─────────────────────────────────────
        self._check_13_amount_threshold(claim_amount)
        self._check_14_damage_cost_sanity(claim_amount, ai_analysis)  # NEW

        # ── PHASE E: Policy & History Validation ──────────────────────────
        self._check_15_policy_active_and_coverage(policy_data, claim_amount)  # NEW
        self._check_16_duplicate_claim_guard(ai_analysis, policy_data, history)  # NEW

        # ── Final decision ────────────────────────────────────────────────
        return self._make_final_decision(claim_amount)

    # ── Internal state ───────────────────────────────────────────────────────

    def _reset(self) -> None:
        self._passed: List[str] = []
        self._failed: List[FailedRule] = []
        self._raw_score: float = 0.0

    # ── Accessor helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _ai(analysis: Dict[str, Any], *keys: str, default: Any = None) -> Any:
        """Safe nested dict getter: _ai(d, 'a', 'b') → d['a']['b']"""
        val = analysis
        for k in keys:
            if not isinstance(val, dict):
                return default
            val = val.get(k, default)
        return val

    def _pass(self, rule_id: str) -> None:
        self._passed.append(rule_id)

    def _fail(
        self,
        rule_id: str,
        rule_name: str,
        reason: str,
        severity: str,
        phase: str,
    ) -> None:
        self._failed.append(
            FailedRule(
                rule_id=rule_id,
                rule_name=rule_name,
                reason=reason,
                severity=severity,
                phase=phase,
            )
        )
        self._raw_score += self.config.SEVERITY_WEIGHTS.get(severity, 0)

    # =========================================================================
    # PHASE A — Integrity & Source Checks
    # =========================================================================

    # CHECK 1 (NEW): Image Quality Gate
    # ─────────────────────────────────
    def _check_1_image_quality_gate(self, ai: Dict[str, Any]) -> None:
        """
        Reject or flag images that are too degraded for reliable analysis.

        Checks:
        • is_blurry (ForensicAnalysis field)
        • is_screen_recapture (photo of a photo / screenshot)
        • has_ui_elements (on-screen app artifacts)
        • image_quality (high | medium | low)

        Severity rationale
        ------------------
        Screen-recaptures are CRITICAL because they nullify ALL metadata checks.
        Blurry images are HIGH — they impair every downstream AI check.
        Low quality alone is MEDIUM — analysis can continue with caution.
        """
        is_screen = self._ai(ai, "forensic_indicators", "is_screen_recapture", default=False)
        has_ui    = self._ai(ai, "forensic_indicators", "has_ui_elements",     default=False)
        is_blurry = self._ai(ai, "forensic_indicators", "is_blurry",           default=False)
        quality   = (self._ai(ai, "forensic_indicators", "image_quality", default="high") or "high").lower()

        if is_screen or has_ui:
            self._fail(
                rule_id="SCREEN_RECAPTURE",
                rule_name="Image Quality Gate — Screen Recapture (v2 NEW)",
                reason=(
                    "Image appears to be a screen-capture or photo of a screen. "
                    "EXIF metadata is stripped and AI results are unreliable."
                ),
                severity="CRITICAL",
                phase="A",
            )
            return  # No point checking downstream on a screen-shot

        if is_blurry:
            self._fail(
                rule_id="IMAGE_BLURRY",
                rule_name="Image Quality Gate — Blur Detection (v2 NEW)",
                reason="Image is excessively blurry. Damage and plate recognition are unreliable.",
                severity="HIGH",
                phase="A",
            )
        elif quality == "low":
            self._fail(
                rule_id="IMAGE_LOW_QUALITY",
                rule_name="Image Quality Gate — Low Quality (v2 NEW)",
                reason="Image quality is low. AI analysis may be inaccurate.",
                severity="MEDIUM",
                phase="A",
            )
        else:
            self._pass("IMAGE_QUALITY_OK")

    # CHECK 2: Metadata Verification (FR-2.1)
    # ─────────────────────────────────────────
    def _check_2_metadata_verification(
        self, ai: Dict[str, Any], policy: Dict[str, Any]
    ) -> None:
        """
        Verify EXIF timestamp and GPS coordinates.

        Fails:
        • No timestamp → HIGH (could be edited image)
        • No GPS       → LOW  (common on older phones; not conclusive)
        • GPS mismatch → MEDIUM (location doesn't match policy address)
        """
        exif = ai.get("exif_metadata", {}) or {}

        if not exif.get("timestamp"):
            self._fail(
                "METADATA_MISSING",
                "Metadata Verification (FR-2.1)",
                "No EXIF timestamp — possible screenshot or digitally edited image.",
                "HIGH",
                "A",
            )
        else:
            self._pass("METADATA_TIMESTAMP")

        gps = exif.get("gps_coordinates", {}) or {}
        if gps.get("latitude") and gps.get("longitude"):
            policy_loc   = (policy.get("location") or "").lower()
            detected_loc = (exif.get("location_name") or "").lower()
            if policy_loc and detected_loc:
                if not self._location_matches(policy_loc, detected_loc):
                    self._fail(
                        "GPS_LOCATION_MISMATCH",
                        "GPS Location Verification",
                        f"Location mismatch — Policy: '{policy_loc}', GPS: '{detected_loc}'.",
                        "MEDIUM",
                        "A",
                    )
                else:
                    self._pass("GPS_LOCATION")
            else:
                self._pass("GPS_EXISTS")
        else:
            self._fail(
                "GPS_MISSING",
                "GPS Verification",
                "No GPS coordinates in image metadata.",
                "LOW",
                "A",
            )

    # CHECK 3: Reverse Image Search (FR-2.2)
    # ─────────────────────────────────────────
    def _check_3_reverse_image_search(self, ai: Dict[str, Any]) -> None:
        """Detect stock or recycled internet photos."""
        auth = ai.get("authenticity_indicators", {}) or {}
        likelihood = (auth.get("stock_photo_likelihood") or "unknown").lower()

        if likelihood in self.config.STOCK_PHOTO_REJECT_LEVELS:
            self._fail(
                "STOCK_PHOTO_DETECTED",
                "Reverse Image Search (FR-2.2)",
                f"Image highly likely to be a stock/internet photo (likelihood: {likelihood}).",
                "CRITICAL",
                "A",
            )
        elif likelihood == "medium":
            self._fail(
                "STOCK_PHOTO_SUSPICIOUS",
                "Stock Photo Check (FR-2.2)",
                "Image has stock-photo characteristics — original source unconfirmed.",
                "MEDIUM",
                "A",
            )
        else:
            self._pass("REVERSE_IMAGE_SEARCH")

    # CHECK 4: Digital Forgery Detection (FR-2.3)
    # ─────────────────────────────────────────────
    def _check_4_digital_forgery(self, ai: Dict[str, Any]) -> None:
        """
        Detect digital manipulation: editing, lighting/shadow inconsistencies,
        compression artifacts, multiple light sources.
        """
        auth = ai.get("authenticity_indicators", {}) or {}
        forensic = ai.get("forensic_indicators", {}) or {}

        issues: List[str] = []
        if auth.get("editing_detected", False):
            issues.append("digital editing detected")
        if not auth.get("lighting_consistent", True):
            issues.append("inconsistent lighting")
        if not auth.get("shadows_natural", True):
            issues.append("unnatural shadows")
        if not auth.get("compression_uniform", True):
            issues.append("non-uniform compression artifacts")
        if forensic.get("multiple_light_sources", False):
            issues.append("multiple conflicting light sources")
        if forensic.get("shadows_inconsistent", False):
            issues.append("shadow direction inconsistency")
        if forensic.get("has_watermarks", False):
            issues.append("watermarks detected (possible recycled media)")

        if issues:
            self._fail(
                "DIGITAL_MANIPULATION",
                "Digital Forgery Detection (FR-2.3)",
                f"Image manipulation indicators: {', '.join(issues)}.",
                "CRITICAL",
                "A",
            )
        else:
            self._pass("DIGITAL_FORGERY")

    # =========================================================================
    # PHASE B — Vehicle & Damage Verification
    # =========================================================================

    # CHECK 5: Vehicle Match (FR-2.4)
    # ──────────────────────────────────
    def _check_5_vehicle_match(
        self, ai: Dict[str, Any], policy: Dict[str, Any]
    ) -> None:
        """Confirm make/model in image matches the insured vehicle."""
        detected   = ai.get("vehicle_identification", {}) or {}
        p_make     = (policy.get("vehicle_make")  or "").lower()
        p_model    = (policy.get("vehicle_model") or "").lower()
        d_make     = (detected.get("make")  or "").lower()
        d_model    = (detected.get("model") or "").lower()
        confidence = detected.get("detected_confidence") or 0.0

        # v2: also check vehicle_color consistency if policy stores it
        p_color = (policy.get("vehicle_color") or "").lower()
        d_color = (detected.get("color") or "").lower()

        if confidence < self.config.MIN_VEHICLE_DETECTION_CONFIDENCE:
            self._fail(
                "VEHICLE_LOW_CONFIDENCE",
                "Vehicle Detection Confidence",
                (
                    f"Vehicle ID confidence {confidence*100:.0f}% is below "
                    f"threshold {self.config.MIN_VEHICLE_DETECTION_CONFIDENCE*100:.0f}%."
                ),
                "MEDIUM",
                "B",
            )

        make_ok  = bool(p_make)  and (p_make in d_make  or d_make in p_make)
        model_ok = bool(p_model) and (p_model in d_model or d_model in p_model)

        if not (make_ok and model_ok):
            self._fail(
                "VEHICLE_MISMATCH",
                "Vehicle Match (FR-2.4)",
                (
                    f"Vehicle mismatch — Policy: {p_make} {p_model}, "
                    f"Detected: {d_make} {d_model}."
                ),
                "CRITICAL",
                "B",
            )
        else:
            self._pass("VEHICLE_MATCH")

        # NEW: color check (MEDIUM — AI color detection is approximate)
        if p_color and d_color and p_color not in d_color and d_color not in p_color:
            self._fail(
                "VEHICLE_COLOR_MISMATCH",
                "Vehicle Color Verification (v2 NEW)",
                f"Color mismatch — Policy: {p_color}, Detected: {d_color}.",
                "MEDIUM",
                "B",
            )

    # CHECK 6: License Plate Match (FR-2.5)
    # ───────────────────────────────────────
    def _check_6_license_plate_match(
        self, ai: Dict[str, Any], policy: Dict[str, Any]
    ) -> None:
        """Strict exact OCR match against policy registration."""
        ocr         = ai.get("ocr_data", {}) or {}
        raw_text    = ocr.get("plate_text") or ""
        ocr_text    = raw_text.upper().replace(" ", "").replace("-", "")
        ocr_conf    = ocr.get("confidence") or 0.0
        policy_plate = (
            (policy.get("vehicle_registration") or "")
            .upper().replace(" ", "").replace("-", "")
        )
        plate_obscured = self._ai(ai, "vehicle_identification", "license_plate_obscured",
                                  default=False)

        if not ocr_text:
            severity = "HIGH" if not plate_obscured else "MEDIUM"
            self._fail(
                "PLATE_NOT_DETECTED",
                "License Plate Detection (FR-2.5)",
                (
                    "License plate not visible or unreadable"
                    + (" (plate may be obscured)." if plate_obscured else ".")
                ),
                severity,
                "B",
            )
            return

        if ocr_conf < self.config.MIN_OCR_PLATE_CONFIDENCE:
            self._fail(
                "PLATE_LOW_CONFIDENCE",
                "License Plate OCR Confidence",
                (
                    f"OCR confidence {ocr_conf*100:.0f}% below threshold "
                    f"{self.config.MIN_OCR_PLATE_CONFIDENCE*100:.0f}%."
                ),
                "MEDIUM",
                "B",
            )

        if policy_plate and ocr_text != policy_plate:
            self._fail(
                "PLATE_MISMATCH",
                "License Plate Verification (FR-2.5)",
                f"Plate mismatch — Policy: {policy_plate}, OCR: {ocr_text}.",
                "CRITICAL",
                "B",
            )
        else:
            self._pass("LICENSE_PLATE")

    # CHECK 7: Chase Number (VIN) Verification (FR-2.8 / original check 8)
    # ───────────────────────────────────────────────────────────────────────
    def _check_7_chase_number_match(
        self, ai: Dict[str, Any], policy: Dict[str, Any]
    ) -> None:
        """Chase / VIN number exact match."""
        ocr         = ai.get("ocr_data", {}) or {}
        ocr_chase   = (ocr.get("chase_number") or "").upper().strip()
        chase_conf  = ocr.get("chase_number_confidence") or 0.0
        policy_chase = (policy.get("chase_number") or "").upper().strip()

        if not ocr_chase:
            self._pass("CHASE_NUMBER_NOT_PROVIDED")
            return

        if chase_conf < self.config.MIN_CHASE_NUMBER_CONFIDENCE:
            self._fail(
                "CHASE_NUMBER_LOW_CONFIDENCE",
                "Chase Number OCR Confidence",
                (
                    f"Chase number OCR confidence {chase_conf*100:.0f}% below "
                    f"threshold {self.config.MIN_CHASE_NUMBER_CONFIDENCE*100:.0f}%."
                ),
                "MEDIUM",
                "B",
            )

        if policy_chase and ocr_chase != policy_chase:
            self._fail(
                "CHASE_NUMBER_MISMATCH",
                "Chase Number Verification (FR-2.8)",
                f"Chase number mismatch — Policy: {policy_chase}, OCR: {ocr_chase}.",
                "HIGH",
                "B",
            )
        else:
            self._pass("CHASE_NUMBER_MATCH")

    # CHECK 8: Pre-Existing Damage (FR-2.6)
    # ───────────────────────────────────────
    def _check_8_pre_existing_damage(self, ai: Dict[str, Any]) -> None:
        """Detect rust, paint fading, old repairs — indicators of prior damage."""
        pre = ai.get("pre_existing_indicators", {}) or {}
        # Also read directly from ForensicAnalysis flat fields
        forensic = ai.get("forensic_indicators", {}) or {}

        indicators: List[str] = []
        if pre.get("rust_detected") or forensic.get("is_rust_present"):
            indicators.append("rust in damaged area")
        if pre.get("paint_fading") or forensic.get("is_paint_faded_around_damage"):
            indicators.append("paint fading around damage")
        if pre.get("dirt_accumulation") or forensic.get("is_dirt_in_damage"):
            indicators.append("accumulated dirt in damage")
        if pre.get("old_repairs_visible"):
            indicators.append("evidence of previous repairs")

        if indicators:
            self._fail(
                "PRE_EXISTING_DAMAGE",
                "Pre-Existing Damage Detection (FR-2.6)",
                f"Pre-existing damage indicators: {', '.join(indicators)}.",
                "HIGH",
                "B",
            )
        else:
            self._pass("PRE_EXISTING_DAMAGE")

    # CHECK 9 (NEW): YOLO vs AI Damage Corroboration
    # ─────────────────────────────────────────────────
    def _check_9_yolo_damage_corroboration(self, ai: Dict[str, Any]) -> None:
        """
        Cross-validate YOLO damage detection against the Groq AI assessment.

        Severity logic
        --------------
        If YOLO says damage exists but AI says none (or vice-versa) → HIGH.
        If severity levels differ by ≥ 2 bands → MEDIUM.
        This catches cases where only one pipeline was fed manipulated images.
        """
        severity_rank = {"none": 0, "minor": 1, "moderate": 2, "severe": 3, "totaled": 4}

        yolo_detected = self._ai(ai, "yolo_results", "yolo_damage_detected", default=None)
        yolo_severity = (self._ai(ai, "yolo_results", "yolo_severity") or "none").lower()
        ai_detected   = self._ai(ai, "damage_assessment", "ai_damage_detected", default=None)
        ai_severity   = (self._ai(ai, "damage_assessment", "ai_severity") or "none").lower()

        # If either pipeline didn't run, skip
        if yolo_detected is None or ai_detected is None:
            self._pass("YOLO_CORROBORATION_SKIPPED")
            return

        if yolo_detected != ai_detected:
            self._fail(
                "YOLO_AI_DAMAGE_DISAGREEMENT",
                "YOLO vs AI Damage Corroboration (v2 NEW)",
                (
                    f"YOLO damage_detected={yolo_detected} contradicts "
                    f"AI damage_detected={ai_detected}. "
                    "Possible image spoofing between analysis stages."
                ),
                "HIGH",
                "B",
            )
        else:
            yolo_rank = severity_rank.get(yolo_severity, 0)
            ai_rank   = severity_rank.get(ai_severity,   0)
            diff      = abs(yolo_rank - ai_rank)
            if diff >= 2:
                self._fail(
                    "YOLO_AI_SEVERITY_GAP",
                    "YOLO vs AI Severity Gap (v2 NEW)",
                    (
                        f"Severity discrepancy: YOLO={yolo_severity}, AI={ai_severity}. "
                        f"Gap of {diff} bands."
                    ),
                    "MEDIUM",
                    "B",
                )
                # Apply compounding penalty directly
                self._raw_score += self.config.YOLO_AI_SEVERITY_MISMATCH_PENALTY
            else:
                self._pass("YOLO_AI_CORROBORATED")

    # CHECK 10 (NEW): Totalled-Vehicle Marker Validation
    # ────────────────────────────────────────────────────
    def _check_10_totalled_vehicle_markers(self, ai: Dict[str, Any]) -> None:
        """
        If AI severity is 'totaled', expect evidence of airbag deployment
        or visible fluid leaks. Their absence is suspicious.

        If AI says 'severe' or 'totaled' but YOLO says 'none' or 'minor',
        this is also caught by Check 9. This check focuses on physical markers.
        """
        ai_severity    = (self._ai(ai, "damage_assessment", "ai_severity") or "none").lower()
        airbags        = self._ai(ai, "damage_assessment", "airbags_deployed",    default=False)
        fluid_leaks    = self._ai(ai, "damage_assessment", "fluid_leaks_visible", default=False)
        parts_missing  = self._ai(ai, "damage_assessment", "parts_missing",       default=False)

        if ai_severity == "totaled":
            markers = []
            if airbags:
                markers.append("airbag deployment")
            if fluid_leaks:
                markers.append("fluid leaks")
            if parts_missing:
                markers.append("missing parts")

            if not markers:
                self._fail(
                    "TOTALED_NO_PHYSICAL_MARKERS",
                    "Totalled Vehicle Physical Marker Check (v2 NEW)",
                    (
                        "Claim severity assessed as 'totaled' but no physical "
                        "markers (airbag deployment, fluid leaks, missing parts) "
                        "are visible. Possible severity inflation."
                    ),
                    "HIGH",
                    "B",
                )
            else:
                self._pass("TOTALED_MARKERS_PRESENT")
        else:
            self._pass("TOTAL_VEHICLE_CHECK_NA")

    # =========================================================================
    # PHASE C — Contextual Consistency
    # =========================================================================

    # CHECK 11: Narrative Consistency (FR-2.7)
    # ─────────────────────────────────────────
    def _check_11_narrative_consistency(self, ai: Dict[str, Any]) -> None:
        """User narrative must align with visual evidence."""
        narrative = ai.get("narrative_consistency", {}) or {}

        if not narrative.get("visual_evidence_matches", False):
            inconsistencies: List[str] = narrative.get("inconsistencies", [])
            self._fail(
                "NARRATIVE_MISMATCH",
                "Narrative Consistency (FR-2.7)",
                (
                    f"Narrative inconsistent with evidence: {'; '.join(inconsistencies)}"
                    if inconsistencies
                    else "User narrative does not match visual evidence."
                ),
                "HIGH",
                "C",
            )
        else:
            self._pass("NARRATIVE_CONSISTENCY")

    # CHECK 12 (NEW): Multi-Image Consistency
    # ─────────────────────────────────────────
    def _check_12_multi_image_consistency(self, ai: Dict[str, Any]) -> None:
        """
        When multiple images are submitted, verify:
        • Same vehicle (plate/color/make across all images)
        • Consistent lighting / time-of-day metadata
        • Consistent damage location across angles

        This check relies on the multi_image_analysis key populated by the
        orchestrator after aggregating individual image results.
        """
        multi = ai.get("multi_image_analysis", {}) or {}
        if not multi:
            self._pass("MULTI_IMAGE_NOT_APPLICABLE")
            return

        issues: List[str] = []
        if not multi.get("plates_consistent", True):
            issues.append("different license plates across images")
        if not multi.get("vehicle_consistent", True):
            issues.append("vehicle make/model differs across images")
        if not multi.get("lighting_consistent", True):
            issues.append("time-of-day / lighting differs across images")
        if not multi.get("damage_location_consistent", True):
            issues.append("damage location contradicts across angles")

        if issues:
            self._fail(
                "MULTI_IMAGE_INCONSISTENCY",
                "Multi-Image Consistency Check (v2 NEW)",
                f"Cross-image inconsistencies detected: {', '.join(issues)}.",
                "HIGH",
                "C",
            )
        else:
            self._pass("MULTI_IMAGE_CONSISTENT")

    # =========================================================================
    # PHASE D — Financial Sanity
    # =========================================================================

    # CHECK 13: Amount Threshold (FR-3.1)
    # ─────────────────────────────────────
    def _check_13_amount_threshold(self, claim_amount: int) -> None:
        """Claim amount vs auto-approval threshold."""
        if claim_amount <= self.config.AUTO_APPROVAL_AMOUNT_THRESHOLD:
            self._pass("AMOUNT_THRESHOLD")
        else:
            self._fail(
                "AMOUNT_EXCEEDS_THRESHOLD",
                "Amount Threshold Check (FR-3.1)",
                (
                    f"Claim ₹{claim_amount:,} exceeds auto-approval limit "
                    f"₹{self.config.AUTO_APPROVAL_AMOUNT_THRESHOLD:,}."
                ),
                "MEDIUM",
                "D",
            )

    # CHECK 14 (NEW): Damage–Cost Sanity
    # ─────────────────────────────────────
    def _check_14_damage_cost_sanity(
        self, claim_amount: int, ai: Dict[str, Any]
    ) -> None:
        """
        Cross-validate claimed amount against AI cost estimate range.

        Flags:
        • Claim > AI max estimate × MAX_CLAIM_TO_ESTIMATE_RATIO → HIGH
        • Claim < AI min estimate / 2 (possibly under-declared) → LOW
        • Damage severity = none but claim > 0 → CRITICAL
        """
        damage = ai.get("damage_assessment", {}) or {}
        ai_severity = (damage.get("ai_severity") or "none").lower()
        ai_min = damage.get("ai_cost_min")   # int or None
        ai_max = damage.get("ai_cost_max")   # int or None

        # No damage but claim submitted
        if ai_severity == "none" and claim_amount > 0:
            self._fail(
                "CLAIM_NO_DAMAGE_DETECTED",
                "Damage–Cost Sanity — No Damage (v2 NEW)",
                (
                    f"AI detected no damage but claim of ₹{claim_amount:,} submitted. "
                    "Possible fraud."
                ),
                "CRITICAL",
                "D",
            )
            return

        # Compare against estimated range
        if ai_max is not None and ai_max > 0:
            ratio = claim_amount / ai_max
            if ratio > self.config.MAX_CLAIM_TO_ESTIMATE_RATIO:
                self._fail(
                    "CLAIM_INFLATED",
                    "Damage–Cost Sanity — Inflated Claim (v2 NEW)",
                    (
                        f"Claim ₹{claim_amount:,} is {ratio:.1f}× the AI max estimate "
                        f"₹{ai_max:,} (limit: {self.config.MAX_CLAIM_TO_ESTIMATE_RATIO}×). "
                        "Possible claim inflation."
                    ),
                    "HIGH",
                    "D",
                )
            elif ai_min is not None and claim_amount < ai_min / 2:
                self._fail(
                    "CLAIM_SUSPICIOUSLY_LOW",
                    "Damage–Cost Sanity — Under-declared (v2 NEW)",
                    (
                        f"Claim ₹{claim_amount:,} is far below AI min estimate "
                        f"₹{ai_min:,}. Possible under-declaration or incorrect images."
                    ),
                    "LOW",
                    "D",
                )
            else:
                self._pass("DAMAGE_COST_SANITY")
        else:
            self._pass("DAMAGE_COST_SANITY_NO_ESTIMATE")

    # =========================================================================
    # PHASE E — Policy & History Validation
    # =========================================================================

    # CHECK 15 (NEW): Policy Active & Coverage Gate
    # ───────────────────────────────────────────────
    def _check_15_policy_active_and_coverage(
        self, policy: Dict[str, Any], claim_amount: int
    ) -> None:
        """
        Validate that the policy is active and covers the claimed amount.

        Checks:
        • policy.status == 'active'
        • claim date (today) is between policy start_date and end_date
        • claim_amount <= policy.plan_coverage (or plan.coverage_amount)
        """
        status      = (policy.get("status") or "").lower()
        coverage    = policy.get("plan_coverage") or policy.get("coverage_amount") or 0
        start_str   = policy.get("start_date")
        end_str     = policy.get("end_date")
        today       = datetime.utcnow().date()

        if status != "active":
            self._fail(
                "POLICY_INACTIVE",
                "Policy Status Check (v2 NEW)",
                f"Policy status is '{status}' — must be 'active' for claim processing.",
                "CRITICAL",
                "E",
            )
        else:
            self._pass("POLICY_ACTIVE")

        # Date window
        in_window = True
        try:
            if start_str:
                start = datetime.fromisoformat(str(start_str)).date()
                if today < start:
                    in_window = False
            if end_str:
                end = datetime.fromisoformat(str(end_str)).date()
                if today > end:
                    in_window = False
        except (ValueError, TypeError):
            in_window = True  # Cannot parse → don't penalise

        if not in_window:
            self._fail(
                "POLICY_EXPIRED_OR_NOT_STARTED",
                "Policy Date Window Check (v2 NEW)",
                f"Incident date {today} falls outside policy window {start_str} – {end_str}.",
                "CRITICAL",
                "E",
            )
        else:
            self._pass("POLICY_DATE_WINDOW")

        # Coverage ceiling
        if coverage and claim_amount > coverage:
            self._fail(
                "CLAIM_EXCEEDS_COVERAGE",
                "Policy Coverage Limit Check (v2 NEW)",
                (
                    f"Claim ₹{claim_amount:,} exceeds policy coverage "
                    f"₹{coverage:,}. Requires agent to assess partial payout."
                ),
                "MEDIUM",
                "E",
            )
        else:
            self._pass("COVERAGE_ADEQUATE")

    # CHECK 16 (NEW): Duplicate / Repeat-Claim Guard
    # ─────────────────────────────────────────────────
    def _check_16_duplicate_claim_guard(
        self,
        ai: Dict[str, Any],
        policy: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]],
    ) -> None:
        """
        Flag if the same license plate or policy has an open/recent claim.

        history : list of dicts, each with keys:
            { claim_id, status, created_at (ISO str), vehicle_registration }
        """
        if not history:
            self._pass("DUPLICATE_CLAIM_NOT_APPLICABLE")
            return

        ocr          = ai.get("ocr_data", {}) or {}
        this_plate   = (
            (ocr.get("plate_text") or policy.get("vehicle_registration") or "")
            .upper().replace(" ", "").replace("-", "")
        )
        window_days  = self.config.DUPLICATE_CLAIM_WINDOW_DAYS
        now          = datetime.utcnow()

        recent_open: List[int] = []
        same_plate_recent: List[int] = []

        for prior in history:
            prior_status = (prior.get("status") or "").lower()
            prior_plate  = (
                (prior.get("vehicle_registration") or "")
                .upper().replace(" ", "").replace("-", "")
            )
            try:
                prior_date = datetime.fromisoformat(str(prior.get("created_at", "")))
                age_days   = (now - prior_date).days
            except (ValueError, TypeError):
                age_days = 999

            if prior_status in ("pending", "processing"):
                recent_open.append(prior.get("claim_id", 0))

            if (
                this_plate
                and prior_plate == this_plate
                and age_days <= window_days
                and prior_status not in ("rejected",)
            ):
                same_plate_recent.append(prior.get("claim_id", 0))

        if recent_open:
            self._fail(
                "DUPLICATE_OPEN_CLAIM",
                "Duplicate Claim Guard — Open Claim (v2 NEW)",
                (
                    f"Policy already has open/processing claim(s): "
                    f"{recent_open}. New claim flagged for review."
                ),
                "HIGH",
                "E",
            )

        if same_plate_recent:
            self._fail(
                "DUPLICATE_PLATE_RECENT",
                "Duplicate Claim Guard — Recent Plate (v2 NEW)",
                (
                    f"Plate {this_plate!r} has {len(same_plate_recent)} recent "
                    f"claim(s) within {window_days} days: {same_plate_recent}. "
                    "Possible staged-accident fraud ring."
                ),
                "HIGH",
                "E",
            )

        if not recent_open and not same_plate_recent:
            self._pass("NO_DUPLICATE_CLAIMS")

    # =========================================================================
    # FINAL DECISION
    # =========================================================================

    def _make_final_decision(self, claim_amount: int) -> VerificationResult:
        """
        Compute the final decision using:
        1. Raw severity score (with optional compounding)
        2. Critical-failure fast path
        3. Weighted confidence score (0-100)
        """
        critical_count = sum(1 for r in self._failed if r.severity == "CRITICAL")
        high_count     = sum(1 for r in self._failed if r.severity == "HIGH")

        # Compounding multiplier for correlated failures
        severe_failure_count = critical_count + high_count
        final_score = self._raw_score
        if severe_failure_count >= self.config.COMPOUND_FAILURE_THRESHOLD:
            final_score *= self.config.COMPOUND_MULTIPLIER

        # Weighted confidence score (100 = perfect, 0 = total failure)
        max_possible = len(self._passed) + len(self._failed)
        raw_pass_rate = (len(self._passed) / max_possible) if max_possible else 1.0
        # Penalise by severity: each CRITICAL reduces confidence more than LOW
        severity_penalty = min(final_score / 50.0, 1.0)   # cap at 1.0
        confidence_score = max(0.0, (raw_pass_rate - severity_penalty)) * 100.0

        # Decision logic
        if not self._failed:
            return self._build(
                "APPROVED",
                "All verification checks passed.",
                "HIGH",
                confidence_score,
                auto_approved=True,
                review=False,
                monitor=False,
                score=final_score,
            )

        if critical_count > 0:
            return self._build(
                "REJECTED",
                f"{critical_count} critical fraud indicator(s) detected.",
                "HIGH",
                confidence_score,
                auto_approved=False,
                review=True,
                monitor=False,
                score=final_score,
            )

        if final_score >= self.config.AUTO_REJECT_SCORE_THRESHOLD:
            return self._build(
                "REJECTED",
                f"Multiple fraud indicators accumulated (severity score: {final_score:.1f}).",
                "HIGH",
                confidence_score,
                auto_approved=False,
                review=True,
                monitor=False,
                score=final_score,
            )

        if final_score >= self.config.FLAG_FOR_REVIEW_SCORE_THRESHOLD:
            return self._build(
                "FLAGGED",
                "Verification issues require human review.",
                "MEDIUM",
                confidence_score,
                auto_approved=False,
                review=True,
                monitor=False,
                score=final_score,
            )

        # Only LOW issues
        return self._build(
            "APPROVED",
            "Minor verification issues within acceptable range.",
            "MEDIUM",
            confidence_score,
            auto_approved=True,
            review=False,
            monitor=True,
            score=final_score,
        )

    def _build(
        self,
        status: str,
        reason: str,
        confidence_level: str,
        confidence_score: float,
        auto_approved: bool,
        review: bool,
        monitor: bool,
        score: float,
    ) -> VerificationResult:
        return VerificationResult(
            status=status,
            decision_reason=reason,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            auto_approved=auto_approved,
            requires_human_review=review,
            requires_monitoring=monitor,
            severity_score=score,
            passed_checks=list(self._passed),
            failed_checks=list(self._failed),
            timestamp=datetime.utcnow().isoformat(),
        )

    # =========================================================================
    # UTILITIES
    # =========================================================================

    @staticmethod
    def _location_matches(loc1: str, loc2: str) -> bool:
        """Token overlap location match (enhance with geocoding if needed)."""
        tokens1 = set(loc1.lower().replace(",", " ").split())
        tokens2 = set(loc2.lower().replace(",", " ").split())
        stopwords = {"the", "of", "and", "in", "at", "near"}
        tokens1 -= stopwords
        tokens2 -= stopwords
        return bool(tokens1 & tokens2)
