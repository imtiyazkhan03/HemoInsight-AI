import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, CheckCircle2, MessageSquare, ShieldAlert, Activity } from 'lucide-react';
import { BloodTestItem } from '../types';

interface ExplanationsSectionProps {
  parameters: BloodTestItem[];
  onSelectParameter: (item: BloodTestItem) => void;
}

export const ExplanationsSection: React.FC<ExplanationsSectionProps> = ({
  parameters,
  onSelectParameter,
}) => {
  const abnormalItems = parameters.filter(
    p => p.status === 'LOW' || p.status === 'HIGH' || p.status === 'NEEDS_REVIEW'
  );

  const [expandedId, setExpandedId] = useState<string | null>(
    abnormalItems.length > 0 ? abnormalItems[0].id : null
  );

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
          <HelpCircle className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-900 tracking-tight">
            What Do Your Results Mean?
          </h3>
          <p className="text-xs text-slate-500">
            Evidence-based context for flagged parameters and clinical next steps
          </p>
        </div>
      </div>

      {abnormalItems.length === 0 ? (
        <div className="bg-teal-50/70 border border-teal-200 rounded-xl p-5 flex items-start space-x-3">
          <CheckCircle2 className="w-5 h-5 text-teal-700 shrink-0 mt-0.5" />
          <div className="text-sm text-slate-700 leading-relaxed">
            <span className="font-bold text-teal-900 block mb-1">
              No Out-of-Range Parameters Flagged
            </span>
            All analyzed blood parameters in this report fall within their supplied laboratory reference ranges. 
            No elevated or reduced test levels were detected. Please remember that reference intervals serve as screening baselines 
            and should always be considered in combination with your overall clinical picture and physical symptoms.
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {abnormalItems.map(item => {
            const isExpanded = expandedId === item.id;
            const isLow = item.status === 'LOW';
            const isHigh = item.status === 'HIGH';

            return (
              <div
                key={item.id}
                className={`border rounded-xl transition-all overflow-hidden ${
                  isExpanded ? 'border-teal-300 ring-1 ring-teal-100 bg-white' : 'border-slate-200 bg-slate-50/60 hover:bg-slate-50'
                }`}
              >
                {/* Header row */}
                <button
                  onClick={() => toggleExpand(item.id)}
                  className="w-full text-left p-4 sm:p-5 flex items-center justify-between gap-4"
                >
                  <div className="flex items-center space-x-3">
                    <span
                      className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                        isLow ? 'bg-blue-500' : isHigh ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-900">{item.test_name}</span>
                        <span
                          className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                            isLow
                              ? 'bg-blue-100 text-blue-800'
                              : isHigh
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-rose-100 text-rose-800'
                          }`}
                        >
                          {item.status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Observed:{' '}
                        <span className="font-semibold text-slate-700">
                          {item.value !== null ? `${item.value} ${item.unit || ''}` : item.raw_value}
                        </span>{' '}
                        • Reference Interval:{' '}
                        <span className="font-medium text-slate-600">
                          {item.ref_min !== null && item.ref_max !== null
                            ? `${item.ref_min} - ${item.ref_max} ${item.unit || ''}`
                            : (item.ref_range_text || 'Not reported')}
                        </span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-slate-400">
                    <span className="text-xs text-teal-700 font-semibold hidden sm:inline">
                      {isExpanded ? 'Hide Details' : 'View Explanation'}
                    </span>
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-1 border-t border-slate-100 text-sm space-y-4 animate-in fade-in duration-150">
                    {/* Primary Plain-Language Explanation */}
                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-200/80 leading-relaxed text-slate-700">
                      <span className="font-bold text-slate-900 block mb-1">
                        Plain-Language Analysis:
                      </span>
                      {item.explanation}
                    </div>

                    {/* Context and Why this is not a diagnosis */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                      <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-3 text-amber-900">
                        <span className="font-bold flex items-center space-x-1 mb-1">
                          <ShieldAlert className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                          <span>Why this alone is NOT a diagnosis</span>
                        </span>
                        A single isolated blood value is not indicative of a specific illness on its own. 
                        Hydration, circadian rhythms, dietary intake, acute viral exposures, and medication timing can temporarily shift numerical levels.
                      </div>

                      <div className="bg-teal-50/60 border border-teal-200 rounded-lg p-3 text-teal-900">
                        <span className="font-bold flex items-center space-x-1 mb-1">
                          <MessageSquare className="w-3.5 h-3.5 text-teal-700 shrink-0" />
                          <span>Recommended Next Step</span>
                        </span>
                        Bring this finding to your doctor or healthcare provider. They will evaluate this parameter alongside your medical history, current symptoms, and complementary lab tests.
                      </div>
                    </div>

                    {/* Symptoms Checklist for the Person */}
                    {item.symptoms && item.symptoms.length > 0 && (
                      <div className="bg-amber-50/70 border border-amber-200/90 rounded-xl p-3.5">
                        <span className="text-xs font-bold text-amber-950 flex items-center space-x-1.5 mb-2">
                          <Activity className="w-3.5 h-3.5 text-amber-700 shrink-0" />
                          <span>Potential Physical Symptoms to Note for Your Doctor:</span>
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                          {item.symptoms.map((symp, sIdx) => (
                            <div key={sIdx} className="text-xs text-amber-900/90 flex items-start space-x-1.5 bg-white/70 rounded-md px-2.5 py-1 border border-amber-100">
                              <span className="text-amber-600 font-bold shrink-0">•</span>
                              <span>{symp}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Questions checklist */}
                    {item.questions_for_doctor && item.questions_for_doctor.length > 0 && (
                      <div className="pt-1">
                        <span className="text-xs font-bold text-slate-800 block mb-1.5">
                          Questions to ask your physician:
                        </span>
                        <ul className="space-y-1">
                          {item.questions_for_doctor.map((q, idx) => (
                            <li key={idx} className="text-xs text-slate-600 flex items-start space-x-2">
                              <span className="text-teal-700 font-bold shrink-0">•</span>
                              <span>{q}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="pt-2 border-t border-slate-100 flex justify-end">
                      <button
                        type="button"
                        onClick={() => onSelectParameter(item)}
                        className="text-xs font-semibold text-teal-700 hover:text-teal-800 hover:underline flex items-center space-x-1"
                      >
                        <span>View Visual Gauge for {item.test_name} →</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
