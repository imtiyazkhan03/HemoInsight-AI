import React, { useState, useMemo } from 'react';
import { Search, CheckCircle2, ArrowDownCircle, ArrowUpCircle, AlertCircle, Eye, Info } from 'lucide-react';
import { BloodTestItem, TestStatus } from '../types';

interface ParameterTableProps {
  parameters: BloodTestItem[];
  onSelectParameter: (item: BloodTestItem) => void;
}

export const ParameterTable: React.FC<ParameterTableProps> = ({
  parameters,
  onSelectParameter,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'ALL' | TestStatus>('ALL');

  // Count per status
  const counts = useMemo(() => {
    return {
      all: parameters.length,
      within_range: parameters.filter(p => p.status === 'WITHIN_RANGE').length,
      low: parameters.filter(p => p.status === 'LOW').length,
      high: parameters.filter(p => p.status === 'HIGH').length,
      needs_review: parameters.filter(p => p.status === 'NEEDS_REVIEW').length,
    };
  }, [parameters]);

  // Filtered list
  const filteredItems = useMemo(() => {
    return parameters.filter(item => {
      // Filter tab
      if (selectedFilter !== 'ALL' && item.status !== selectedFilter) {
        return false;
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const nameMatch = item.test_name.toLowerCase().includes(q);
        const catMatch = (item.category || '').toLowerCase().includes(q);
        const expMatch = (item.explanation || '').toLowerCase().includes(q);
        return nameMatch || catMatch || expMatch;
      }
      return true;
    });
  }, [parameters, selectedFilter, searchQuery]);

  const renderBadge = (status: TestStatus) => {
    switch (status) {
      case 'WITHIN_RANGE':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Within Range</span>
          </span>
        );
      case 'LOW':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <ArrowDownCircle className="w-3.5 h-3.5" />
            <span>Low</span>
          </span>
        );
      case 'HIGH':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            <ArrowUpCircle className="w-3.5 h-3.5" />
            <span>High</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Needs Review</span>
          </span>
        );
    }
  };

  return (
    <div id="findings-table" className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Controls Header */}
      <div className="p-5 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
          <button
            onClick={() => setSelectedFilter('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === 'ALL'
                ? 'bg-teal-700 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Results ({counts.all})
          </button>
          <button
            onClick={() => setSelectedFilter('WITHIN_RANGE')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === 'WITHIN_RANGE'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
            }`}
          >
            Within Range ({counts.within_range})
          </button>
          <button
            onClick={() => setSelectedFilter('LOW')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === 'LOW'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-blue-50 text-blue-800 hover:bg-blue-100'
            }`}
          >
            Low ({counts.low})
          </button>
          <button
            onClick={() => setSelectedFilter('HIGH')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              selectedFilter === 'HIGH'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'bg-amber-50 text-amber-900 hover:bg-amber-100'
            }`}
          >
            High ({counts.high})
          </button>
          {counts.needs_review > 0 && (
            <button
              onClick={() => setSelectedFilter('NEEDS_REVIEW')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedFilter === 'NEEDS_REVIEW'
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'bg-rose-50 text-rose-800 hover:bg-rose-100'
              }`}
            >
              Needs Review ({counts.needs_review})
            </button>
          )}
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search test name or category..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-600 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/75 border-b border-slate-200 text-slate-600 text-[11px] font-bold uppercase tracking-wider">
              <th className="py-3.5 px-4 sm:px-6">Test</th>
              <th className="py-3.5 px-4">Result</th>
              <th className="py-3.5 px-4">Reference Range</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4 sm:px-6">Explanation</th>
              <th className="py-3.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-12 text-slate-400 text-sm">
                  No parameters found matching the selected filters.
                </td>
              </tr>
            ) : (
              filteredItems.map(item => (
                <tr
                  key={item.id}
                  onClick={() => onSelectParameter(item)}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                >
                  {/* Test Name */}
                  <td className="py-3.5 px-4 sm:px-6">
                    <div className="font-semibold text-slate-900 group-hover:text-teal-700 transition-colors">
                      {item.test_name}
                    </div>
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 font-normal mt-0.5">
                      <span>{item.category || 'General'}</span>
                      {item.symptoms && item.symptoms.length > 0 && (
                        <span className="inline-flex items-center text-[10px] font-semibold bg-amber-50 text-amber-800 border border-amber-200/80 px-1.5 py-0.2 rounded-full">
                          {item.symptoms.length} symptoms linked
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Result */}
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-slate-900">
                      {item.value !== null && item.value !== undefined ? item.value : (item.raw_value || '—')}
                    </span>{' '}
                    <span className="text-xs text-slate-500 font-medium">{item.unit || ''}</span>
                    {item.lab_flag && (
                      <span className="ml-1.5 px-1 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-700">
                        {item.lab_flag}
                      </span>
                    )}
                  </td>

                  {/* Reference Range */}
                  <td className="py-3.5 px-4 text-xs text-slate-600">
                    {item.ref_min !== null && item.ref_max !== null ? (
                      <span className="font-medium">
                        {item.ref_min} – {item.ref_max} <span className="text-slate-400">{item.unit || ''}</span>
                      </span>
                    ) : (
                      <span className="text-slate-400 italic">
                        {item.ref_range_text || 'Not reported'}
                      </span>
                    )}
                  </td>

                  {/* Status */}
                  <td className="py-3.5 px-4">
                    {renderBadge(item.status)}
                  </td>

                  {/* Explanation summary */}
                  <td className="py-3.5 px-4 sm:px-6 text-xs text-slate-600 max-w-md truncate">
                    {item.explanation || 'Click to view full detail.'}
                  </td>

                  {/* Action */}
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectParameter(item);
                      }}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 text-xs font-semibold text-teal-700 hover:text-teal-900 hover:bg-teal-50 rounded-md transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Details</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer hint */}
      <div className="p-3 bg-slate-50 border-t border-slate-100 text-center text-xs text-slate-500 flex items-center justify-center space-x-2">
        <Info className="w-3.5 h-3.5 text-slate-400" />
        <span>Click any row to open the complete reference interval visualizer and evidence-supported explanation.</span>
      </div>
    </div>
  );
};
