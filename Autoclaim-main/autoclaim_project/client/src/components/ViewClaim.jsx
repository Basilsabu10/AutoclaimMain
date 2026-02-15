import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./ViewClaim.css";

function ViewClaim() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [claim, setClaim] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchClaimDetails();

        // Set up polling for processing status
        const pollInterval = setInterval(async () => {
            // Only poll if claim exists and is still processing
            if (claim && (claim.processing_status === "pending" || claim.processing_status === "processing")) {
                fetchClaimDetails();
            }
        }, 3000); // Poll every 3 seconds

        // Cleanup interval on unmount
        return () => clearInterval(pollInterval);
    }, [id, claim?.processing_status]);

    const fetchClaimDetails = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/claims/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.status === 401) {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                navigate("/");
                return;
            }

            if (!response.ok) {
                throw new Error("Failed to fetch claim details");
            }

            const data = await response.json();
            setClaim(data);

            // Stop loading only if processing is complete or failed
            if (data.processing_status === "completed" || data.processing_status === "failed") {
                setLoading(false);
            } else if (!claim) {
                // First load, show loading
                setLoading(false);
            }
        } catch (error) {
            console.error("Error fetching claim:", error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const statusClasses = {
            pending: "status-pending",
            approved: "status-approved",
            rejected: "status-rejected",
        };
        return <span className={`status-badge ${statusClasses[status]}`}>{status?.toUpperCase()}</span>;
    };

    const formatCurrency = (min, max) => {
        if (!min && !max) return "N/A";
        if (min && max) return `$${min} - $${max}`;
        return `$${min || max}`;
    };

    if (loading) {
        return (
            <>
                <Navbar />
                <div className="view-claim-container">
                    <div className="loading-spinner">Loading claim details...</div>
                </div>
            </>
        );
    }

    if (error || !claim) {
        return (
            <>
                <Navbar />
                <div className="view-claim-container">
                    <div className="error-message">
                        <h2>Error Loading Claim</h2>
                        <p>{error || "Claim not found"}</p>
                        <button onClick={() => navigate("/dashboard")} className="back-btn">
                            Return to Dashboard
                        </button>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div className="view-claim-container">
                <div className="view-claim-header">
                    <button onClick={() => navigate(-1)} className="back-btn">
                        ← Back
                    </button>
                    <h1>Claim Details #{claim.id}</h1>
                </div>

                {/* Processing Status Banner */}
                {(claim.processing_status === "pending" || claim.processing_status === "processing") && (
                    <div className="processing-banner" style={{
                        backgroundColor: '#fff3cd',
                        border: '2px solid #ffc107',
                        borderRadius: '8px',
                        padding: '15px 20px',
                        marginBottom: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '15px'
                    }}>
                        <div className="spinner" style={{
                            width: '24px',
                            height: '24px',
                            border: '3px solid #f3f3f3',
                            borderTop: '3px solid #ffc107',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite'
                        }}></div>
                        <div>
                            <strong>🔄 Rule-Based Verification in Progress...</strong>
                            <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
                                Analyzing your claim with 8 fraud detection rules and AI image analysis. This usually takes 10-30 seconds.
                            </p>
                        </div>
                    </div>
                )}

                {claim.processing_status === "failed" && (
                    <div className="processing-banner" style={{
                        backgroundColor: '#f8d7da',
                        border: '2px solid #dc3545',
                        borderRadius: '8px',
                        padding: '15px 20px',
                        marginBottom: '20px'
                    }}>
                        <strong>⚠️ Verification Analysis Failed</strong>
                        <p style={{ margin: '5px 0 0 0', fontSize: '14px' }}>
                            There was an error processing your claim. Our team will review it manually.
                        </p>
                    </div>
                )}

                <div className="claim-grid">
                    {/* Basic Information */}
                    <div className="claim-card">
                        <h2>📋 Basic Information</h2>
                        <div className="info-grid">
                            <div className="info-item">
                                <span className="info-label">Status</span>
                                {getStatusBadge(claim.status)}
                            </div>
                            <div className="info-item">
                                <span className="info-label">Submitted By</span>
                                <span className="info-value">{claim.user_email}</span>
                            </div>
                            <div className="info-item">
                                <span className="info-label">Submission Date</span>
                                <span className="info-value">
                                    {new Date(claim.created_at).toLocaleString()}
                                </span>
                            </div>
                            {claim.accident_date && (
                                <div className="info-item">
                                    <span className="info-label">Accident Date</span>
                                    <span className="info-value">
                                        {new Date(claim.accident_date).toLocaleDateString()}
                                    </span>
                                </div>
                            )}
                            {claim.vehicle_number_plate && (
                                <div className="info-item">
                                    <span className="info-label">Vehicle Plate</span>
                                    <span className="info-value plate-number">{claim.vehicle_number_plate}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Claim Description */}
                    {claim.description && (
                        <div className="claim-card full-width">
                            <h2>📝 Claim Description</h2>
                            <p className="description-text">{claim.description}</p>
                        </div>
                    )}

                    {/* Rule-Based Verification Results */}
                    {claim.forensic_analysis && (
                        <>
                            {/* Verification Decision */}
                            <div className="claim-card full-width">
                                <h2>⚖️ Rule-Based Verification Decision</h2>
                                <div className="info-grid">
                                    <div className="info-item">
                                        <span className="info-label">Verification Status</span>
                                        <span className={`ai-badge ${claim.ai_recommendation || claim.status}`}>
                                            {(claim.ai_recommendation || claim.status)?.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Severity Score</span>
                                        <span className="info-value">
                                            {claim.forensic_analysis.overall_confidence_score || 0}
                                        </span>
                                    </div>
                                    {claim.estimated_cost_min && claim.estimated_cost_max && (
                                        <div className="info-item">
                                            <span className="info-label">Estimated Repair Cost</span>
                                            <span className="info-value cost">
                                                ₹{claim.estimated_cost_min?.toLocaleString()} - ₹{claim.estimated_cost_max?.toLocaleString()}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {claim.forensic_analysis.ai_reasoning && (
                                    <div className="reasoning-section">
                                        <span className="info-label">Decision Reason:</span>
                                        <p className="reasoning-text">{claim.forensic_analysis.ai_reasoning}</p>
                                    </div>
                                )}

                                {/* Failed Checks */}
                                {claim.forensic_analysis.ai_risk_flags && claim.forensic_analysis.ai_risk_flags.length > 0 && (
                                    <div className="risk-flags" style={{ marginTop: '20px' }}>
                                        <h3 style={{ color: '#dc3545', marginBottom: '15px' }}>
                                            ⚠️ Failed Verification Checks ({claim.forensic_analysis.ai_risk_flags.length})
                                        </h3>
                                        <div className="flags-list">
                                            {claim.forensic_analysis.ai_risk_flags.map((flag, index) => (
                                                <div key={index} style={{
                                                    backgroundColor: '#f8d7da',
                                                    border: '1px solid #f5c2c7',
                                                    borderRadius: '6px',
                                                    padding: '12px 15px',
                                                    marginBottom: '10px',
                                                    fontSize: '14px',
                                                    color: '#842029'
                                                }}>
                                                    <strong>❌ {flag}</strong>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Passed Checks Indicator */}
                                {(!claim.forensic_analysis.ai_risk_flags || claim.forensic_analysis.ai_risk_flags.length === 0) && (
                                    <div style={{
                                        marginTop: '20px',
                                        backgroundColor: '#d1e7dd',
                                        border: '1px solid #badbcc',
                                        borderRadius: '6px',
                                        padding: '15px',
                                        color: '#0f5132'
                                    }}>
                                        <strong>✅ All Verification Checks Passed</strong>
                                        <p style={{ margin: '5px 0 0 0', fontSize: '14px' }}>
                                            This claim passed all 8 fraud detection rules and is eligible for processing.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </>
                    )}

                    {/* Forensic Analysis */}
                    {claim.forensic_analysis && (
                        <>
                            {/* Fraud Detection & Risk Assessment */}
                            <div className="claim-card">
                                <h2>🚨 Fraud Detection & Risk Assessment</h2>
                                <div className="info-grid">
                                    <div className="info-item">
                                        <span className="info-label">Authenticity Score</span>
                                        <span className={`score-badge ${claim.forensic_analysis.authenticity_score >= 80 ? 'high' : claim.forensic_analysis.authenticity_score >= 50 ? 'medium' : 'low'}`}>
                                            {claim.forensic_analysis.authenticity_score ? `${claim.forensic_analysis.authenticity_score}/100` : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Fraud Probability</span>
                                        <span className={`fraud-badge ${claim.forensic_analysis.fraud_probability < 30 ? 'low' : claim.forensic_analysis.fraud_probability < 70 ? 'medium' : 'high'}`}>
                                            {claim.forensic_analysis.fraud_probability ? `${claim.forensic_analysis.fraud_probability}%` : 'N/A'}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Forgery Detected</span>
                                        <span className={`badge ${claim.forensic_analysis.forgery_detected ? 'danger' : 'success'}`}>
                                            {claim.forensic_analysis.forgery_detected ? '⚠️ YES' : '✓ NO'}
                                        </span>
                                    </div>
                                    <div className="info-item">
                                        <span className="info-label">Confidence Score</span>
                                        <span className="info-value">{claim.forensic_analysis.confidence_score || 'N/A'}/100</span>
                                    </div>
                                </div>

                                {claim.forensic_analysis.risk_flags && claim.forensic_analysis.risk_flags.length > 0 && (
                                    <div className="risk-flags">
                                        <span className="info-label">⚠️ Risk Flags:</span>
                                        <div className="flags-list">
                                            {claim.forensic_analysis.risk_flags.map((flag, index) => (
                                                <span key={index} className="risk-tag">{flag}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Vehicle Identification */}
                            <div className="claim-card">
                                <h2>🚗 Vehicle Identification (AI)</h2>
                                <div className="info-grid">
                                    {claim.forensic_analysis.vehicle_make && (
                                        <div className="info-item">
                                            <span className="info-label">Make</span>
                                            <span className="info-value">{claim.forensic_analysis.vehicle_make}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.vehicle_model && (
                                        <div className="info-item">
                                            <span className="info-label">Model</span>
                                            <span className="info-value">{claim.forensic_analysis.vehicle_model}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.vehicle_year && (
                                        <div className="info-item">
                                            <span className="info-label">Year</span>
                                            <span className="info-value">{claim.forensic_analysis.vehicle_year}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.vehicle_color && (
                                        <div className="info-item">
                                            <span className="info-label">Color</span>
                                            <span className="info-value">{claim.forensic_analysis.vehicle_color}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.license_plate_text && (
                                        <div className="info-item">
                                            <span className="info-label">License Plate (OCR)</span>
                                            <span className="info-value plate-number">{claim.forensic_analysis.license_plate_text}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.license_plate_match_status && (
                                        <div className="info-item">
                                            <span className="info-label">Plate Verification</span>
                                            <span className={`badge ${claim.forensic_analysis.license_plate_match_status === 'MATCH' ? 'success' : claim.forensic_analysis.license_plate_match_status === 'MISMATCH' ? 'danger' : 'warning'}`}>
                                                {claim.forensic_analysis.license_plate_match_status}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* YOLO Damage Detection */}
                            {claim.forensic_analysis.yolo_damage_detected && (
                                <div className="claim-card">
                                    <h2>🎯 YOLO Damage Detection (GPU-Accelerated)</h2>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Damage Detected</span>
                                            <span className="badge success">✓ YES</span>
                                        </div>
                                        {claim.forensic_analysis.yolo_severity && (
                                            <div className="info-item">
                                                <span className="info-label">YOLO Severity</span>
                                                <span className={`severity-badge ${claim.forensic_analysis.yolo_severity}`}>
                                                    {claim.forensic_analysis.yolo_severity.toUpperCase()}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                    {claim.forensic_analysis.yolo_summary && (
                                        <div className="reasoning-section">
                                            <span className="info-label">YOLO Summary:</span>
                                            <p className="reasoning-text">{claim.forensic_analysis.yolo_summary}</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* AI Damage Assessment */}
                            <div className="claim-card">
                                <h2>🤖 AI Damage Assessment (Groq)</h2>
                                <div className="info-grid">
                                    {claim.forensic_analysis.ai_damage_type && (
                                        <div className="info-item">
                                            <span className="info-label">Damage Type</span>
                                            <span className="info-value">{claim.forensic_analysis.ai_damage_type}</span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.ai_severity && (
                                        <div className="info-item">
                                            <span className="info-label">Severity Level</span>
                                            <span className={`severity-badge ${claim.forensic_analysis.ai_severity}`}>
                                                {claim.forensic_analysis.ai_severity.toUpperCase()}
                                            </span>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.ai_structural_damage !== null && (
                                        <div className="info-item">
                                            <span className="info-label">Structural Damage</span>
                                            <span className={`badge ${claim.forensic_analysis.ai_structural_damage ? 'danger' : 'success'}`}>
                                                {claim.forensic_analysis.ai_structural_damage ? '⚠️ YES' : '✓ NO'}
                                            </span>
                                        </div>
                                    )}
                                    {(claim.forensic_analysis.ai_cost_min || claim.forensic_analysis.ai_cost_max) && (
                                        <div className="info-item">
                                            <span className="info-label">AI Cost Estimate</span>
                                            <span className="info-value cost">
                                                ₹{claim.forensic_analysis.ai_cost_min?.toLocaleString()} - ₹{claim.forensic_analysis.ai_cost_max?.toLocaleString()}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {claim.forensic_analysis.ai_affected_parts && claim.forensic_analysis.ai_affected_parts.length > 0 && (
                                    <div className="affected-parts">
                                        <span className="info-label">Affected Parts:</span>
                                        <div className="parts-list">
                                            {claim.forensic_analysis.ai_affected_parts.map((part, index) => (
                                                <span key={index} className="part-tag">{part}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {claim.forensic_analysis.ai_safety_concerns && claim.forensic_analysis.ai_safety_concerns.length > 0 && (
                                    <div className="safety-concerns">
                                        <span className="info-label">⚠️ Safety Concerns:</span>
                                        <ul>
                                            {claim.forensic_analysis.ai_safety_concerns.map((concern, index) => (
                                                <li key={index}>{concern}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {claim.forensic_analysis.ai_reasoning && (
                                    <div className="reasoning-section">
                                        <span className="info-label">AI Reasoning:</span>
                                        <p className="reasoning-text">{claim.forensic_analysis.ai_reasoning}</p>
                                    </div>
                                )}
                            </div>

                            {/* Pre-existing Damage */}
                            {claim.forensic_analysis.pre_existing_damage_detected && (
                                <div className="claim-card">
                                    <h2>🔍 Pre-existing Damage Detection</h2>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="info-label">Pre-existing Damage</span>
                                            <span className="badge warning">⚠️ DETECTED</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="info-label">Confidence</span>
                                            <span className="info-value">{claim.forensic_analysis.pre_existing_confidence}%</span>
                                        </div>
                                    </div>
                                    {claim.forensic_analysis.pre_existing_description && (
                                        <div className="reasoning-section">
                                            <span className="info-label">Description:</span>
                                            <p className="reasoning-text">{claim.forensic_analysis.pre_existing_description}</p>
                                        </div>
                                    )}
                                    {claim.forensic_analysis.pre_existing_indicators && claim.forensic_analysis.pre_existing_indicators.length > 0 && (
                                        <div className="indicators">
                                            <span className="info-label">Indicators:</span>
                                            <div className="parts-list">
                                                {claim.forensic_analysis.pre_existing_indicators.map((indicator, index) => (
                                                    <span key={index} className="part-tag">{indicator}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Image Metadata */}
                            {(claim.forensic_analysis.exif_timestamp || claim.forensic_analysis.exif_location_name) && (
                                <div className="claim-card">
                                    <h2>📸 Image Metadata (EXIF)</h2>
                                    <div className="info-grid">
                                        {claim.forensic_analysis.exif_timestamp && (
                                            <div className="info-item">
                                                <span className="info-label">Photo Timestamp</span>
                                                <span className="info-value">
                                                    {new Date(claim.forensic_analysis.exif_timestamp).toLocaleString()}
                                                </span>
                                            </div>
                                        )}
                                        {claim.forensic_analysis.exif_location_name && (
                                            <div className="info-item">
                                                <span className="info-label">Location</span>
                                                <span className="info-value">{claim.forensic_analysis.exif_location_name}</span>
                                            </div>
                                        )}
                                        {claim.forensic_analysis.exif_camera_make && (
                                            <div className="info-item">
                                                <span className="info-label">Camera</span>
                                                <span className="info-value">
                                                    {claim.forensic_analysis.exif_camera_make} {claim.forensic_analysis.exif_camera_model}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </>
                    )}

                    {/* Uploaded Images */}
                    {(claim.image_paths?.length > 0 || claim.front_image_path || claim.case_number_image_path || claim.estimate_bill_path) && (
                        <div className="claim-card full-width">
                            <h2>📷 Uploaded Files</h2>

                            {claim.image_paths?.length > 0 && (
                                <div className="image-section">
                                    <h3>Damage Images ({claim.image_paths.length})</h3>
                                    <div className="image-gallery">
                                        {claim.image_paths.map((path, index) => (
                                            <div key={index} className="image-item">
                                                <img
                                                    src={`http://localhost:8000/uploads/${path.split('/').pop()}`}
                                                    alt={`Damage ${index + 1}`}
                                                    onError={(e) => {
                                                        e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23ddd' width='200' height='200'/%3E%3Ctext fill='%23999' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EImage Not Found%3C/text%3E%3C/svg%3E";
                                                    }}
                                                />
                                                <span className="image-label">Damage {index + 1}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {claim.front_image_path && (
                                <div className="image-section">
                                    <h3>Front View Image</h3>
                                    <div className="image-gallery">
                                        <div className="image-item">
                                            <img
                                                src={`http://localhost:8000/uploads/${claim.front_image_path.split('/').pop()}`}
                                                alt="Front View"
                                                onError={(e) => {
                                                    e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23ddd' width='200' height='200'/%3E%3Ctext fill='%23999' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EImage Not Found%3C/text%3E%3C/svg%3E";
                                                }}
                                            />
                                            <span className="image-label">Front View</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {claim.case_number_image_path && (
                                <div className="image-section">
                                    <h3>Case Number Image</h3>
                                    <div className="image-gallery">
                                        <div className="image-item">
                                            <img
                                                src={`http://localhost:8000/uploads/${claim.case_number_image_path.split('/').pop()}`}
                                                alt="Case Number"
                                                className="img-fluid"
                                                style={{ maxWidth: '300px', borderRadius: '8px' }}
                                                onError={(e) => {
                                                    e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23ddd' width='200' height='200'/%3E%3Ctext fill='%23999' x='50%25' y='50%25' text-anchor='middle' dy='.3em'%3EImage Not Found%3C/text%3E%3C/svg%3E";
                                                }}
                                            />
                                            <span className="image-label">Case Number</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {claim.estimate_bill_path && (
                                <div className="image-section">
                                    <h3>Estimate Bill</h3>
                                    <div className="file-item">
                                        <span>📄 {claim.estimate_bill_path.split('/').pop()}</span>
                                        <a
                                            href={`http://localhost:8000/uploads/${claim.estimate_bill_path.split('/').pop()}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="view-file-btn"
                                        >
                                            View File
                                        </a>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

export default ViewClaim;
