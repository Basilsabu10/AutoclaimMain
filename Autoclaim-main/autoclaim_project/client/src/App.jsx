import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

// New components
import Navbar from "./components/Navbar";
import Homepage from "./pages/Homepage";
import SubmitClaim from "./pages/SubmitClaim";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ClaimUpload from "./components/ClaimUpload";
import UserDashboard from "./components/UserDashboard";
import AdminDashboard from "./components/AdminDashboard";
import AgentDashboard from "./components/AgentDashboard";
import AITestPage from "./components/AITestPage";
import ViewClaim from "./components/ViewClaim";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <div className="app-root min-vh-100">
        <Navbar />

        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Homepage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes - Any authenticated user */}
          <Route
            path="/submit-claim"
            element={
              <ProtectedRoute>
                <SubmitClaim />
              </ProtectedRoute>
            }
          />

          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <ClaimUpload />
              </ProtectedRoute>
            }
          />

          {/* Claim Detail View */}
          <Route
            path="/claim/:id"
            element={
              <ProtectedRoute>
                <ViewClaim />
              </ProtectedRoute>
            }
          />

          {/* AI Test Page */}
          <Route
            path="/ai-test"
            element={
              <ProtectedRoute>
                <AITestPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes - User only */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredRole="user">
                <UserDashboard />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes - Agent only */}
          <Route
            path="/agent"
            element={
              <ProtectedRoute requiredRole="agent">
                <AgentDashboard />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes - Admin only */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Track Claim - placeholder for now */}
          <Route
            path="/track-claim"
            element={
              <div className="container py-5 text-center">
                <h2>Track Your Claim</h2>
                <p>This feature is coming soon. For now, please login to view your claims in the dashboard.</p>
              </div>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;