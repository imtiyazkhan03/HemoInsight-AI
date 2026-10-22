import React, { useState } from 'react';
import { 
  Stethoscope, AlertTriangle, CheckCircle, ChevronDown, 
  ChevronUp, FlaskConical, MessageSquare, ShieldCheck, 
  Activity, ArrowRight, Sparkles 
} from 'lucide-react';
import { AssociatedCondition } from '../types';

interface AssociatedConditionsSectionProps {
  conditions: AssociatedCondition[];
  isLoading?: boolean;
}

export const AssociatedConditionsSection: React.FC<AssociatedConditionsSectionProps> = ({
  conditions,
  isLoading = false,
}) => {
  const [expandedId, setExpandedId] = useState<string | null>(conditions[0]?.id || null);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  if (!conditions || conditions.length === 0) {
    return null;
  }

  const getMatchBadgeStyle = (level: string, score: number) => {
    if (score >= 70 || level.includes('High')) {
      return {
        bg: 'bg-rose-50 text-rose-800 border-rose-200',
        dot: 'bg-rose-500',
        pill: 'High Correlation',
      };
    }
    if (score >= 45 || level.includes('Moderate')) {
      return {
        bg: 'bg-amber-50 text-amber-800 border-amber-200',
        dot: 'bg-amber-500',
        pill: 'Moderate Correlation',
      };
    }
    return {
      bg: 'bg-sky-50 text-sky-800 border-sky-200',
      dot: 'bg-sky-500',
      pill: 'Possible Consideration',
    };
  };

  return (
    <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm transition-all space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div className="flex items-start sm:items-center space-x-3.5">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-teal-700 to-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Stethoscope className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                Potential Clinical Condition Correlations
              </h2>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200 flex items-center space-x-1">
                <Sparkles className="w-3 h-3 text-teal-600" />
                <span>{conditions.length} Matched</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Correlating extracted biomarker patterns and physical symptoms with clinical differentials (e.g. Enteric/Typhoid Fever, Anemia, Thyroid or Hepatic changes) for physician consultation.
            </p>
          </div>
        </div>

        {/* Safety Badge */}
        <div className="flex items-center space-x-1.5 text-xs text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl shrink-0">
          <ShieldCheck className="w-4 h-4 text-teal-600" />
          <span>Non-Diagnostic • For Doctor Review</span>
        </div>
      </div>

      {isLoading && (
        <div className="py-6 text-center text-xs text-slate-500 flex items-center justify-center space-x-2">
          <div className="w-4 h-4 border-2 border-teal-600 border-t-transparent rounded-full animate-spin" />
          <span>Re-correlating conditions with updated symptoms...</span>
        </div>
      )}

      {/* Conditions Grid / Accordion */}
      <div className="space-y-4">
        {conditions.map(condition => {
          const isExpanded = expandedId === condition.id;
          const badgeStyle = getMatchBadgeStyle(condition.match_level, condition.match_score);

          return (
            <div
              key={condition.id}
              className={`rounded-xl border transition-all ${
                isExpanded 
                  ? 'border-teal-300 bg-gradient-to-b from-teal-50/20 via-white to-white shadow-sm ring-1 ring-teal-200/50' 
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              {/* Collapsed / Header View */}
              <button
                type="button"
                onClick={() => toggleExpand(condition.id)}
                className="w-full p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between text-left gap-3.5"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-bold text-slate-900 text-base">
                      {condition.condition_name}
                    </span>
                    <span className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
                      {condition.category}
                    </span>
                    <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border flex items-center space-x-1.5 ${badgeStyle.bg}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${badgeStyle.dot}`} />
                      <span>{condition.match_score}% {badgeStyle.pill}</span>
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2">
                    {condition.overview}
                  </p>
                </div>

                <div className="flex items-center space-x-3 shrink-0 self-end sm:self-center">
                  <span className="text-xs font-semibold text-teal-700 hover:text-teal-800 hidden sm:inline">
                    {isExpanded ? 'Hide Details' : 'View Diagnostics & Questions'}
                  </span>
                  <div className="w-7 h-7 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>
              </button>

              {/* Expanded Diagnostic Detail Drawer */}
              {isExpanded && (
                <div className="px-4 pb-5 sm:px-6 sm:pb-6 pt-2 border-t border-slate-100 space-y-5 animate-in fade-in duration-200">
                  {/* Biomarkers and Symptoms Chips */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                    {/* Matching Biomarkers */}
                    <div className="bg-slate-50/80 rounded-xl p-3.5 border border-slate-200/80 space-y-2">
                      <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-700">
                        <Activity className="w-3.5 h-3.5 text-rose-500" />
                        <span>Correlated Out-of-Range Biomarkers ({condition.matching_biomarkers.length})</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {condition.matching_biomarkers.map((bm, idx) => (
                          <span
                            key={idx}
                            className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-white border border-rose-200/90 text-rose-900 shadow-2xs"
                          >
                            {bm}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Matching Symptoms */}
                    <div className="bg-slate-50/80 rounded-xl p-3.5 border border-slate-200/80 space-y-2">
                      <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-700">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                        <span>Correlated Clinical Symptoms ({condition.matching_symptoms.length})</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {condition.matching_symptoms.length > 0 ? (
                          condition.matching_symptoms.map((symp, idx) => (
                            <span
                              key={idx}
                              className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-white border border-amber-200 text-amber-900 shadow-2xs"
                            >
                              {symp}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-500 italic">
                            Identified based on characteristic laboratory biomarker combination.
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Suggested Follow-up Tests to Discuss */}
                  {condition.suggested_follow_up_tests && condition.suggested_follow_up_tests.length > 0 && (
                    <div className="bg-teal-50/50 rounded-xl p-4 border border-teal-200/80 space-y-2.5">
                      <div className="flex items-center space-x-2 text-xs font-bold text-teal-900 uppercase tracking-wider">
                        <FlaskConical className="w-4 h-4 text-teal-700" />
                        <span>Recommended Confirmatory Tests to Discuss with Your Doctor</span>
                      </div>
                      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-700">
                        {condition.suggested_follow_up_tests.map((test, idx) => (
                          <li key={idx} className="flex items-start space-x-2 bg-white/90 p-2.5 rounded-lg border border-teal-100">
                            <CheckCircle className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                            <span>{test}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Doctor Discussion Points */}
                  {condition.doctor_discussion_points && condition.doctor_discussion_points.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-800 uppercase tracking-wider">
                        <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
                        <span>Physician Consultation Checklist</span>
                      </div>
                      <div className="space-y-1.5">
                        {condition.doctor_discussion_points.map((pt, idx) => (
                          <div
                            key={idx}
                            className="flex items-start space-x-2 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200/70"
                          >
                            <ArrowRight className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                            <span>{pt}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
};
