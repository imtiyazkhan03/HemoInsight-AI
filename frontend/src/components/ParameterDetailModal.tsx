import React from 'react';
import { X, CheckCircle2, ArrowDownCircle, ArrowUpCircle, HelpCircle, MessageSquare, AlertCircle } from 'lucide-react';
import { BloodTestItem } from '../types';
import { RangeVisualizer } from './RangeVisualizer';

interface ParameterDetailModalProps {
  item: BloodTestItem | null;
  onClose: () => void;
}

export const ParameterDetailModal: React.FC<ParameterDetailModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  const getStatusBadge = () => {
    switch (item.status) {
      case 'WITHIN_RANGE':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-4 h-4" />
            <span>Within Range</span>
          </span>
        );
      case 'LOW':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
            <ArrowDownCircle className="w-4 h-4" />
            <span>Below Reference Range (Low)</span>
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
            <ArrowUpCircle className="w-4 h-4" />
            <span>Above Reference Range (High)</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">
            <AlertCircle className="w-4 h-4" />
            <span>Needs Review</span>
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-slate-100 relative animate-in fade-in zoom-in-95 duration-150">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-start justify-between pr-8">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-teal-700 bg-teal-50 px-2.5 py-1 rounded-md border border-teal-100">
              {item.category || 'Laboratory Investigation'}
            </span>
            <h3 className="text-2xl font-bold text-slate-900 mt-2">
              {item.test_name}
            </h3>
            {item.description && (
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                {item.description}
              </p>
            )}
          </div>
        </div>

        {/* Results Banner Box */}
        <div className="mt-6 bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-medium text-slate-500 block">Measured Result</span>
            <div className="text-2xl font-extrabold text-slate-900 mt-0.5">
              {item.value !== null && item.value !== undefined ? item.value : (item.raw_value || 'N/A')}{' '}
              <span className="text-sm font-semibold text-slate-500">{item.unit || ''}</span>
            </div>
          </div>

          <div className="text-left sm:text-right">
            <span className="text-xs font-medium text-slate-500 block">Report Reference Interval</span>
            <div className="text-sm font-bold text-slate-800 mt-0.5">
              {item.ref_range_text
                ? item.ref_range_text
                : item.ref_min !== null && item.ref_max !== null
                ? item.ref_max >= 99999
                  ? `≥ ${item.ref_min} ${item.unit || ''}`
                  : `${item.ref_min} - ${item.ref_max} ${item.unit || ''}`
                : 'Not specified in report'}
            </div>
          </div>

          <div className="sm:self-center">
            {getStatusBadge()}
          </div>
        </div>

        {/* Range Visualizer Gauge */}
        <div className="mt-5 bg-white border border-slate-200 rounded-xl p-4">
          <span className="text-xs font-semibold text-slate-700 block mb-1">Interval Mapping</span>
          <RangeVisualizer
            value={item.value}
            refMin={item.ref_min}
            refMax={item.ref_max}
            unit={item.unit}
            status={item.status}
          />
        </div>

        {/* Plain Language Explanation */}
        <div className="mt-6">
          <h4 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-teal-700" />
            <span>Plain Language Explanation</span>
          </h4>
          <div className="mt-2 text-sm text-slate-700 leading-relaxed bg-teal-50/50 border border-teal-100 rounded-xl p-4">
            {item.explanation || 'No explanation available for this parameter.'}
          </div>
        </div>

        {/* Correlated Clinical Symptoms */}
        {item.symptoms && item.symptoms.length > 0 && (
          <div className="mt-5">
            <h4 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
              <span>Physical Symptoms Correlated with this Finding</span>
            </h4>
            <p className="text-xs text-slate-500 mt-1 mb-2">
              If your level is {item.status.toLowerCase().replace('_', ' ')}, a person might commonly experience or report:
            </p>
            <div className="flex flex-wrap gap-2">
              {item.symptoms.map((s, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center text-xs font-medium bg-amber-50 text-amber-900 border border-amber-200/70 px-2.5 py-1 rounded-lg"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Questions for Doctor */}
        {item.questions_for_doctor && item.questions_for_doctor.length > 0 && (
          <div className="mt-5">
            <h4 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-teal-700" />
              <span>Questions to Discuss with Your Doctor</span>
            </h4>
            <ul className="mt-2 space-y-1.5">
              {item.questions_for_doctor.map((q, idx) => (
                <li key={idx} className="text-xs text-slate-700 flex items-start space-x-2">
                  <span className="text-teal-700 font-bold shrink-0">•</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-semibold rounded-lg transition-colors"
          >
            Close Detail
          </button>
        </div>
      </div>
    </div>
  );
};
