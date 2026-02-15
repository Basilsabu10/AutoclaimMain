import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function AgentDashboard() {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchAllClaims();
    }, []);

    const fetchAllClaims = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:8000/claims/all", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.status === 401 || response.status === 403) {
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                navigate("/");
                return;
            }

            const data = await response.json();
            setClaims(data.claims || []);
        } catch (error) {
            console.error("Failed to fetch claims:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        navigate("/");
    };

    const handleViewClaim = (claimId) => {
        navigate(`/claim/${claimId}`);
    };

    const getStatusBadge = (status) => {
        const statusClasses = {
            pending: "status-pending",
            approved: "status-approved",
            rejected: "status-rejected",
        };
        return <span className={`status-badge ${statusClasses[status]}`}>{status}</span>;
    };

    return (
        <div className="dashboard-container agent">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <div className="logo agent-logo">AC</div>
                    <h1>Agent Dashboard</h1>
                </div>
                <div className="header-right">
                    <span className="agent-badge">AGENT</span>
                    <button onClick={handleLogout} className="logout-btn">Logout</button>
                </div>
            </header>

            {/* Main Content */}
            <main className="dashboard-main">
                {/* Stats Cards */}
                <div className="stats-row">
                    <div className="stat-card">
                        <div className="stat-icon">📋</div>
                        <div className="stat-info">
                            <span className="stat-value">{claims.length}</span>
                            <span className="stat-label">Total Claims</span>
                        </div>
                    </div>
                    <div className="stat-card warning">
                        <div className="stat-icon">⏳</div>
                        <div className="stat-info">
                            <span className="stat-value">{claims.filter(c => c.status === "pending").length}</span>
                            <span className="stat-label">Pending Review</span>
                        </div>
                    </div>
                    <div className="stat-card success">
                        <div className="stat-icon">✅</div>
                        <div className="stat-info">
                            <span className="stat-value">{claims.filter(c => c.status === "approved").length}</span>
                            <span className="stat-label">Approved</span>
                        </div>
                    </div>
                    <div className="stat-card danger">
                        <div className="stat-icon">❌</div>
                        <div className="stat-info">
                            <span className="stat-value">{claims.filter(c => c.status === "rejected").length}</span>
                            <span className="stat-label">Rejected</span>
                        </div>
                    </div>
                </div>

                {/* Claims Table */}
                <div className="claims-section">
                    <h2>All Claims</h2>

                    {loading ? (
                        <div className="loading">Loading claims...</div>
                    ) : claims.length === 0 ? (
                        <div className="empty-state">
                            <p>No claims have been submitted yet.</p>
                        </div>
                    ) : (
                        <div className="claims-table-wrapper">
                            <table className="claims-table agent-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>User</th>
                                        <th>Description</th>
                                        <th>Vehicle #</th>
                                        <th>Images</th>
                                        <th>Status</th>
                                        <th>AI Recommendation</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {claims.map((claim) => (
                                        <tr key={claim.id}>
                                            <td>#{claim.id}</td>
                                            <td className="user-cell">{claim.user_email}</td>
                                            <td className="description-cell">{claim.description || "No description"}</td>
                                            <td>{claim.vehicle_number_plate || "N/A"}</td>
                                            <td>{claim.images_count} 📷</td>
                                            <td>{getStatusBadge(claim.status)}</td>
                                            <td>
                                                {claim.ai_recommendation ? (
                                                    <span className={`ai-badge ${claim.ai_recommendation.toLowerCase()}`}>
                                                        {claim.ai_recommendation}
                                                    </span>
                                                ) : (
                                                    "N/A"
                                                )}
                                            </td>
                                            <td>{new Date(claim.created_at).toLocaleDateString()}</td>
                                            <td className="actions-cell">
                                                <button
                                                    className="action-btn view"
                                                    onClick={() => handleViewClaim(claim.id)}
                                                >
                                                    👁️ View
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

export default AgentDashboard;
