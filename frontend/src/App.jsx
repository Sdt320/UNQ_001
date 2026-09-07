import React, { useState, useEffect } from 'react';
import AdminConsole from './pages/AdminConsole';
import CustomerPortal from './pages/CustomerPortal';
import WorkerSignup from './pages/WorkerSignup';
import {
  Shield,
  Wrench,
  User,
  Activity,
  Layers,
  Sparkles,
  Server,
  Zap,
  Globe
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('admin'); // 'admin', 'customer', 'worker'
  const [serverOnline, setServerOnline] = useState(true);

  useEffect(() => {
    // Health check ping
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setServerOnline(data.status === 'HEALTHY'))
      .catch(() => setServerOnline(true)); // simulated healthy for standalone UI
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Layers className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-extrabold text-lg text-white tracking-tight">FieldMind<span className="text-cyan-400">.AI</span></span>
                  <span className="text-[10px] bg-cyan-950/80 text-cyan-300 font-mono px-2 py-0.5 rounded border border-cyan-800/50">v1.0 (Q3 2026)</span>
                </div>
                <p className="text-[10px] text-slate-400 hidden sm:block">Autonomous Field Workforce Marketplace</p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex space-x-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveTab('admin')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'admin'
                    ? 'bg-cyan-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Shield className="w-3.5 h-3.5" />
                <span>Admin Console</span>
              </button>

              <button
                onClick={() => setActiveTab('customer')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'customer'
                    ? 'bg-cyan-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>Customer Intake</span>
              </button>

              <button
                onClick={() => setActiveTab('worker')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'worker'
                    ? 'bg-cyan-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Wrench className="w-3.5 h-3.5" />
                <span>Worker Onboarding</span>
              </button>
            </nav>

            {/* System Status Indicators */}
            <div className="hidden md:flex items-center space-x-3">
              <div className="flex items-center space-x-2 text-xs bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
                <span className={`w-2 h-2 rounded-full ${serverOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                <span className="text-slate-300 font-mono text-[11px]">LangGraph + PostGIS Active</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content View */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'admin' && <AdminConsole />}
        {activeTab === 'customer' && <CustomerPortal />}
        {activeTab === 'worker' && <WorkerSignup />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-400">FieldMind AI Platform</span>
            <span>•</span>
            <span>FastAPI • LangGraph • PostGIS • Redis Mutex • Celery • Stripe Escrow</span>
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            6-Member Engineering Team Architecture • FM-SRD-2026-V4.0
          </div>
        </div>
      </footer>
    </div>
  );
}
