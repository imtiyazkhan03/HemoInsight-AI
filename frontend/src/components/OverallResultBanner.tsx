import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, ArrowDownCircle, ArrowUpCircle, ChevronDown } from 'lucide-react';
import { ReportSummary } from '../types';

interface OverallResultBannerProps {
  summary: ReportSummary;
  onScrollToTable: () => void;
  onOpenVerification?: () => void;
}

export const OverallResultBanner: React.FC<OverallResultBannerProps> = ({
  summary,
  onScrollToTable,
  onOpenVerification,
}) => {
  const { overall_outcome, overall_title, overall_message, low_count, high_count, within_range_count, total_parameters, needs_review_count, affected_parameters } = summary;

  if (overall_outcome === 'NO_ABNORMAL_DETECTED') {
    return (
      <div className="bg-gradient-to-r from-teal-50 via-emerald-50 to-teal-50 border border-teal-200 rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-xl bg-teal-700 text-white flex items-center justify-center shrink-0 shadow-md shadow-teal-700/20">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <div>
              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-100 text-teal-800 mb-2">
                All Analyzed Results Within Limits
              </div>
              <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {overall_title}
              </h2>
              <p className="mt-2 text-sm text-slate-700 max-w-2xl leading-relaxed">
                {overall_message}
              </p>

              {/* Stats badges */}
              <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold text-slate-700">
                <span className="bg-white/90 border border-teal-200 px-3 py-1 rounded-lg">
                  Analyzed Parameters: <b>{total_parameters}</b>
                </span>
                <span className="bg-teal-100/90 text-teal-900 border border-teal-300 px-3 py-1 rounded-lg">
                  Within Range: <b>{within_range_count}</b>
                </span>
                {needs_review_count > 0 && (
                  <span className="bg-amber-100/90 text-amber-900 border border-amber-300 px-3 py-1 rounded-lg">
                    Needing Review: <b>{needs_review_count}</b>
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="shrink-0 w-full md:w-auto">
            <button
              onClick={onScrollToTable}
              className="w-full md:w-auto px-5 py-2.5 bg-teal-700 hover:bg-teal-800 text-white text-sm font-semibold rounded-xl shadow transition-colors flex items-center justify-center space-x-2"
            >
              <span>View All Results</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (overall_outcome === 'SOME_NEED_ATTENTION') {
    return (
      <div className="bg-gradient-to-r from-amber-50 via-rose-50/40 to-amber-50 border border-amber-200 rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-xl bg-amber-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-amber-600/20">
              <AlertTriangle className="w-7 h-7" />
            </div>
            <div>
              <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 mb-2">
                Out-of-Range Parameters Flagged
              </div>
              <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                {overall_title}
              </h2>
              <p className="mt-2 text-sm text-slate-700 max-w-2xl leading-relaxed">
                {overall_message}
              </p>

              {/* Counts */}
              <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold">
                {low_count > 0 && (
                  <span className="inline-flex items-center space-x-1 bg-blue-50 text-blue-800 border border-blue-200 px-3 py-1 rounded-lg">
                    <ArrowDownCircle className="w-3.5 h-3.5" />
                    <span>Low Results: <b>{low_count}</b></span>
                  </span>
                )}
                {high_count > 0 && (
                  <span className="inline-flex items-center space-x-1 bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1 rounded-lg">
                    <ArrowUpCircle className="w-3.5 h-3.5" />
                    <span>High Results: <b>{high_count}</b></span>
                  </span>
                )}
                <span className="bg-teal-50 text-teal-800 border border-teal-200 px-3 py-1 rounded-lg">
                  Within Range: <b>{within_range_count}</b>
                </span>
                {needs_review_count > 0 && (
                  <span className="bg-slate-100 text-slate-700 border border-slate-200 px-3 py-1 rounded-lg">
                    Needs Review: <b>{needs_review_count}</b>
                  </span>
                )}
              </div>

              {/* Affected parameters list */}
              {affected_parameters.length > 0 && (
                <div className="mt-3 text-xs text-slate-600">
                  <span className="font-semibold text-slate-700">Affected parameters:</span>{' '}
                  <span className="text-slate-800 font-medium">{affected_parameters.join(', ')}</span>
                </div>
              )}
            </div>
          </div>

          <div className="shrink-0 w-full md:w-auto">
            <button
              onClick={onScrollToTable}
              className="w-full md:w-auto px-5 py-2.5 bg-amber-700 hover:bg-amber-800 text-white text-sm font-semibold rounded-xl shadow transition-colors flex items-center justify-center space-x-2"
            >
              <span>View Findings</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Outcome C: Insufficient data
  return (
    <div className="bg-gradient-to-r from-rose-50 via-amber-50/50 to-rose-50 border border-rose-200 rounded-2xl p-6 sm:p-8 shadow-sm">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 rounded-xl bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-rose-600/20">
            <AlertCircle className="w-7 h-7" />
          </div>
          <div>
            <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 mb-2">
              Verification Required
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              {overall_title}
            </h2>
            <p className="mt-2 text-sm text-slate-700 max-w-2xl leading-relaxed">
              {overall_message}
            </p>
            <div className="mt-3 text-xs font-medium text-rose-700 bg-rose-100/60 border border-rose-200 rounded-lg p-2.5 max-w-xl">
              Medical Safety Note: An incomplete or partially extracted report cannot be classified as normal. Please review the highlighted parameters below to verify or supply the missing reference ranges.
            </div>
          </div>
        </div>

        {onOpenVerification && (
          <div className="shrink-0 w-full md:w-auto">
            <button
              onClick={onOpenVerification}
              className="w-full md:w-auto px-5 py-2.5 bg-rose-700 hover:bg-rose-800 text-white text-sm font-semibold rounded-xl shadow transition-colors flex items-center justify-center space-x-2"
            >
              <span>Review & Correct Data</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
