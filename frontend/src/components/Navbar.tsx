import React from 'react';
import { Activity, ShieldCheck, FileText, HelpCircle } from 'lucide-react';

interface NavbarProps {
  onNavigate: (section: 'landing' | 'upload' | 'samples' | 'how-it-works') => void;
  isBackendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate, isBackendOnline }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => onNavigate('landing')}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-800 to-teal-600 flex items-center justify-center text-white shadow-md shadow-teal-700/20 group-hover:from-teal-700 group-hover:to-teal-500 transition-all duration-200">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-extrabold text-slate-900 tracking-tight">HemoInsight AI</span>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 bg-teal-100 text-teal-800 rounded-full border border-teal-200">
                VitalScan Core
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">Smart Blood Report Analyzer & Clinical Intelligence</p>
          </div>
        </div>

        {/* Links */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-600">
          <button 
            onClick={() => onNavigate('landing')} 
            className="hover:text-teal-700 transition-colors"
          >
            Home
          </button>
          <button 
            onClick={() => onNavigate('how-it-works')} 
            className="hover:text-teal-700 transition-colors flex items-center space-x-1"
          >
            <HelpCircle className="w-4 h-4 text-slate-400" />
            <span>How It Works</span>
          </button>
          <button 
            onClick={() => onNavigate('samples')} 
            className="hover:text-teal-700 transition-colors flex items-center space-x-1"
          >
            <FileText className="w-4 h-4 text-slate-400" />
            <span>Sample Reports</span>
          </button>
        </nav>

        {/* Status & CTA */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
            <span className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
            <span className="hidden sm:inline">{isBackendOnline ? 'Analysis Engine Ready' : 'Connecting Engine...'}</span>
          </div>

          <button
            onClick={() => onNavigate('upload')}
            className="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-sm font-semibold rounded-lg shadow-sm transition-all shadow-teal-700/20 hover:shadow-teal-700/30 flex items-center space-x-2"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Analyze Report</span>
          </button>
        </div>
      </div>
    </header>
  );
};
