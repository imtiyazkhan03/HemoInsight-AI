import React from 'react';
import { Activity, ShieldCheck } from 'lucide-react';

const currentYear = new Date().getFullYear();

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 text-xs border-t border-slate-800 py-10 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-teal-700 to-teal-500 flex items-center justify-center text-white shadow-md shadow-teal-900/30">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <span className="font-extrabold text-white text-sm">HemoInsight AI</span>
              <span className="text-slate-500 ml-2">Smart Blood Report Analyzer • Powered by VitalScan Engine</span>
            </div>
          </div>

          <div className="flex items-center space-x-6 text-slate-400">
            <span>•</span>
            <span className="flex items-center space-x-1.5 text-slate-300">
              <ShieldCheck className="w-4 h-4 text-teal-400" />
              <span>HIPAA-Conscious / Client-Side Safe</span>
            </span>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-slate-500 text-[11px] gap-3">
          <p>
            © {currentYear} HemoInsight AI  Built for evidence-supported laboratory report interpretation.
          </p>
          <p className="flex items-center space-x-1">
            <span>Engineered with precision for clinical literacy & healthcare clarity</span>
          </p>
        </div>
      </div>
    </footer>
  );
};
