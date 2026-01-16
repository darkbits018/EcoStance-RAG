import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Link2, Database, Mail } from 'lucide-react';
import './layout.css'; // specific layout styles if needed

export const AppLayout: React.FC = () => {
    return (
        <div className="app-layout">
            <aside className="sidebar glass-panel">
                <div className="logo-area">
                    <h3>Custom CRM</h3>
                </div>
                <nav className="nav-menu">
                    <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <LayoutDashboard size={20} />
                        <span>Dashboard</span>
                    </NavLink>
                    <NavLink to="/connections" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Link2 size={20} />
                        <span>Connections</span>
                    </NavLink>
                    <NavLink to="/dumps" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Database size={20} />
                        <span>Dumps</span>
                    </NavLink>
                    <NavLink to="/emails" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Mail size={20} />
                        <span>Emails</span>
                    </NavLink>
                </nav>
            </aside>
            <main className="content-area">
                <Outlet />
            </main>
        </div>
    );
};
