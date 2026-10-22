import React from 'react';
import { ShieldAlert } from 'lucide-react';

export const MedicalDisclaimer: React.FC = () => {
  return (
    <div className="bg-slate-100/90 border border-slate-300/80 rounded-2xl p-5 text-slate-700 text-xs leading-relaxed">
      <div className="flex items-start space-x-3">
        <ShieldAlert className="w-5 h-5 text-teal-800 shrink-0 mt-0.5" />
        <div className="space-y-1.5">
          <span className="font-bold text-slate-900 block text-sm">
            Important Medical & Educational Safety Notice
          </span>
          <p>
            <b>HemoInsight AI</b> is an educational blood report interpretation and clinical literacy tool designed for academic Experiment 9. 
            It is <b>NOT</b> a diagnostic medical device and cannot diagnose illnesses, prescribe medication, or formulate treatment protocols.
          </p>
          <p className="text-slate-600">
            • <b>Reference intervals vary:</b> Laboratory reference ranges differ significantly between different hospitals, diagnostic machines, test reagents, and geographic regions. Always rely on the specific reference range provided by the testing laboratory.
            <br />
            • <b>Holistic context required:</b> A normal blood result does not guarantee the absence of illness, nor does a minor deviation indicate a severe medical condition. Blood tests must always be interpreted alongside clinical symptoms, physical examinations, and personal medical history.
            <br />
            • <b>Consult a physician:</b> If you experience concerning symptoms, persistent discomfort, or if any test result is significantly outside expected ranges, immediately consult a qualified healthcare provider.
          </p>
        </div>
      </div>
    </div>
  );
};
