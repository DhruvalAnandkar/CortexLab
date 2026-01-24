/**
 * Main Layout
 * 
 * App shell with header and content area.
 */

import { Outlet } from 'react-router-dom';
import { Header } from './Header';

export function MainLayout() {
    return (
        <div className="min-h-screen bg-[var(--color-bg-primary)]">
            <Header />
            <main className="max-w-7xl mx-auto px-4 py-6">
                <Outlet />
            </main>
        </div>
    );
}
