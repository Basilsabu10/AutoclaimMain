import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

function Navbar() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userEmail, setUserEmail] = useState('');
    const [userName, setUserName] = useState('');
    const [userRole, setUserRole] = useState('');
    const navigate = useNavigate();
    const location = useLocation(); // Track route changes

    // Function to check and update authentication status
    const checkAuthStatus = () => {
        const token = localStorage.getItem('token');
        const role = localStorage.getItem('role');
        const email = localStorage.getItem('userEmail');

        if (token) {
            setIsAuthenticated(true);
            setUserRole(role || '');
            setUserEmail(email || '');
            // Extract username from email (part before @)
            setUserName(email ? email.split('@')[0] : 'User');
        } else {
            setIsAuthenticated(false);
            setUserEmail('');
            setUserName('');
            setUserRole('');
        }
    };

    // Check authentication status on mount, route changes, and storage events
    useEffect(() => {
        checkAuthStatus();

        // Listen for storage changes (from other tabs/windows)
        window.addEventListener('storage', checkAuthStatus);

        // Listen for custom login event (from same window)
        window.addEventListener('userLoggedIn', checkAuthStatus);

        return () => {
            window.removeEventListener('storage', checkAuthStatus);
            window.removeEventListener('userLoggedIn', checkAuthStatus);
        };
    }, [location]); // Re-run when location changes

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('userEmail');
        checkAuthStatus(); // Update state immediately
        setUserEmail('');
        setUserRole('');
        navigate('/');
    };

    return (
        <nav className="navbar navbar-expand-md header-nav px-4">
            <Link className="navbar-brand d-flex align-items-center" to="/">
                <div className="brand-logo rounded-circle d-flex align-items-center justify-content-center me-2">
                    <span className="shield-icon">🛡️</span>
                </div>
                <span className="fw-bold">AutoClaim</span>
            </Link>

            <button
                className="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#mainNavbar"
                aria-controls="mainNavbar"
                aria-expanded="false"
                aria-label="Toggle navigation"
            >
                <span className="navbar-toggler-icon"></span>
            </button>

            <div className="collapse navbar-collapse" id="mainNavbar">
                <ul className="navbar-nav ms-auto align-items-center">
                    <li className="nav-item">
                        <Link className="nav-link" to="/">
                            Home
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link" to="/submit-claim">
                            Submit Claim
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link className="nav-link" to="/track-claim">
                            Track Claim
                        </Link>
                    </li>

                    {isAuthenticated && (
                        <li className="nav-item">
                            <Link
                                className="nav-link"
                                to={
                                    userRole === 'admin' ? '/admin' :
                                        userRole === 'agent' ? '/agent' :
                                            '/dashboard'
                                }
                            >
                                Dashboard
                            </Link>
                        </li>
                    )}

                    {/* Not authenticated - show Login & Register buttons */}
                    {!isAuthenticated ? (
                        <>
                            <li className="nav-item ms-2">
                                <Link
                                    to="/login"
                                    className="btn btn-outline-secondary rounded-pill px-3"
                                    style={{
                                        borderColor: '#7392B7',
                                        color: '#35516b',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    Login
                                </Link>
                            </li>
                            <li className="nav-item ms-2">
                                <Link
                                    to="/register"
                                    className="btn btn-teal rounded-pill px-3"
                                    style={{ fontSize: '0.9rem' }}
                                >
                                    Register
                                </Link>
                            </li>
                        </>
                    ) : (
                        /* Authenticated - show user dropdown */
                        <li className="nav-item dropdown ms-3">
                            <button
                                className="btn btn-teal rounded-pill px-3 dropdown-toggle"
                                data-bs-toggle="dropdown"
                                aria-expanded="false"
                            >
                                👤 {userName}
                            </button>
                            <ul className="dropdown-menu dropdown-menu-end">
                                <li>
                                    <div className="dropdown-item-text">
                                        <small className="text-muted d-block">{userEmail}</small>
                                        <small className="text-muted">Role: {userRole}</small>
                                    </div>
                                </li>
                                <li><hr className="dropdown-divider" /></li>
                                <li>
                                    <Link
                                        className="dropdown-item"
                                        to={
                                            userRole === 'admin' ? '/admin' :
                                                userRole === 'agent' ? '/agent' :
                                                    '/dashboard'
                                        }
                                    >
                                        My Dashboard
                                    </Link>
                                </li>
                                <li>
                                    <button
                                        className="dropdown-item"
                                        onClick={handleLogout}
                                    >
                                        Logout
                                    </button>
                                </li>
                            </ul>
                        </li>
                    )}
                </ul>
            </div>
        </nav>
    );
}

export default Navbar;
