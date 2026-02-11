import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import PharmacyLogin from './components/PharmacyLogin';
import PharmacySignup from './components/PharmacySignup';
import PharmaPortal from './components/PharmacyPortal';
import { useAuth } from './context/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { currentUser } = useAuth();
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<PharmacyLogin />} />
      <Route path="/signup" element={<PharmacySignup />} />
      
      {/* Protected Routes */}
      <Route 
        path="/portal/*" 
        element={
          <ProtectedRoute>
            <PharmaPortal />
          </ProtectedRoute>
        } 
      />
      
      {/* Default Redirect */}
      <Route path="/" element={<Navigate to="/portal/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/portal/dashboard" replace />} />

    </Routes>
  );
}

export default App;
