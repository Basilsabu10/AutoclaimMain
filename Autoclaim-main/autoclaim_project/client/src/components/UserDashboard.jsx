import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import Navbar from "./Navbar";
import "./Dashboard.css";

function UserDashboard() {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);
    const [userEmail, setUserEmail] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        fetchClaims();
    }, []);

    const fetchClaims = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:8000/claims/my", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem("token");
                localStorage.removeItem("role");
                navigate("/");
                return;
            }

            const data = await response.json();
            setClaims(data.claims || []);
            setUserEmail(data.user_email || "");
        } catch (error) {
            console.error("Failed to fetch claims:", error);
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
        return <span className={`status-badge ${statusClasses[status]}`}>{status}</span>;
    };

    const handleClaimClick = (claimId) => {
        navigate(`/claim/${claimId}`);
    };

    return (
        <>
            <Navbar />
            <div className="dashboard-container">
                {/* Header */}
                <header className="dashboard-header">
                    <div className="header-left">
                        <div className="logo">AC</div>
                        <h1>AUTOCLAIM Dashboard</h1>
                    </div>
                    <div className="header-right">
                        <span className="user-email">{userEmail}</span>
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
                        <div className="stat-card">
                            <div className="stat-icon">⏳</div>
                            <div className="stat-info">
                                <span className="stat-value">{claims.filter(c => c.status === "pending").length}</span>
                                <span className="stat-label">Pending</span>
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-icon">✅</div>
                            <div className="stat-info">
                                <span className="stat-value">{claims.filter(c => c.status === "approved").length}</span>
                                <span className="stat-label">Approved</span>
                            </div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-icon">❌</div>
                            <div className="stat-info">
                                <span className="stat-value">{claims.filter(c => c.status === "rejected").length}</span>
                                <span className="stat-label">Rejected</span>
                            </div>
                        </div>
                    </div>

                    {/* Action Button */}
                    <div className="action-row">
                        <Link to="/upload" className="new-claim-btn">
                            + Submit New Claim
                        </Link>
                    </div>

                    {/* Claims Table */}
                    <div className="claims-section">
                        <h2>Your Claims</h2>

                        {loading ? (
                            <div className="loading">Loading claims...</div>
                        ) : claims.length === 0 ? (
                            <div className="empty-state">
                                <p>No claims submitted yet.</p>
                                <Link to="/upload">Submit your first claim</Link>
                            </div>
                        ) : (
                            <div className="claims-table-wrapper">
                                <table className="claims-table">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Description</th>
                                            <th>Images</th>
                                            <th>Status</th>
                                            <th>Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {claims.map((claim) => (
                                            <tr
                                                key={claim.id}
                                                onClick={() => handleClaimClick(claim.id)}
                                                className="clickable-row"
                                            >
                                                <td>#{claim.id}</td>
                                                <td className="description-cell">{claim.description || "No description"}</td>
                                                <td>{claim.images_count} 📷</td>
                                                <td>{getStatusBadge(claim.status)}</td>
                                                <td>{new Date(claim.created_at).toLocaleDateString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </>
    );
}

export default UserDashboard;

