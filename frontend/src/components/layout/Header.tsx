/**
 * Header Component
 * 
 * App header with logo, navigation, and user menu.
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Beaker, LogOut, ChevronDown } from 'lucide-react';
import { authApi } from '../../lib/api';
import { useAuthStore } from '../../stores/authStore';
import { getInitials } from '../../lib/utils';

export function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await authApi.logout();
        } catch (e) {
            // Ignore errors
        }
        logout();
        localStorage.removeItem('session_token');
        navigate('/login');
    };

    return (
        <header className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
            <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
                        <Beaker className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-xl font-bold gradient-text">CortexLab</span>
                </Link>

                {/* User Menu */}
                <div className="relative">
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors"
                    >
                        {user?.avatar_url ? (
                            <img
                                src={user.avatar_url}
                                alt={user.name}
                                className="w-8 h-8 rounded-full"
                            />
                        ) : (
                            <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center text-white text-sm font-medium">
                                {user ? getInitials(user.name) : '?'}
                            </div>
                        )}
                        <span className="text-sm font-medium text-[var(--color-text-primary)]">
                            {user?.name || 'User'}
                        </span>
                        <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
                    </button>

                    {isMenuOpen && (
                        <>
                            <div
                                className="fixed inset-0 z-10"
                                onClick={() => setIsMenuOpen(false)}
                            />
                            <div className="absolute right-0 top-full mt-2 w-48 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg shadow-lg z-20 py-1">
                                <div className="px-4 py-2 border-b border-[var(--color-border)]">
                                    <p className="text-sm font-medium">{user?.name}</p>
                                    <p className="text-xs text-[var(--color-text-muted)]">{user?.email}</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[var(--color-text-primary)] hover:bg-[var(--color-bg-tertiary)] transition-colors"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign out
                                </button>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
}
