import React, { useState } from 'react';
import { AlertCircle, CheckCircle, Plus, Trash2, X, RefreshCw } from 'lucide-react';
import { BloodTestItem, ReportMetadata } from '../types';

interface VerificationModalProps {
  isOpen: boolean;
  metadata: ReportMetadata;
  parameters: BloodTestItem[];
  onClose: () => void;
  onConfirm: (verifiedParams: BloodTestItem[]) => void;
  isLoading?: boolean;
}

export const VerificationModal: React.FC<VerificationModalProps> = ({
  isOpen,
  metadata,
  parameters,
  onClose,
  onConfirm,
  isLoading = false,
}) => {
  const [items, setItems] = useState<BloodTestItem[]>(parameters);
  const [prevParams, setPrevParams] = useState(parameters);

  if (prevParams !== parameters) {
    setPrevParams(parameters);
    setItems(parameters);
  }

  if (!isOpen) return null;

  const handleFieldChange = (id: string, field: keyof BloodTestItem, val: any) => {
    setItems(prev =>
      prev.map(item => {
        if (item.id === id) {
          const updated = { ...item, [field]: val };
          // If editing value or min/max, update numeric fields
          if (field === 'raw_value') {
            updated.raw_value = val;
            const cleanStr = String(val).trim();
            const num = parseFloat(cleanStr);
            updated.value = cleanStr !== '' && !isNaN(num) ? num : null;
          }
          if (field === 'ref_min') {
            const cleanStr = String(val).trim();
            const num = parseFloat(cleanStr);
            updated.ref_min = cleanStr !== '' && !isNaN(num) ? num : null;
          }
          if (field === 'ref_max') {
            const cleanStr = String(val).trim();
            const num = parseFloat(cleanStr);
            updated.ref_max = cleanStr !== '' && !isNaN(num) ? num : null;
          }
          // If both min, max, and value are now provided, clear verification flag
          if (updated.value !== null && updated.ref_min !== null && updated.ref_max !== null) {
            updated.needs_verification = false;
            updated.verification_reason = null;
          } else {
            updated.needs_verification = true;
            if (updated.value === null) {
              updated.verification_reason = "Missing or unparsed numerical value.";
            } else {
              updated.verification_reason = "Missing laboratory reference interval.";
            }
          }
          return updated;
        }
        return item;
      })
    );
  };

  const handleAddNewItem = () => {
    const newItem: BloodTestItem = {
      id: Math.random().toString(36).substring(2, 9),
      test_name: 'New Test Parameter',
      category: 'General Laboratory',
      value: 0,
      raw_value: '0',
      unit: '',
      ref_min: 0,
      ref_max: 100,
      status: 'WITHIN_RANGE',
      confidence: 'HIGH',
      needs_verification: false,
      questions_for_doctor: [],
    };
    setItems(prev => [...prev, newItem]);
  };

  const handleDeleteItem = (id: string) => {
    setItems(prev => prev.filter(item => item.id !== id));
  };

  const uncertainCount = items.filter(i => i.needs_verification).length;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6">
      <div className="bg-white rounded-2xl max-w-5xl w-full p-6 sm:p-8 shadow-2xl border border-slate-100 relative animate-in fade-in zoom-in-95 duration-150 max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-200 shrink-0">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 mb-2">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Verification & OCR Quality Check</span>
            </div>
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900">
              Verify Extracted Report Parameters
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              File: <span className="font-semibold text-slate-700">{metadata.filename}</span> •{' '}
              {uncertainCount > 0 ? (
                <span className="text-amber-700 font-semibold">{uncertainCount} parameters require range confirmation</span>
              ) : (
                <span className="text-emerald-700 font-semibold">All parameters have valid observed values and ranges</span>
              )}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Table Area */}
        <div className="overflow-y-auto flex-1 my-4 border border-slate-200 rounded-xl">
          <table className="w-full text-left border-collapse text-xs">
            <thead className="bg-slate-50 sticky top-0 border-b border-slate-200 z-10 text-slate-600 font-bold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-3">Status / Flag</th>
                <th className="py-3 px-3">Test Parameter Name</th>
                <th className="py-3 px-3 w-28">Measured Value</th>
                <th className="py-3 px-3 w-24">Unit</th>
                <th className="py-3 px-3 w-28">Ref Min</th>
                <th className="py-3 px-3 w-28">Ref Max</th>
                <th className="py-3 px-3 text-right">Delete</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map(item => (
                <tr
                  key={item.id}
                  className={item.needs_verification ? 'bg-amber-50/50' : 'hover:bg-slate-50'}
                >
                  {/* Status / Notice */}
                  <td className="py-2.5 px-3">
                    {item.needs_verification ? (
                      <div className="flex flex-col">
                        <span className="inline-flex items-center space-x-1 text-amber-700 font-semibold">
                          <AlertCircle className="w-3.5 h-3.5" />
                          <span>Review</span>
                        </span>
                        {item.verification_reason && (
                          <span className="text-[10px] text-amber-600 truncate max-w-xs" title={item.verification_reason}>
                            {item.verification_reason}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="inline-flex items-center space-x-1 text-emerald-700 font-semibold">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Ready</span>
                      </span>
                    )}
                  </td>

                  {/* Test Name */}
                  <td className="py-2.5 px-3">
                    <input
                      type="text"
                      value={item.test_name}
                      onChange={e => handleFieldChange(item.id, 'test_name', e.target.value)}
                      className="w-full px-2 py-1 bg-white border border-slate-200 rounded text-xs font-semibold focus:ring-1 focus:ring-teal-600 focus:outline-none"
                    />
                  </td>

                  {/* Value */}
                  <td className="py-2.5 px-3">
                    <input
                      type="text"
                      value={item.raw_value !== undefined && item.raw_value !== null ? item.raw_value : (item.value !== null && item.value !== undefined ? String(item.value) : '')}
                      onChange={e => handleFieldChange(item.id, 'raw_value', e.target.value)}
                      placeholder="e.g. 13.5"
                      className="w-full px-2 py-1 bg-white border border-slate-200 rounded text-xs font-bold focus:ring-1 focus:ring-teal-600 focus:outline-none"
                    />
                  </td>

                  {/* Unit */}
                  <td className="py-2.5 px-3">
                    <input
                      type="text"
                      value={item.unit || ''}
                      onChange={e => handleFieldChange(item.id, 'unit', e.target.value)}
                      placeholder="e.g. g/dL"
                      className="w-full px-2 py-1 bg-white border border-slate-200 rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none"
                    />
                  </td>

                  {/* Ref Min */}
                  <td className="py-2.5 px-3">
                    <input
                      type="number"
                      step="any"
                      value={item.ref_min !== null && item.ref_min !== undefined ? item.ref_min : ''}
                      onChange={e => handleFieldChange(item.id, 'ref_min', e.target.value)}
                      placeholder="Min limit"
                      className={`w-full px-2 py-1 bg-white border rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none ${
                        item.ref_min === null ? 'border-amber-400 bg-amber-50' : 'border-slate-200'
                      }`}
                    />
                  </td>

                  {/* Ref Max */}
                  <td className="py-2.5 px-3">
                    <input
                      type="number"
                      step="any"
                      value={item.ref_max !== null && item.ref_max !== undefined ? item.ref_max : ''}
                      onChange={e => handleFieldChange(item.id, 'ref_max', e.target.value)}
                      placeholder="Max limit"
                      className={`w-full px-2 py-1 bg-white border rounded text-xs focus:ring-1 focus:ring-teal-600 focus:outline-none ${
                        item.ref_max === null ? 'border-amber-400 bg-amber-50' : 'border-slate-200'
                      }`}
                    />
                  </td>

                  {/* Delete button */}
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-rose-50 transition-colors"
                      title="Remove row"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer actions */}
        <div className="pt-3 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
          <button
            onClick={handleAddNewItem}
            className="w-full sm:w-auto px-4 py-2 border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-lg transition-colors flex items-center justify-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Missing Test Row</span>
          </button>

          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <button
              onClick={onClose}
              className="w-1/2 sm:w-auto px-4 py-2 text-slate-600 hover:text-slate-800 text-xs font-semibold rounded-lg hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => onConfirm(items)}
              disabled={isLoading}
              className="w-1/2 sm:w-auto px-6 py-2 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow transition-colors flex items-center justify-center space-x-2"
            >
              {isLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
              <span>Confirm & Run Analysis</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
