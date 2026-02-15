import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function AdminDashboard() {
    const [activeTab, setActiveTab] = useState("claims"); // claims or agents
    const [claims, setClaims] = useState([]);
    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(null);
    const navigate = useNavigate();

    // Agent registration form
    const [agentEmail, setAgentEmail] = useState("");
    const [agentPassword, setAgentPassword] = useState("");
    const [agentName, setAgentName] = useState("");
    const [agentFormLoading, setAgentFormLoading] = useState(false);

    useEffect(() => {
        fetchAllClaims();
        fetchAllAgents();
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

    const updateClaimStatus = async (claimId, newStatus) => {
        setUpdating(claimId);
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(
                `http://localhost:8000/claims/${claimId}/status?new_status=${newStatus}`,
                {
                    method: "PUT",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (response.ok) {
                // Update local state
                setClaims(claims.map(claim =>
                    claim.id === claimId ? { ...claim, status: newStatus } : claim
                ));
            }
        } catch (error) {
            console.error("Failed to update status:", error);
        } finally {
            setUpdating(null);
        }
    };

    const fetchAllAgents = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:8000/admin/agents", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setAgents(data.agents || []);
            }
        } catch (error) {
            console.error("Failed to fetch agents:", error);
        }
    };

    const registerAgent = async (e) => {
        e.preventDefault();
        setAgentFormLoading(true);

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(
                `http://localhost:8000/admin/register-agent?email=${encodeURIComponent(agentEmail)}&password=${encodeURIComponent(agentPassword)}&name=${encodeURIComponent(agentName)}`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (response.ok) {
                alert("Agent registered successfully!");
                setAgentEmail("");
                setAgentPassword("");
                setAgentName("");
                fetchAllAgents(); // Refresh agents list
            } else {
                const data = await response.json();
                alert("Failed to register agent: " + (data.detail || "Unknown error"));
            }
        } catch (error) {
            alert("Failed to register agent: " + error.message);
        } finally {
            setAgentFormLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        navigate("/");
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
        <div className="dashboard-container admin">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <div className="logo admin-logo">AC</div>
                    <h1>Admin Dashboard</h1>
                </div>
                <div className="header-right">
                    <span className="admin-badge">ADMIN</span>
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

                {/* Tab Navigation */}
                <div className="tabs-navigation" style={{ marginBottom: "2rem" }}>
                    <button
                        className={`tab-btn ${activeTab === "claims" ? "active" : ""}`}
                        onClick={() => setActiveTab("claims")}
                        style={{
                            padding: "0.75rem 1.5rem",
                            background: activeTab === "claims" ? "rgba(99, 102, 241, 0.2)" : "rgba(255, 255, 255, 0.05)",
                            border: activeTab === "claims" ? "1px solid rgba(99, 102, 241, 0.5)" : "1px solid rgba(255, 255, 255, 0.1)",
                            color: "white",
                            borderRadius: "8px",
                            cursor: "pointer",
                            marginRight: "1rem",
                            transition: "all 0.2s"
                        }}
                    >
                        📋 Claims Management
                    </button>
                    <button
                        className={`tab-btn ${activeTab === "agents" ? "active" : ""}`}
                        onClick={() => setActiveTab("agents")}
                        style={{
                            padding: "0.75rem 1.5rem",
                            background: activeTab === "agents" ? "rgba(99, 102, 241, 0.2)" : "rgba(255, 255, 255, 0.05)",
                            border: activeTab === "agents" ? "1px solid rgba(99, 102, 241, 0.5)" : "1px solid rgba(255, 255, 255, 0.1)",
                            color: "white",
                            borderRadius: "8px",
                            cursor: "pointer",
                            transition: "all 0.2s"
                        }}
                    >
                        👥 Agent Management
                    </button>
                </div>

                {/* Claims Section */}
                {activeTab === "claims" && (
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
                                <table className="claims-table admin-table">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>User</th>
                                            <th>Description</th>
                                            <th>Images</th>
                                            <th>Status</th>
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
                                                <td>{claim.images_count} 📷</td>
                                                <td>{getStatusBadge(claim.status)}</td>
                                                <td>{new Date(claim.created_at).toLocaleDateString()}</td>
                                                <td className="actions-cell">
                                                    {updating === claim.id ? (
                                                        <span className="updating">Updating...</span>
                                                    ) : (
                                                        <div className="action-buttons">
                                                            <button
                                                                className="action-btn approve"
                                                                onClick={() => updateClaimStatus(claim.id, "approved")}
                                                                disabled={claim.status === "approved"}
                                                            >
                                                                ✓
                                                            </button>
                                                            <button
                                                                className="action-btn reject"
                                                                onClick={() => updateClaimStatus(claim.id, "rejected")}
                                                                disabled={claim.status === "rejected"}
                                                            >
                                                                ✕
                                                            </button>
                                                            <button
                                                                className="action-btn pending"
                                                                onClick={() => updateClaimStatus(claim.id, "pending")}
                                                                disabled={claim.status === "pending"}
                                                            >
                                                                ↺
                                                            </button>
                                                        </div>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {/* Agent Management Section */}
                {activeTab === "agents" && (
                    <div className="agents-section">
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "2rem" }}>
                            {/* Agent Registration Form */}
                            <div style={{
                                background: "rgba(255, 255, 255, 0.03)",
                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                borderRadius: "16px",
                                padding: "1.5rem"
                            }}>
                                <h2 style={{ marginTop: 0 }}>Register New Agent</h2>
                                <form onSubmit={registerAgent}>
                                    <div style={{ marginBottom: "1rem" }}>
                                        <label style={{ display: "block", marginBottom: "0.5rem", color: "rgba(255, 255, 255, 0.7)" }}>
                                            Full Name
                                        </label>
                                        <input
                                            type="text"
                                            value={agentName}
                                            onChange={(e) => setAgentName(e.target.value)}
                                            required
                                            style={{
                                                width: "100%",
                                                padding: "0.75rem",
                                                background: "rgba(255, 255, 255, 0.05)",
                                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                                borderRadius: "8px",
                                                color: "white",
                                                fontSize: "1rem"
                                            }}
                                        />
                                    </div>
                                    <div style={{ marginBottom: "1rem" }}>
                                        <label style={{ display: "block", marginBottom: "0.5rem", color: "rgba(255, 255, 255, 0.7)" }}>
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            value={agentEmail}
                                            onChange={(e) => setAgentEmail(e.target.value)}
                                            required
                                            style={{
                                                width: "100%",
                                                padding: "0.75rem",
                                                background: "rgba(255, 255, 255, 0.05)",
                                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                                borderRadius: "8px",
                                                color: "white",
                                                fontSize: "1rem"
                                            }}
                                        />
                                    </div>
                                    <div style={{ marginBottom: "1.5rem" }}>
                                        <label style={{ display: "block", marginBottom: "0.5rem", color: "rgba(255, 255, 255, 0.7)" }}>
                                            Password
                                        </label>
                                        <input
                                            type="password"
                                            value={agentPassword}
                                            onChange={(e) => setAgentPassword(e.target.value)}
                                            required
                                            minLength={6}
                                            style={{
                                                width: "100%",
                                                padding: "0.75rem",
                                                background: "rgba(255, 255, 255, 0.05)",
                                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                                borderRadius: "8px",
                                                color: "white",
                                                fontSize: "1rem"
                                            }}
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={agentFormLoading}
                                        style={{
                                            width: "100%",
                                            padding: "0.75rem",
                                            background: "linear-gradient(135deg, #10b981, #06b6d4)",
                                            border: "none",
                                            borderRadius: "8px",
                                            color: "white",
                                            fontWeight: "600",
                                            cursor: agentFormLoading ? "not-allowed" : "pointer",
                                            opacity: agentFormLoading ? 0.6 : 1
                                        }}
                                    >
                                        {agentFormLoading ? "Registering..." : "Register Agent"}
                                    </button>
                                </form>
                            </div>

                            {/* Agents List */}
                            <div style={{
                                background: "rgba(255, 255, 255, 0.03)",
                                border: "1px solid rgba(255, 255, 255, 0.1)",
                                borderRadius: "16px",
                                padding: "1.5rem"
                            }}>
                                <h2 style={{ marginTop: 0 }}>Registered Agents ({agents.length})</h2>
                                {agents.length === 0 ? (
                                    <div style={{ textAlign: "center", padding: "2rem", color: "rgba(255, 255, 255, 0.5)" }}>
                                        No agents registered yet.
                                    </div>
                                ) : (
                                    <div style={{ overflowX: "auto" }}>
                                        <table className="claims-table">
                                            <thead>
                                                <tr>
                                                    <th>ID</th>
                                                    <th>Name</th>
                                                    <th>Email</th>
                                                    <th>Created</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {agents.map((agent) => (
                                                    <tr key={agent.id}>
                                                        <td>#{agent.id}</td>
                                                        <td>{agent.name}</td>
                                                        <td className="user-cell">{agent.email}</td>
                                                        <td>{new Date(agent.created_at).toLocaleDateString()}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default AdminDashboard;
