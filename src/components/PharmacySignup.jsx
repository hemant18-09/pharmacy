import React, { useState } from 'react';
import { Link } from 'react-router-dom';
// import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Pill, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const PharmacySignup = () => {
    // const navigate = useNavigate(); // Not currently used
    // const { login } = useAuth(); // We'll use custom signup endpoint

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        pharmacy_name: '',
        license_no: '',
        address: ''
    });

    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Call the backend signup endpoint
            const response = await fetch('/pharmacy/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password,
                    pharmacy_name: formData.pharmacy_name,
                    license_no: formData.license_no,
                    location: {
                        address: formData.address,
                        lat: 0,
                        lng: 0
                    }
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Signup failed');
            }

            setSuccess(true);

            // Optional: Automatically login? 
            // For now, let's ask them to login manually or wait for verification

        } catch (err) {
            console.error("Signup Error:", err);
            setError(err.message || "Failed to create account.");
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-teal-700 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white p-8 md:p-12 rounded-xl shadow-2xl w-full max-w-md text-center"
                >
                    <div className="text-teal-700 mb-6 flex justify-center">
                        <CheckCircle size={64} />
                    </div>
                    <h2 className="text-gray-900 text-3xl font-bold mb-4">Registration Successful!</h2>
                    <p className="text-gray-500 mb-8">
                        Your pharmacy <strong>{formData.pharmacy_name}</strong> has been registered.
                        Your account is currently <strong>Pending Verification</strong>.
                        Please wait for Admin approval before logging in.
                    </p>
                    <Link
                        to="/login"
                        className="inline-block px-8 py-3 bg-teal-700 text-white rounded-lg font-semibold hover:bg-teal-800 transition-colors"
                    >
                        Go to Login
                    </Link>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-teal-700 flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white p-6 md:p-12 rounded-xl shadow-2xl w-full max-w-lg text-center"
            >
                {/* Logo Section */}
                <div className="flex items-center justify-center gap-2 mb-6">
                    <div className="border-2 border-teal-700 rounded-lg w-10 h-10 flex items-center justify-center text-teal-700">
                        <Pill size={24} strokeWidth={2} />
                    </div>
                    <h2 className="text-teal-700 text-2xl font-bold m-0">DocAI Pharmacy</h2>
                </div>

                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Partner Registration</h1>
                <p className="text-gray-500 mb-6">Register your pharmacy to join the network</p>

                {error && (
                    <div className="bg-red-50 text-red-800 p-3 rounded-lg mb-6 text-sm text-left border border-red-200">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="text-left space-y-4">

                    <div className="grid grid-cols-1 gap-4">
                        <div>
                            <label className="block font-medium text-gray-700 mb-1">Pharmacy Name</label>
                            <input
                                name="pharmacy_name"
                                required
                                placeholder="e.g. Wellness Pharmacy"
                                value={formData.pharmacy_name}
                                onChange={handleChange}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block font-medium text-gray-700 mb-1">License No.</label>
                            <input
                                name="license_no"
                                required
                                placeholder="e.g. PH-1234"
                                value={formData.license_no}
                                onChange={handleChange}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                            />
                        </div>
                        <div>
                            <label className="block font-medium text-gray-700 mb-1">Email</label>
                            <input
                                type="email"
                                name="email"
                                required
                                placeholder="Email Address"
                                value={formData.email}
                                onChange={handleChange}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                            />
                        </div>
                    </div>

                    <div className="mb-4">
                        <label className="block font-medium text-gray-700 mb-1">Address</label>
                        <input
                            name="address"
                            required
                            placeholder="Full Address"
                            value={formData.address}
                            onChange={handleChange}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                        />
                    </div>

                    <div className="mb-6">
                        <label className="block font-medium text-gray-700 mb-1">Password</label>
                        <input
                            type="password"
                            name="password"
                            required
                            placeholder="Create Password"
                            value={formData.password}
                            onChange={handleChange}
                            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-700 focus:border-transparent transition-shadow"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 bg-teal-700 text-white rounded-lg font-semibold text-lg transition-colors hover:bg-teal-800 focus:outline-none focus:ring-4 focus:ring-teal-300 ${loading ? 'opacity-80 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Registering...' : 'Register Pharmacy'}
                    </button>
                </form>

                <div className="mt-8">
                    <p className="text-gray-500 mb-4">
                        Already have an account? <Link to="/login" className="text-teal-700 font-bold hover:underline">Login here</Link>
                    </p>
                    <Link to="/patient" className="inline-flex items-center gap-2 text-teal-700 hover:text-teal-900 font-medium transition-colors">
                        <ArrowLeft size={16} /> Back to Patient Portal
                    </Link>
                </div>

            </motion.div>
        </div>
    );
};

export default PharmacySignup;
