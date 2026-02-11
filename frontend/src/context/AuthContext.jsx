import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check local storage for an existing session
    const storedUser = localStorage.getItem('pharma_user');
    if (storedUser) {
      setCurrentUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    // For demo purposes, we'll accept any login or check against a hardcoded credential
    // In a real app, this would verify with Firebase or the Backend
    console.log("Logging in with:", email);
    
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 800));

    // Create a mock user object
    // Assuming if they login on Pharmacy portal, they are a pharmacist
    const user = {
      uid: 'mock-user-id-' + Date.now(),
      email: email,
      role: 'pharmacist',
      profile: {
        role: 'pharmacist'
      }
    };

    setCurrentUser(user);
    localStorage.setItem('pharma_user', JSON.stringify(user));
    return user;
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('pharma_user');
  };

  const value = {
    currentUser,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
