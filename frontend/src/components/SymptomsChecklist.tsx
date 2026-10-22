import React, { useState } from 'react';
import { Activity, CheckSquare, Square, Info, Copy, Check, RotateCcw } from 'lucide-react';

interface SymptomsChecklistProps {
  symptoms: string[];
  affectedParameters: string[];
  onSelectedSymptomsChange?: (selected: string[]) => void;
}

export const SymptomsChecklist: React.FC<SymptomsChecklistProps> = ({
  symptoms,
  affectedParameters,
  onSelectedSymptomsChange,
}) => {
  const [checkedSymptoms, setCheckedSymptoms] = useState<Record<string, boolean>>({});
  const [filterMode, setFilterMode] = useState<'all' | 'checked'>('all');
  const [copied, setCopied] = useState<boolean>(false);

  if (!symptoms || symptoms.length === 0) {
    return null;
  }

  const notifyChange = (updated: Record<string, boolean>) => {
    if (onSelectedSymptomsChange) {
      const activeList = Object.keys(updated).filter(k => updated[k]);
      onSelectedSymptomsChange(activeList);
    }
  };

  const toggleSymptom = (symp: string) => {
    setCheckedSymptoms(prev => {
      const next = {
        ...prev,
        [symp]: !prev[symp],
      };
      notifyChange(next);
      return next;
    });
  };

  const selectAll = () => {
    const allChecked: Record<string, boolean> = {};
    symptoms.forEach(s => { allChecked[s] = true; });
    setCheckedSymptoms(allChecked);
    notifyChange(allChecked);
  };

  const clearAll = () => {
    setCheckedSymptoms({});
    setFilterMode('all');
    notifyChange({});
  };

  const checkedCount = Object.values(checkedSymptoms).filter(Boolean).length;

  const handleCopy = () => {
    const activeList = checkedCount > 0
      ? symptoms.filter(s => checkedSymptoms[s])
      : symptoms;

    const textToCopy = [
      `--- HemoInsight AI: Correlated Clinical Symptoms Checklist ---`,
      `Flagged Parameters: ${affectedParameters.join(', ')}`,
      `Noted Symptoms for Doctor Discussion:`,
      ...activeList.map(s => `• ${s}`),
    ].join('\n');

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const displayedSymptoms = filterMode === 'checked'
    ? symptoms.filter(s => checkedSymptoms[s])
    : symptoms;

  return (
    <div className="bg-gradient-to-br from-amber-50/90 via-white to-orange-50/60 rounded-2xl border border-amber-200/90 p-6 sm:p-7 shadow-sm transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0 border border-amber-200 shadow-sm">
            <Activity className="w-5 h-5 text-amber-700" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <span>Potential Physical Symptoms Checklist</span>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
                {symptoms.length} Correlated
              </span>
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Based on out-of-range parameters ({affectedParameters.slice(0, 3).join(', ')}{affectedParameters.length > 3 ? '...' : ''}), here are common physical symptoms people report. Check any you are experiencing to discuss with your doctor.
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleCopy}
            className="px-3 py-1.5 bg-white border border-amber-300 hover:bg-amber-50 text-amber-900 text-xs font-semibold rounded-lg shadow-sm flex items-center space-x-1.5 transition-colors"
            title="Copy checklist to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-amber-700" />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy Checklist'}</span>
          </button>

          {checkedCount > 0 ? (
            <button
              type="button"
              onClick={clearAll}
              className="px-2.5 py-1.5 bg-white/80 hover:bg-white border border-slate-300 text-slate-600 text-xs font-medium rounded-lg flex items-center space-x-1 transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Clear ({checkedCount})</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={selectAll}
              className="px-2.5 py-1.5 bg-white/80 hover:bg-white border border-slate-300 text-slate-600 text-xs font-medium rounded-lg transition-colors"
            >
              Select All
            </button>
          )}

          {checkedCount > 0 && (
            <div className="flex rounded-lg border border-amber-300 bg-white p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setFilterMode('all')}
                className={`px-2 py-0.5 rounded-md font-medium transition-colors ${
                  filterMode === 'all' ? 'bg-amber-100 text-amber-900 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All ({symptoms.length})
              </button>
              <button
                type="button"
                onClick={() => setFilterMode('checked')}
                className={`px-2 py-0.5 rounded-md font-medium transition-colors ${
                  filterMode === 'checked' ? 'bg-amber-100 text-amber-900 font-semibold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Noted ({checkedCount})
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Grid of Symptoms */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 mt-4">
        {displayedSymptoms.map((symptom, idx) => {
          const isChecked = !!checkedSymptoms[symptom];
          return (
            <button
              key={idx}
              type="button"
              onClick={() => toggleSymptom(symptom)}
              className={`text-left p-3 rounded-xl border text-xs transition-all flex items-start space-x-2.5 cursor-pointer ${
                isChecked
                  ? 'bg-amber-100/90 border-amber-400 text-amber-950 font-medium shadow-sm ring-1 ring-amber-300/60'
                  : 'bg-white/85 hover:bg-amber-50/60 border-amber-200/70 text-slate-700 hover:border-amber-300'
              }`}
            >
              <span className="mt-0.5 shrink-0 text-amber-700">
                {isChecked ? (
                  <CheckSquare className="w-4 h-4 text-amber-800" />
                ) : (
                  <Square className="w-4 h-4 text-slate-400" />
                )}
              </span>
              <span className="leading-snug">{symptom}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-4 pt-3.5 border-t border-amber-200/70 flex items-start space-x-2 text-[11px] text-slate-500">
        <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <span>
          <b>Clinical note:</b> Experiencing zero symptoms does not invalidate an out-of-range lab result, nor does having these symptoms confirm any illness. Share this checklist with your physician during consultation for a comprehensive diagnostic review.
        </span>
      </div>
    </div>
  );
};
