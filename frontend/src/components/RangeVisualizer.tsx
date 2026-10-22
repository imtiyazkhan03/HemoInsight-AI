import React from 'react';
import { TestStatus } from '../types';

interface RangeVisualizerProps {
  value: number | null | undefined;
  refMin: number | null | undefined;
  refMax: number | null | undefined;
  unit?: string | null;
  status: TestStatus;
}

export const RangeVisualizer: React.FC<RangeVisualizerProps> = ({
  value,
  refMin,
  refMax,
  unit,
  status,
}) => {
  if (value === null || value === undefined || refMin === null || refMin === undefined || refMax === null || refMax === undefined) {
    return (
      <div className="text-xs text-slate-400 italic">
        Visual interval not available (requires min & max range)
      </div>
    );
  }

  // Handle open-ended intervals (e.g. > 40 where refMax is 999999, or < 100 where refMin is 0)
  const isOpenEndedHigh = refMax >= 99999;
  const effectiveRefMax = isOpenEndedHigh
    ? Math.max(refMin * 2.2, (value || refMin) * 1.3)
    : refMax;

  // Calculate percentage along the gauge
  const rangeSpan = Math.max(effectiveRefMax - refMin, 0.0001);
  const visualMin = Math.max(0, refMin - rangeSpan * 0.35);
  const visualMax = effectiveRefMax + rangeSpan * 0.35;
  const totalSpan = Math.max(visualMax - visualMin, 0.0001);

  const normalStartPct = Math.max(0, Math.min(100, ((refMin - visualMin) / totalSpan) * 100));
  const normalEndPct = isOpenEndedHigh
    ? 100
    : Math.max(0, Math.min(100, ((refMax - visualMin) / totalSpan) * 100));
  const normalWidthPct = Math.max(0, normalEndPct - normalStartPct);

  const valuePct = Math.max(2, Math.min(98, ((value - visualMin) / totalSpan) * 100));

  let markerColor = 'bg-teal-700 text-white border-white';
  let badgeLabel = 'In Range';
  if (status === 'LOW') {
    markerColor = 'bg-blue-600 text-white border-white';
    badgeLabel = 'Low';
  } else if (status === 'HIGH') {
    markerColor = 'bg-amber-600 text-white border-white';
    badgeLabel = 'High';
  }

  const upperLimitLabel = isOpenEndedHigh
    ? `No upper limit (≥ ${refMin})`
    : `${refMax} ${unit || ''}`;

  return (
    <div className="w-full pt-4 pb-2">
      {/* Visual Bar Container */}
      <div className="relative h-3 bg-slate-200 rounded-full overflow-hidden">
        {/* Normal / Within Range zone */}
        <div
          className="absolute top-0 bottom-0 bg-emerald-100 border-x border-emerald-300"
          style={{
            left: `${normalStartPct}%`,
            width: `${normalWidthPct}%`,
          }}
          title={isOpenEndedHigh ? `Reference Interval: ≥ ${refMin} ${unit || ''}` : `Reference Interval: ${refMin} - ${refMax} ${unit || ''}`}
        />
      </div>

      {/* Marker pin */}
      <div className="relative w-full h-0">
        <div
          className="absolute -top-3.5 transform -translate-x-1/2 flex flex-col items-center pointer-events-none"
          style={{ left: `${valuePct}%` }}
        >
          <div className={`px-1.5 py-0.5 rounded text-[10px] font-bold shadow-md ${markerColor}`}>
            {value} {unit || ''} ({badgeLabel})
          </div>
          <div className="w-0.5 h-3 bg-slate-900 mt-0.5" />
        </div>
      </div>

      {/* Range Labels underneath */}
      <div className="flex justify-between items-center text-[11px] text-slate-500 mt-4 px-1">
        <div>
          <span className="font-medium text-slate-600">Lower Limit:</span> {refMin} {unit || ''}
        </div>
        <div className="text-center">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            {isOpenEndedHigh ? `Reference: ≥ ${refMin} ${unit || ''}` : `Reference Zone: ${refMin} – ${refMax}`}
          </span>
        </div>
        <div>
          <span className="font-medium text-slate-600">Upper Limit:</span> {upperLimitLabel}
        </div>
      </div>
    </div>
  );
};
