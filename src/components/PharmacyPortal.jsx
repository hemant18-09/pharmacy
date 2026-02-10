import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard, ShoppingCart, Package, FileText, Settings as SettingsIcon, LogOut,
    Search, Bell, ChevronDown,
    ShoppingBag, CheckCircle, AlertTriangle, TrendingUp,
    Eye, Clock, CheckCircle2, AlertCircle,
    X, MessageSquare, MapPin,
    Plus, Filter, Edit2, Trash2, Menu,
    User, Shield, Users, Camera, Save, Calendar, Download
} from 'lucide-react';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

// --- API Helpers ---
const API_BASE = '';

const fetchStats = async () => {
    try {
        const res = await fetch(`${API_BASE}/pharmacy/stats`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        return await res.json();
    } catch (e) {
        console.error(e);
        return {};
    }
};

const fetchOrders = async (status = null) => {
    try {
        const url = status ? `${API_BASE}/pharmacy/orders?status=${status}` : `${API_BASE}/pharmacy/orders`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch orders');
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
};

const fetchOrderDetail = async (id) => {
    const res = await fetch(`${API_BASE}/pharmacy/orders/${id}`);
    if (!res.ok) throw new Error('Failed to fetch order detail');
    return await res.json();
};

const fetchInventory = async () => {
    try {
        const res = await fetch(`${API_BASE}/pharmacy/inventory`);
        if (!res.ok) throw new Error('Failed to fetch inventory');
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
};

const updateStock = async (itemId, quantity) => {
    const res = await fetch(`${API_BASE}/pharmacy/inventory/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, quantity }),
    });
    if (!res.ok) throw new Error('Failed to update stock');
    return await res.json();
};

const updateOrderStatus = async (orderId, status) => {
    const res = await fetch(`${API_BASE}/pharmacy/orders/${orderId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error('Failed to update order status');
    return await res.json();
};

const fetchDailySummary = async () => {
    try {
        const res = await fetch(`${API_BASE}/pharmacy/reports/daily-summary?days=7`);
        if (!res.ok) throw new Error('Failed to fetch daily summary');
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
};

const fetchTopMedicines = async () => {
    try {
        const res = await fetch(`${API_BASE}/pharmacy/reports/top-medicines?limit=5`);
        if (!res.ok) throw new Error('Failed to fetch top medicines');
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
};

const addInventoryItem = async (item) => {
    const res = await fetch(`${API_BASE}/pharmacy/inventory/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
    });
    if (!res.ok) throw new Error('Failed to add inventory item');
    return await res.json();
};

const deleteInventoryItem = async (itemId) => {
    const res = await fetch(`${API_BASE}/pharmacy/inventory/${itemId}`, {
        method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete inventory item');
    return await res.json();
};

// --- Sub-Components ---

const Sidebar = ({ activePage, onNavigate, isOpen, onClose, logout }) => {
    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'orders', icon: ShoppingCart, label: 'Orders' },
        { id: 'history', icon: Clock, label: 'History' },
        { id: 'inventory', icon: Package, label: 'Inventory' },
        { id: 'reports', icon: FileText, label: 'Reports' },
        { id: 'settings', icon: SettingsIcon, label: 'Settings' },
    ];

    const handleLogout = async () => {
        try {
            await logout();
            // Assuming AuthContext or App handles redirect
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 md:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar Content */}
            <div className={`fixed left-0 top-0 h-full w-64 bg-teal-900 text-white flex flex-col shadow-lg z-50 transition-transform duration-300 transform 
                ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}>
                <div className="p-6 border-b border-teal-800 flex justify-between items-center">
                    <h1 className="text-xl font-bold tracking-wide">DOC AI Pharmacy</h1>
                    <button onClick={onClose} className="md:hidden text-teal-200 hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                <nav className="flex-1 overflow-y-auto py-4">
                    <ul className="space-y-1">
                        {navItems.map((item) => (
                            <li key={item.id}>
                                <button
                                    onClick={() => {
                                        onNavigate(item.id);
                                        onClose(); // Close sidebar on mobile after selection
                                    }}
                                    className={`w-full flex items-center gap-3 px-6 py-3 transition-colors ${activePage === item.id
                                        ? 'bg-teal-800 border-r-4 border-white text-white'
                                        : 'text-teal-100 hover:bg-teal-800/50 hover:text-white'
                                        }`}
                                >
                                    <item.icon size={20} />
                                    <span className="font-medium">{item.label}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="p-4 border-t border-teal-800">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 w-full px-4 py-2 text-teal-100 hover:text-white hover:bg-teal-800/50 rounded-lg transition-colors">
                        <LogOut size={20} />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </div>
        </>
    );
};

const Header = ({ onMenuClick, currentUser, logout, searchQuery, onSearchChange }) => {
    const [showProfileMenu, setShowProfileMenu] = useState(false);
    const userName = currentUser?.profile?.full_name || currentUser?.displayName || 'Pharmacist';
    const userRole = currentUser?.profile?.role === 'pharmacist' ? 'Chief Pharmacist' : 'Staff';
    const email = currentUser?.email || 'N/A';
    const pharmacyId = currentUser?.profile?.pharmacy_id || 'PH-MAIN-001';
    const initials = currentUser?.profile?.full_name
        ? currentUser.profile.full_name.split(' ').map(n => n[0]).join('').toUpperCase()
        : 'DP';

    return (
        <header className="flex items-center justify-between h-16 bg-white px-4 md:px-8 shadow-sm border-b border-gray-200 sticky top-0 z-30">
            <div className="flex items-center gap-4 flex-1 max-w-xl">
                <button
                    onClick={onMenuClick}
                    className="md:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                >
                    <Menu size={24} />
                </button>

                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => onSearchChange(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent text-sm"
                    />
                </div>
            </div>

            <div className="flex items-center gap-4 md:gap-6">
                <button className="relative p-2 text-gray-500 hover:text-teal-700 transition-colors rounded-full hover:bg-gray-50">
                    <Bell size={20} />
                    <span className="absolute top-1.5 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
                </button>

                <div className="relative">
                    <div
                        onClick={() => setShowProfileMenu(!showProfileMenu)}
                        className="flex items-center gap-3 pl-4 md:pl-6 border-l border-gray-200 cursor-pointer group"
                    >
                        <div className="h-9 w-9 bg-teal-100 rounded-full flex items-center justify-center text-teal-700 font-bold border-2 border-white shadow-sm ring-2 ring-gray-50 uppercase">
                            {initials}
                        </div>
                        <div className="hidden md:block">
                            <p className="text-sm font-semibold text-gray-700 group-hover:text-teal-700">{userName}</p>
                            <p className="text-xs text-gray-500">{userRole}</p>
                        </div>
                        <ChevronDown size={16} className={`text-gray-400 group-hover:text-teal-700 hidden md:block transition-transform ${showProfileMenu ? 'rotate-180' : ''}`} />
                    </div>

                    {/* Profile Dropdown */}
                    {showProfileMenu && (
                        <>
                            <div className="fixed inset-0 z-10" onClick={() => setShowProfileMenu(false)} />
                            <div className="absolute right-0 top-full mt-3 w-72 bg-white rounded-xl shadow-xl border border-gray-100 z-20 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                                <div className="p-4 bg-teal-50 border-b border-teal-100">
                                    <h3 className="text-sm font-bold text-teal-900">User Profile</h3>
                                    <p className="text-xs text-teal-700 mt-1">Manage your account details</p>
                                </div>
                                <div className="p-4 space-y-4">
                                    <div className="flex items-center gap-4">
                                        <div className="h-12 w-12 bg-teal-100 rounded-full flex items-center justify-center text-teal-700 font-bold text-lg uppercase">
                                            {initials}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-800">{userName}</p>
                                            <p className="text-xs text-gray-500">{email}</p>
                                        </div>
                                    </div>

                                    <div className="space-y-2 pt-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-500">Role</span>
                                            <span className="font-medium text-gray-700 badge bg-gray-100 px-2 py-0.5 rounded">{userRole}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-gray-500">Pharmacy ID</span>
                                            <span className="font-medium text-gray-700 font-mono">{pharmacyId}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="p-2 border-t border-gray-100 bg-gray-50">
                                    <button
                                        onClick={() => {
                                            logout();
                                            setShowProfileMenu(false);
                                        }}
                                        className="flex items-center gap-2 w-full px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
                                    >
                                        <LogOut size={16} />
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
};

const Layout = ({ children, activePage, onNavigate, logout, currentUser, searchQuery, onSearchChange }) => {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <div className="flex min-h-screen bg-gray-50 font-sans">
            <Sidebar
                activePage={activePage}
                onNavigate={onNavigate}
                isOpen={isMobileMenuOpen}
                onClose={() => setIsMobileMenuOpen(false)}
                logout={logout}
            />
            <div className="flex-1 md:ml-64 flex flex-col min-w-0 transition-all duration-300">
                <Header
                    onMenuClick={() => setIsMobileMenuOpen(true)}
                    currentUser={currentUser}
                    logout={logout}
                    searchQuery={searchQuery}
                    onSearchChange={onSearchChange}
                />
                <main className="flex-1 p-4 md:p-8 overflow-y-auto">
                    {children}
                </main>
            </div>
        </div>
    );
};

const StatsCard = ({ title, value, icon: Icon, colorClass, bgClass }) => {
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between transition-transform hover:-translate-y-1 duration-200">
            <div>
                <h3 className="text-gray-500 text-sm font-medium mb-1">{title}</h3>
                <p className="text-2xl font-bold text-gray-800">{value}</p>
            </div>
            <div className={`p-3 rounded-lg ${bgClass} ${colorClass}`}>
                <Icon size={24} />
            </div>
        </div>
    );
};

const ActiveOrdersTable = ({ orders, onViewDetails, showFulfillmentActions = false, onStatusChange }) => {
    const getPriorityBadge = (priority) => {
        // Mock priority since it's not in the list API yet
        const displayPriority = priority || 'NORMAL';
        switch (displayPriority) {
            case 'EMERGENCY':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse">
                        <AlertCircle size={12} className="mr-1" />
                        EMERGENCY
                    </span>
                );
            case 'URGENT':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        URGENT
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                        NORMAL
                    </span>
                );
        }
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'ACCEPTED':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                        <CheckCircle2 size={12} className="mr-1" />
                        ACCEPTED
                    </span>
                );
            case 'REJECTED':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                        REJECTED
                    </span>
                );
            case 'PICKED_UP':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-200 text-gray-800 border border-gray-300">
                        PICKED UP
                    </span>
                );
            case 'READY':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                        <CheckCircle2 size={12} className="mr-1" />
                        READY
                    </span>
                );
            case 'PREPARING':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">
                        <Clock size={12} className="mr-1" />
                        PREPARING
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                        {status}
                    </span>
                );
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mt-8">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <div>
                    <h2 className="text-lg font-bold text-gray-800">Active Queue</h2>
                    <p className="text-sm text-gray-500">Real-time prescription orders</p>
                </div>
                <button className="text-teal-700 hover:text-teal-900 text-sm font-medium">View All</button>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium text-xs uppercase tracking-wider">
                        <tr>
                            <th className="px-6 py-4">Order ID</th>
                            <th className="px-6 py-4">Patient Name</th>
                            <th className="px-6 py-4">Medications</th>
                            <th className="px-6 py-4">Priority (Est)</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {orders.map((order, index) => (
                            <tr key={index} className="hover:bg-gray-50/50 transition-colors">
                                <td className="px-6 py-4 font-medium text-gray-900">{order.id}</td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-teal-50 text-teal-700 flex items-center justify-center text-xs font-bold">
                                            {order.patient_name.split(' ').map(n => n[0]).join('')}
                                        </div>
                                        <span className="text-gray-700 font-medium">{order.patient_name}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-gray-500">{order.medication_count} items</td>
                                <td className="px-6 py-4">{getPriorityBadge('NORMAL')}</td>
                                <td className="px-6 py-4">{getStatusBadge(order.status)}</td>
                                <td className="px-6 py-4 text-right">
                                    {showFulfillmentActions ? (
                                        <div className="flex items-center justify-end gap-2">
                                            <button
                                                onClick={() => onStatusChange(order, 'READY')}
                                                className="px-3 py-1.5 bg-teal-600 text-white hover:bg-teal-700 rounded-md text-sm font-medium transition-colors"
                                            >
                                                Ready for Pickup
                                            </button>
                                            <button
                                                onClick={() => onStatusChange(order, 'DELIVERED')}
                                                className="px-3 py-1.5 bg-green-600 text-white hover:bg-green-700 rounded-md text-sm font-medium transition-colors"
                                            >
                                                Delivered
                                            </button>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => onViewDetails(order)}
                                            className="inline-flex items-center gap-2 px-3 py-1.5 bg-teal-50 text-teal-700 hover:bg-teal-100 rounded-md text-sm font-medium transition-colors"
                                        >
                                            <Eye size={16} />
                                            View Details
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {orders.length === 0 && (
                <div className="p-8 text-center text-gray-500">No active orders found.</div>
            )}
        </div>
    );
};

const Dashboard = ({ onViewDetails, refreshTrigger }) => {
    console.log("Rendering Pharmacy Dashboard");
    const [stats, setStats] = useState({
        new_prescriptions_today: 0,
        orders_in_progress: 0,
        orders_delivered_today: 0,
        low_stock_alerts: 0
    });
    const [orders, setOrders] = useState([]);

    useEffect(() => {
        // Fetch Stats
        fetchStats().then(setStats).catch(console.error);
        // Fetch Orders
        fetchOrders('NEW').then(setOrders).catch(console.error);
    }, [refreshTrigger]);

    const statCards = [
        {
            title: 'Pending Orders',
            value: stats.new_prescriptions_today || 0,
            icon: ShoppingBag,
            colorClass: 'text-amber-600',
            bgClass: 'bg-amber-100',
        },
        {
            title: 'Completed Today',
            value: stats.orders_delivered_today || 0,
            icon: CheckCircle,
            colorClass: 'text-teal-600',
            bgClass: 'bg-teal-100',
        },
        {
            title: 'Low Stock Alerts',
            value: stats.low_stock_alerts || 0,
            icon: AlertTriangle,
            colorClass: 'text-red-600',
            bgClass: 'bg-red-100',
        },
        {
            title: 'Orders In Progress',
            value: stats.orders_in_progress || 0,
            icon: TrendingUp,
            colorClass: 'text-blue-600',
            bgClass: 'bg-blue-100',
        },
    ];

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, index) => (
                    <StatsCard key={index} {...stat} />
                ))}
            </div>

            <ActiveOrdersTable orders={orders} onViewDetails={onViewDetails} />
        </div>
    );
};

const PrescriptionModal = ({ order, onClose, onRefresh }) => {
    const [loading, setLoading] = useState(false);
    const [orderDetails, setOrderDetails] = useState(null);

    useEffect(() => {
        if (order?.id) {
            setLoading(true);
            fetchOrderDetail(order.id)
                .then(data => {
                    setOrderDetails(data);
                })
                .finally(() => setLoading(false));
        }
    }, [order]); // eslint-disable-line

    const handleStatusChange = async (newStatus) => {
        try {
            await updateOrderStatus(order.id, newStatus);
            if (onRefresh) onRefresh();
            onClose();
        } catch (err) {
            console.error("Status Update Failed:", err);
            alert("Failed to update status. Please try again.");
        }
    };

    if (!order) return null;

    if (loading || !orderDetails) {
        return (
            <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center">
                <div className="bg-white p-8 rounded-xl">
                    <p>Loading order details...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/50 z-[60] flex justify-end transition-opacity duration-300">
            <div className="w-full max-w-4xl bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-300 slide-in-from-right">

                {/* Header */}
                <div className="px-8 py-6 border-b border-gray-200 flex items-center justify-between bg-white">
                    <div className="flex items-center gap-4">
                        <h2 className="text-2xl font-bold text-gray-800">Order {orderDetails.id}</h2>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${orderDetails.status === 'READY' ? 'bg-green-100 text-green-800 border border-green-200' :
                            orderDetails.status === 'PREPARING' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                                orderDetails.status === 'ACCEPTED' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                                    orderDetails.status === 'REJECTED' ? 'bg-red-100 text-red-800 border border-red-200' :
                                        'bg-gray-100 text-gray-800 border border-gray-200'
                            }`}>
                            {orderDetails.status}
                        </span>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors">
                        <X size={24} />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto bg-gray-50 p-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">

                        {/* Left Column: Patient & Doctor */}
                        <div className="space-y-6">
                            {/* Patient Card */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-teal-100">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-800">{orderDetails.patient_name}</h3>
                                        <p className="text-sm text-gray-500">{orderDetails.patient_age} Years • {orderDetails.patient_gender}</p>
                                    </div>
                                </div>
                                <div className="space-y-2 mt-4 text-sm">
                                    <div className="flex items-center text-gray-600 gap-2">
                                        <span className="font-medium w-16">Contact:</span>
                                        <span>{orderDetails.patient_contact_id}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Doctor Card */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-teal-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-1">{orderDetails.doctor_name}</h3>
                                <p className="text-sm text-teal-700 font-medium mb-4">Registered Doctor</p>
                                <div className="text-sm text-gray-600">
                                    <span className="font-medium mr-2">Reg ID:</span>
                                    {orderDetails.doctor_registration_id}
                                </div>
                            </div>
                        </div>

                        {/* Right Column: Agentic Data */}
                        <div className="space-y-6">
                            {/* Doctor's Notes */}
                            <div className="bg-yellow-50 p-6 rounded-xl border border-yellow-200 text-yellow-900">
                                <h4 className="flex items-center gap-2 font-bold mb-3 text-yellow-800">
                                    <MessageSquare size={18} />
                                    Instructions
                                </h4>
                                <p className="text-sm leading-relaxed opacity-90">
                                    {/* Mock notes as it is not in API response yet */}
                                    Please verify patient allergies before dispensing. Ensure correct dosage instructions are explained.
                                </p>
                            </div>

                            {/* Map Placeholder */}
                            <div className="bg-gray-200 h-48 rounded-xl border border-gray-300 flex flex-col items-center justify-center text-gray-500 gap-2 relative overflow-hidden group">
                                <div className="absolute inset-0 bg-gray-300 opacity-20 pattern-grid-lg"></div>
                                <MapPin size={32} />
                                <span className="font-medium">Delivery Mode: {orderDetails.delivery_mode}</span>
                            </div>
                        </div>
                    </div>

                    {/* Medication Table */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
                        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                            <h3 className="font-bold text-gray-800">Prescribed Medications</h3>
                        </div>
                        <table className="w-full text-left text-sm">
                            <thead className="bg-gray-50 text-gray-500 font-medium uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-3">Medicine Name</th>
                                    <th className="px-6 py-3">Strength</th>
                                    <th className="px-6 py-3">Frequency</th>
                                    <th className="px-6 py-3">Duration</th>
                                    <th className="px-6 py-3">User Instr.</th>
                                    <th className="px-6 py-3 text-center">Stock</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {orderDetails.medications.map((med, index) => {
                                    return (
                                        <tr key={index} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 font-medium text-gray-900">{med.drug_name}</td>
                                            <td className="px-6 py-4 text-gray-600">{med.strength}</td>
                                            <td className="px-6 py-4">
                                                <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-md font-medium text-xs border border-blue-100">
                                                    {med.frequency}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-gray-600">{med.duration}</td>
                                            <td className="px-6 py-4 text-gray-600">{med.instructions}</td>
                                            <td className="px-6 py-4 text-center">
                                                <div className="text-gray-500 text-xs">
                                                    Check Inventory
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Action Footer */}
                <div className="p-4 border-t border-gray-200 bg-white flex-shrink-0 flex flex-col sm:flex-row justify-between items-center gap-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                    <button
                        onClick={() => handleStatusChange('REJECTED')}
                        className="w-full sm:w-auto px-6 py-2 border border-red-200 text-red-600 font-semibold rounded-lg hover:bg-red-50 transition-colors text-sm"
                    >
                        Reject Order
                    </button>
                    <button
                        onClick={() => handleStatusChange('ACCEPTED')}
                        className="w-full sm:w-auto px-6 py-2 text-white font-bold rounded-lg shadow-md hover:shadow-lg transition-all text-sm"
                        style={{ backgroundColor: '#0f766e' }}
                    >
                        Accept Order
                    </button>
                </div>

            </div>
        </div>
    );
};

const OrdersScreen = ({ onViewDetails, refreshTrigger }) => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchOrders('ACCEPTED')
            .then(setOrders)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [refreshTrigger]);

    const handleQuickStatus = async (order, status) => {
        try {
            await updateOrderStatus(order.id, status);
            const updated = await fetchOrders('ACCEPTED');
            setOrders(updated);
        } catch (error) {
            console.error("Failed to update order status:", error);
            alert("Failed to update order status");
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Accepted Orders</h2>
                    <p className="text-gray-500">Orders you have accepted for fulfillment</p>
                </div>
            </div>
            <ActiveOrdersTable
                orders={orders}
                onViewDetails={onViewDetails}
                showFulfillmentActions
                onStatusChange={handleQuickStatus}
            />
        </div>
    );
};

const HistoryScreen = ({ refreshTrigger }) => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([fetchOrders('DELIVERED'), fetchOrders('PICKED_UP')])
            .then(([delivered, pickedUp]) => {
                const merged = [...delivered, ...pickedUp];
                const unique = new Map(merged.map(item => [item.id, item]));
                setOrders(Array.from(unique.values()));
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [refreshTrigger]);

    const formatDate = (value) => {
        if (!value) return 'N/A';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString();
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Order History</h2>
                    <p className="text-gray-500">Delivered and picked up orders with timestamps</p>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 text-gray-500 font-medium text-xs uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Order ID</th>
                                <th className="px-6 py-4">Patient</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Medications</th>
                                <th className="px-6 py-4">Accepted</th>
                                <th className="px-6 py-4">Completed</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {orders.map((order) => (
                                <tr key={order.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="px-6 py-4 font-medium text-gray-900">{order.id}</td>
                                    <td className="px-6 py-4 text-gray-700">{order.patient_name}</td>
                                    <td className="px-6 py-4">{order.status}</td>
                                    <td className="px-6 py-4 text-gray-600">{order.medication_count} items</td>
                                    <td className="px-6 py-4 text-gray-600">{formatDate(order.accepted_at)}</td>
                                    <td className="px-6 py-4 text-gray-600">{formatDate(order.completed_at)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {!loading && orders.length === 0 && (
                    <div className="p-8 text-center text-gray-500">No history records yet.</div>
                )}
            </div>
        </div>
    );
};

const InventoryScreen = ({ searchQuery }) => {
    const [filterLowStock, setFilterLowStock] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [inventory, setInventory] = useState([]);
    
    // State for new item form
    const [newItem, setNewItem] = useState({
        drug_name: '',
        strength: '',
        quantity: 0,
        batch_number: '',
        expiry_date: '',
        threshold: 10
    });

    useEffect(() => {
        fetchInventory().then(setInventory).catch(console.error);
    }, []);

    const normalizedQuery = searchQuery.trim().toLowerCase();
    const filteredInventory = inventory.filter(item => {
        if (filterLowStock && !item.is_low_stock) return false;
        if (!normalizedQuery) return true;
        const haystack = [
            item.drug_name,
            item.batch_number,
            item.strength
        ].filter(Boolean).join(' ').toLowerCase();
        return haystack.includes(normalizedQuery);
    });

    const handleEditClick = (item) => {
        setSelectedItem({ ...item });
        setShowEditModal(true);
    };

    const handleSaveStock = async (e) => {
        e.preventDefault();
        try {
            const updated = await updateStock(selectedItem.id, selectedItem.quantity);
            setInventory(prev => prev.map(item => item.id === updated.id ? updated : item));
            setShowEditModal(false);
        } catch (error) {
            console.error("Failed to update stock:", error);
            alert("Failed to update stock");
        }
    };

    const handleAddSubmit = async (e) => {
        e.preventDefault();
        try {
            const added = await addInventoryItem(newItem);
            setInventory(prev => [...prev, added]);
            setShowAddModal(false);
            setNewItem({
                drug_name: '',
                strength: '',
                quantity: 0,
                batch_number: '',
                expiry_date: '',
                threshold: 10
            });
        } catch (error) {
            console.error("Failed to add item:", error);
            alert("Failed to add item");
        }
    };

    const handleDeleteItem = async (item) => {
        const confirmed = window.confirm(`Delete ${item.drug_name}? This cannot be undone.`);
        if (!confirmed) return;
        try {
            await deleteInventoryItem(item.id);
            setInventory(prev => prev.filter(existing => existing.id !== item.id));
        } catch (error) {
            console.error("Failed to delete item:", error);
            alert("Failed to delete item");
        }
    };

    return (
        <div className="space-y-6">
            {/* Header & Toolbar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Inventory Management</h2>
                    <p className="text-gray-500">Track stock levels and expiry dates</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setFilterLowStock(!filterLowStock)}
                        className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-colors ${filterLowStock ? 'bg-red-50 border-red-200 text-red-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        <Filter size={18} />
                        <span className="hidden sm:inline">{filterLowStock ? 'Showing Low Stock' : 'Filter Low Stock'}</span>
                        <span className="sm:hidden">Filter</span>
                    </button>
                    <button 
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-teal-700 text-white rounded-lg hover:bg-teal-800 shadow-sm transition-colors"
                    >
                        <Plus size={18} />
                        Add Medicine
                    </button>
                </div>
            </div>

            {/* Mobile Inventory List (Cards) */}
            <div className="md:hidden space-y-4">
                {filteredInventory.map((item) => (
                    <div key={item.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <h3 className="font-bold text-gray-900">{item.drug_name}</h3>
                                <p className="text-sm text-gray-500">Batch: {item.batch_number}</p>
                            </div>
                            <div className="flex gap-2">
                                <button onClick={() => handleEditClick(item)} className="p-2 text-teal-600 bg-teal-50 rounded-lg">
                                    <Edit2 size={16} />
                                </button>
                                <button onClick={() => handleDeleteItem(item)} className="p-2 text-red-600 bg-red-50 rounded-lg">
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                            <div>
                                <p className="text-gray-500 text-xs uppercase">Stock</p>
                                {item.is_low_stock ? (
                                    <span className="font-bold text-red-600 flex items-center gap-1">
                                        <AlertTriangle size={14} /> {item.quantity} (Low)
                                    </span>
                                ) : (
                                    <span className="font-semibold text-gray-700">{item.quantity}</span>
                                )}
                            </div>
                            <div>
                                <p className="text-gray-500 text-xs uppercase">Expiry</p>
                                <span className={`font-medium ${item.is_expiring_soon ? 'text-red-600' : 'text-gray-700'}`}>
                                    {item.expiry_date ? item.expiry_date.substring(0, 10) : 'N/A'}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
                
                {filteredInventory.length === 0 && (
                    <div className="p-8 text-center text-gray-400 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                        No items found matching your filter.
                    </div>
                )}
            </div>

            {/* Desktop Inventory Table */}
            <div className="hidden md:block bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-gray-500 font-medium text-xs uppercase tracking-wider">
                        <tr>
                            <th className="px-6 py-4">Medicine Name</th>
                            <th className="px-6 py-4">Batch No</th>
                            <th className="px-6 py-4">Expiry Date</th>
                            <th className="px-6 py-4">Stock Level</th>
                            <th className="px-6 py-4">Price / Unit</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {filteredInventory.map((item) => {
                            return (
                                <tr key={item.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="px-6 py-4 font-medium text-gray-900">{item.drug_name}</td>
                                    <td className="px-6 py-4 text-gray-500 uppercase text-xs font-semibold tracking-wide">{item.batch_number}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center gap-1 ${item.is_expiring_soon ? 'text-red-600 font-medium' : 'text-gray-600'}`}>
                                            {item.is_expiring_soon && <AlertCircle size={14} />}
                                            {item.expiry_date ? item.expiry_date.substring(0, 10) : 'N/A'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        {item.is_low_stock ? (
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                Low Stock ({item.quantity})
                                            </span>
                                        ) : (
                                            <span className="text-gray-700 font-medium">{item.quantity}</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-gray-700">₹--</td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <button onClick={() => handleEditClick(item)} className="p-1.5 text-gray-400 hover:text-teal-600 hover:bg-teal-50 rounded-md transition-colors">
                                                <Edit2 size={16} />
                                            </button>
                                            <button onClick={() => handleDeleteItem(item)} className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors">
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
                {filteredInventory.length === 0 && (
                    <div className="p-12 text-center text-gray-400">
                        No items found matching your filter.
                    </div>
                )}
            </div>

            {/* Add Item Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 z-[70] flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden max-h-[90vh] overflow-y-auto">
                        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <h3 className="font-bold text-gray-800">Add New Medicine</h3>
                            <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleAddSubmit} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Medicine Name</label>
                                <input
                                    type="text"
                                    required
                                    value={newItem.drug_name}
                                    onChange={(e) => setNewItem({ ...newItem, drug_name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                                    placeholder="e.g. Paracetamol"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Strength</label>
                                    <input
                                        type="text"
                                        value={newItem.strength}
                                        onChange={(e) => setNewItem({ ...newItem, strength: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                                        placeholder="500mg"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                                    <input
                                        type="number"
                                        required
                                        min="0"
                                        value={newItem.quantity}
                                        onChange={(e) => setNewItem({ ...newItem, quantity: parseInt(e.target.value) || 0 })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Batch Number</label>
                                <input
                                    type="text"
                                    required
                                    value={newItem.batch_number}
                                    onChange={(e) => setNewItem({ ...newItem, batch_number: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                                    placeholder="e.g. BTX-20250101"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                                <input
                                    type="date"
                                    required
                                    value={newItem.expiry_date}
                                    onChange={(e) => setNewItem({ ...newItem, expiry_date: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none"
                                />
                            </div>
                            
                            <div className="flex justify-end gap-3 pt-4">
                                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors">
                                    Cancel
                                </button>
                                <button type="submit" className="px-4 py-2 bg-teal-700 text-white font-medium rounded-lg hover:bg-teal-800 transition-colors">
                                    Add Item
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit Modal */}
            {showEditModal && selectedItem && (
                <div className="fixed inset-0 bg-black/50 z-[70] flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                            <h3 className="font-bold text-gray-800">Update Stock</h3>
                            <button onClick={() => setShowEditModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleSaveStock} className="p-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Medicine Name</label>
                                <input
                                    type="text"
                                    value={selectedItem.drug_name}
                                    disabled
                                    className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-gray-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">New Stock Quantity</label>
                                <input
                                    type="number"
                                    value={selectedItem.quantity}
                                    onChange={(e) => setSelectedItem({ ...selectedItem, quantity: parseInt(e.target.value) || 0 })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none"
                                    min="0"
                                />
                            </div>
                            <div className="flex justify-end gap-3 pt-4">
                                <button type="button" onClick={() => setShowEditModal(false)} className="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors">
                                    Cancel
                                </button>
                                <button type="submit" className="px-4 py-2 bg-teal-700 text-white font-medium rounded-lg hover:bg-teal-800 transition-colors">
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

const ReportsScreen = () => {
    const [ordersTrendData, setOrdersTrendData] = useState([]);
    const [topSellingData, setTopSellingData] = useState([]);

    useEffect(() => {
        fetchDailySummary().then(data => {
            // Map API response to chart format
            const mapped = data.map(d => ({
                day: d.label,
                orders: d.total_orders
            }));
            setOrdersTrendData(mapped);
        }).catch(console.error);

        fetchTopMedicines().then(data => {
            const mapped = data.map(d => ({
                name: d.drug_name,
                sales: d.count
            }));
            setTopSellingData(mapped);
        }).catch(console.error);
    }, []);

    const statusDistributionData = [
        { name: 'Pending', value: 12, color: '#F59E0B' },
        { name: 'Ready', value: 45, color: '#0F766E' },
        { name: 'Delivered', value: 30, color: '#10B981' },
        { name: 'Cancelled', value: 5, color: '#EF4444' },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Analytics Overview</h2>
                    <p className="text-gray-500">Performance metrics and insights</p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors shadow-sm">
                        <Calendar size={18} />
                        Last 7 Days
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 border border-teal-600 text-teal-700 rounded-lg hover:bg-teal-50 transition-colors shadow-sm font-medium">
                        <Download size={18} />
                        Export PDF
                    </button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                    <div>
                        <p className="text-gray-500 text-sm font-medium">Total Revenue</p>
                        <h3 className="text-2xl font-bold text-gray-800">₹--</h3>
                    </div>
                    <div className="p-3 bg-teal-50 text-teal-600 rounded-lg">
                        <TrendingUp size={24} />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                    <div>
                        <p className="text-gray-500 text-sm font-medium">Total Orders</p>
                        <h3 className="text-2xl font-bold text-gray-800">--</h3>
                    </div>
                    <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                        <ShoppingBag size={24} />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                    <div>
                        <p className="text-gray-500 text-sm font-medium">Avg. Delivery Time</p>
                        <h3 className="text-2xl font-bold text-gray-800">-- mins</h3>
                    </div>
                    <div className="p-3 bg-amber-50 text-amber-600 rounded-lg">
                        <Clock size={24} />
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Line Chart: Orders Trend */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-6">Orders Trend</h3>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={ordersTrendData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                    cursor={{ stroke: '#0F766E', strokeWidth: 1, strokeDasharray: '4 4' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="orders"
                                    stroke="#0F766E"
                                    strokeWidth={3}
                                    dot={{ fill: '#0F766E', strokeWidth: 2, r: 4 }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Bar Chart: Top Selling Medicines */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-6">Top Selling Medicines</h3>
                    <div className="h-80 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={topSellingData} layout="vertical" margin={{ left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#E5E7EB" />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#4B5563', fontSize: 12 }} width={100} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                    cursor={{ fill: '#F3F4F6' }}
                                />
                                <Bar dataKey="sales" fill="#0F766E" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Donut Chart: Order Status Distribution */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 col-span-1 lg:col-span-2 flex flex-col items-center">
                    <h3 className="text-lg font-bold text-gray-800 mb-6 w-full text-left">Order Status Distribution</h3>
                    <div className="h-80 w-full max-w-md">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={statusDistributionData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={80}
                                    outerRadius={110}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {statusDistributionData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend verticalAlign="bottom" height={36} iconType="circle" />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>
        </div>
    );
};

const SettingsScreen = () => {
    const [activeTab, setActiveTab] = useState('general');
    const [notifications, setNotifications] = useState({
        email: true,
        sms: true,
        dailyReport: false,
    });
    const [saveStatus, setSaveStatus] = useState(null); // 'saving', 'success', 'error', null

    const tabs = [
        { id: 'general', label: 'General', icon: User },
        { id: 'security', label: 'Security', icon: Shield },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'team', label: 'Team Members', icon: Users },
    ];

    const handleToggle = (key) => {
        if (key === 'sms') return; // Locked as per requirements
        setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleSave = async () => {
        setSaveStatus('saving');
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            setSaveStatus('success');
            setTimeout(() => setSaveStatus(null), 3000);
        } catch (error) {
            console.error(error);
            setSaveStatus('error');
        }
    };

    return (
        <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">

            {/* Left Column: Tabs */}
            <div className="w-full lg:w-64 flex-shrink-0">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50">
                        <h3 className="font-bold text-gray-800">Settings</h3>
                    </div>
                    <nav className="p-2 space-y-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${activeTab === tab.id
                                    ? 'bg-teal-50 text-teal-700'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                    }`}
                            >
                                <tab.icon size={18} />
                                <span className="font-medium">{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>
            </div>

            {/* Right Column: Content Panel */}
            <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">

                {/* General Tab Content */}
                {activeTab === 'general' && (
                    <div className="flex-1 overflow-y-auto">
                        <div className="p-6 border-b border-gray-100">
                            <h2 className="text-xl font-bold text-gray-800">General Information</h2>
                            <p className="text-gray-500 text-sm">Manage your pharmacy profile and operating details</p>
                        </div>

                        <div className="p-8 space-y-8 max-w-3xl">
                            {/* Profile Section */}
                            <div className="flex items-start gap-6">
                                <div className="relative group cursor-pointer">
                                    <div className="w-24 h-24 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 text-2xl font-bold border-4 border-white shadow-sm ring-2 ring-gray-100">
                                        DP
                                    </div>
                                    <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Camera className="text-white" size={24} />
                                    </div>
                                </div>
                                <div className="flex-1 space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Pharmacy Name</label>
                                            <input
                                                type="text"
                                                defaultValue="DOC AI Pharmacy - Central"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-shadow"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">License Number</label>
                                            <input
                                                type="text"
                                                defaultValue="PH-REG-2024-8899"
                                                disabled
                                                className="w-full px-4 py-2 bg-gray-100 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                                            <input
                                                type="email"
                                                defaultValue="admin@docapharmacy.com"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-shadow"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <hr className="border-gray-100" />

                            {/* Location & Hours */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-800">Location & Hours</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="md:col-span-2">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Pharmacy Address</label>
                                        <textarea
                                            rows="3"
                                            defaultValue="123, Healthcare Boulevard, Tech City, State - 560001"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-shadow resize-none"
                                        ></textarea>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Opening Time</label>
                                        <input
                                            type="time"
                                            defaultValue="09:00"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-shadow"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Closing Time</label>
                                        <input
                                            type="time"
                                            defaultValue="22:00"
                                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none transition-shadow"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Footer */}
                        <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-end gap-3 items-center">
                            {saveStatus === 'success' && (
                                <span className="text-green-600 text-sm font-medium animate-in fade-in">Changes saved successfully!</span>
                            )}
                            <button className="px-6 py-2.5 text-gray-600 font-medium hover:text-gray-800 transition-colors">
                                Cancel
                            </button>
                            <button 
                                onClick={handleSave}
                                disabled={saveStatus === 'saving'}
                                className={`px-6 py-2.5 font-medium rounded-lg shadow-sm flex items-center gap-2 transition-all ${
                                    saveStatus === 'saving' ? 'bg-teal-600 opacity-75' : 'bg-teal-700 hover:bg-teal-800'
                                } text-white`}>
                                {saveStatus === 'saving' ? (
                                    <>
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save size={18} />
                                        Save Changes
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Notifications Tab Content */}
                {activeTab === 'notifications' && (
                    <div className="flex-1 overflow-y-auto">
                        <div className="p-6 border-b border-gray-100">
                            <h2 className="text-xl font-bold text-gray-800">Notification Preferences</h2>
                            <p className="text-gray-500 text-sm">Control how and when you receive alerts</p>
                        </div>
                        <div className="p-8 space-y-6 max-w-2xl">

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                                <div>
                                    <h4 className="font-medium text-gray-900">Email on New Order</h4>
                                    <p className="text-sm text-gray-500">Receive an email whenever a new order is placed</p>
                                </div>
                                <button
                                    onClick={() => handleToggle('email')}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${notifications.email ? 'bg-teal-600' : 'bg-gray-300'}`}
                                >
                                    <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${notifications.email ? 'translate-x-6' : 'translate-x-0'}`} />
                                </button>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100 opacity-75">
                                <div>
                                    <h4 className="font-medium text-gray-900 flex items-center gap-2">
                                        SMS for Emergency Cases
                                        <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">Locked</span>
                                    </h4>
                                    <p className="text-sm text-gray-500">Instant SMS alerts for high-priority/emergency orders</p>
                                </div>
                                <button
                                    disabled
                                    className="w-12 h-6 rounded-full bg-teal-600 relative cursor-not-allowed opacity-80"
                                >
                                    <span className="absolute top-1 left-1 bg-white w-4 h-4 rounded-full translate-x-6" />
                                </button>
                            </div>

                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                                <div>
                                    <h4 className="font-medium text-gray-900">Daily Report Summary</h4>
                                    <p className="text-sm text-gray-500">Receive a daily digest of sales and inventory status</p>
                                </div>
                                <button
                                    onClick={() => handleToggle('dailyReport')}
                                    className={`w-12 h-6 rounded-full transition-colors relative ${notifications.dailyReport ? 'bg-teal-600' : 'bg-gray-300'}`}
                                >
                                    <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${notifications.dailyReport ? 'translate-x-6' : 'translate-x-0'}`} />
                                </button>
                            </div>

                        </div>
                    </div>
                )}

                {/* Placeholders for other tabs */}
                {(activeTab === 'security' || activeTab === 'team') && (
                    <div className="flex-1 flex items-center justify-center text-gray-400">
                        <div className="text-center">
                            <p className="text-xl font-medium">Coming Soon</p>
                            <p className="text-sm">This module is under development.</p>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

// --- Main Application Component ---

const PharmaPortal = () => {
    const { logout, currentUser } = useAuth();
    const navigate = useNavigate();
    const [activePage, setActivePage] = useState('dashboard');
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [searchQuery, setSearchQuery] = useState('');

    const handleNavigate = (pageId) => {
        setActivePage(pageId);
        // Close modal when navigating
        setSelectedOrder(null);
    };

    const handleViewDetails = (order) => {
        setSelectedOrder(order);
    };

    const renderContent = () => {
        switch (activePage) {
            case 'dashboard': return <Dashboard onViewDetails={handleViewDetails} refreshTrigger={refreshTrigger} />;
            case 'orders': return <OrdersScreen onViewDetails={handleViewDetails} refreshTrigger={refreshTrigger} />;
            case 'history': return <HistoryScreen refreshTrigger={refreshTrigger} />;
            case 'inventory': return <InventoryScreen searchQuery={searchQuery} />;
            case 'reports': return <ReportsScreen />;
            case 'settings': return <SettingsScreen />;
            default: return <Dashboard onViewDetails={handleViewDetails} refreshTrigger={refreshTrigger} />;
        }
    };

    const handleOrderUpdate = () => {
        setRefreshTrigger(prev => prev + 1);
        // Optional: Refresh modal details if needed inside modal component logic
        // But since we close on success usually, or refetch inside modal, this is mainly for parent lists
    };

    return (
        <Layout
            activePage={activePage}
            onNavigate={handleNavigate}
            logout={logout}
            currentUser={currentUser}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
        >
            {renderContent()}

            <PrescriptionModal
                order={selectedOrder}
                onClose={() => setSelectedOrder(null)}
                onRefresh={handleOrderUpdate}
            />
        </Layout>
    );
};

export default PharmaPortal;
