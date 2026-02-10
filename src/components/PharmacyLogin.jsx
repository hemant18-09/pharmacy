
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Pill } from 'lucide-react';
import { motion } from 'framer-motion';

const PharmacyLogin = () => {
    const navigate = useNavigate();
    const { login, currentUser } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [isLoggingIn, setIsLoggingIn] = useState(false);

    useEffect(() => {
        if (currentUser) {
            const role = currentUser.role || currentUser.profile?.role;
            if (role === 'pharmacist') {
                navigate('/portal/dashboard', { replace: true });
            }
        }
    }, [currentUser, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setError('');
            setLoading(true);
            setIsLoggingIn(true);
            await login(email, password);
        } catch (err) {
            console.error("Login Error:", err);
            if (err.code === 'auth/network-request-failed') {
                setError("Network Error: Unable to connect. Check internet.");
            } else if (err.code === 'auth/invalid-credential' || err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
                setError("Invalid email or password.");
            } else {
                setError(`Login Failed: ${err.message}`);
            }
            setLoading(false);
            setIsLoggingIn(false);
        }
    };

    return (
        <div className="min-h-screen bg-teal-700 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white p-8 md:p-12 rounded-xl shadow-2xl w-full max-w-md text-center"
            >
                {/* Logo Section */}
                <div className="flex items-center justify-center gap-2 mb-6">
                    <div className="border-2 border-teal-700 rounded-lg w-10 h-10 flex items-center justify-center text-teal-700">
                        <Pill size={24} strokeWidth={2} />
                    </div>
                    <h2 className="text-teal-700 text-2xl font-bold m-0">DocAI Pharmacy</h2>
                </div>

                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Pharmacist Login</h1>
                <p className="text-gray-500 mb-8">Access inventory and order management system</p>

                {error && (
                    <div className="bg-red-50 text-red-800 p-3 rounded-lg mb-4 text-sm text-left border border-red-200">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="text-left">
                    <div className="mb-4">
                        <label className="block font-medium text-gray-700 mb-2">Email Address</label>
                        <input
                            type="email"
                            required
                            placeholder="pharma.delhi.1@docai.in"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                        />
                    </div>

                    <div className="mb-6">
                        <label className="block font-medium text-gray-700 mb-2">Password</label>
                        <input
                            type="password"
                            required
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 bg-teal-700 text-white rounded-lg font-semibold text-lg transition-colors hover:bg-teal-800 focus:outline-none focus:ring-4 focus:ring-teal-300 ${loading ? 'opacity-80 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                </form>

                {/* Demo Credentials Box */}
                <div className="mt-8 p-4 bg-teal-50 border border-teal-100 rounded-lg text-left text-sm text-gray-700">
                    <strong className="block mb-2 text-teal-700 text-xs uppercase tracking-wider">Demo Credentials:</strong>
                    <div className="font-mono space-y-1">
                        <div>
                            <span className="text-teal-600 font-bold">User:</span> pharma.delhi.1@docai.in
                        </div>
                        <div>
                            <span className="text-teal-600 font-bold">Password:</span> password123
                        </div>
                    </div>
                </div>

                <div className="mt-8">
                    <Link to="/patient" className="inline-flex items-center gap-2 text-teal-700 hover:text-teal-900 font-medium transition-colors">
                        <ArrowLeft size={16} /> Back to Patient Portal
                    </Link>
                </div>

                <div className="mt-4 text-sm text-gray-500">
                    Don't have an account? <Link to="/signup" className="text-teal-700 font-bold hover:underline">Register Pharmacy</Link>
                </div>

            </motion.div>
        </div>
    );
};

export default PharmacyLogin;
