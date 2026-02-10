import React from 'react';
import { motion } from 'framer-motion';
import { Pill, FileText, Clock, AlertCircle } from 'lucide-react';

const PatientPharmacy = () => {
    return (
        <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginBottom: '2rem' }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{
                        padding: '12px',
                        backgroundColor: '#ccfbf1',
                        borderRadius: '12px',
                        color: '#0f766e'
                    }}>
                        <Pill size={32} />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#111827', margin: 0 }}>
                            Pharmacy & Medicines
                        </h1>
                        <p style={{ color: '#6b7280' }}>Manage your prescriptions and orders</p>
                    </div>
                </div>
            </motion.div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '1.5rem',
                marginBottom: '3rem'
            }}>
                {/* Active Orders Card */}
                <div style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #f3f4f6'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h3 style={{ fontWeight: '600', color: '#374151' }}>Active Orders</h3>
                        <Clock size={20} className="text-teal-600" />
                    </div>
                    <div style={{ textAlign: 'center', padding: '2rem 0', color: '#9ca3af' }}>
                        <p>No active orders currently.</p>
                        <button style={{
                            marginTop: '1rem',
                            padding: '0.5rem 1rem',
                            backgroundColor: '#0f766e',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            fontWeight: '500',
                            cursor: 'pointer'
                        }}>
                            Order New Medicines
                        </button>
                    </div>
                </div>

                {/* Past Prescriptions */}
                <div style={{
                    backgroundColor: 'white',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #f3f4f6'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h3 style={{ fontWeight: '600', color: '#374151' }}>Recent Prescriptions</h3>
                        <FileText size={20} className="text-teal-600" />
                    </div>
                    <div style={{ textAlign: 'center', padding: '2rem 0', color: '#9ca3af' }}>
                        <p>No recent digital prescriptions found.</p>
                    </div>
                </div>
            </div>

            <div style={{
                padding: '1rem',
                backgroundColor: '#fefce8',
                border: '1px solid #fde047',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: '#854d0e'
            }}>
                <AlertCircle size={20} />
                <p style={{ margin: 0, fontSize: '0.9rem' }}>
                    <strong>Note:</strong> Pharmacy integration is currently in beta. Please contact support for urgent medication requests.
                </p>
            </div>
        </div>
    );
};

export default PatientPharmacy;
