import React, { useState } from 'react';
import { 
  FileText, Download, RotateCcw, CheckCircle2, 
  ArrowDownCircle, ArrowUpCircle, AlertCircle, Edit3,
  Calendar, User, Building, FileSpreadsheet, Sparkles
} from 'lucide-react';
import { AnalysisResponse, BloodTestItem, ReportMetadata } from '../types';
import { OverallResultBanner } from './OverallResultBanner';
import { ParameterTable } from './ParameterTable';
import { ParameterDetailModal } from './ParameterDetailModal';
import { ExplanationsSection } from './ExplanationsSection';
import { VerificationModal } from './VerificationModal';
import { MedicalDisclaimer } from './MedicalDisclaimer';
import { SymptomsChecklist } from './SymptomsChecklist';

interface ResultsDashboardProps {
  analysis: AnalysisResponse;
  onReset: () => void;
  onDownloadCsv: () => void;
  onDownloadPdf: () => void;
  onVerifyAndFinalize: (metadata: ReportMetadata, params: BloodTestItem[]) => void;
  isDownloadingPdf?: boolean;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  analysis,
  onReset,
  onDownloadCsv,
  onDownloadPdf,
  onVerifyAndFinalize,
  isDownloadingPdf = false,
}) => {
  const [selectedParam, setSelectedParam] = useState<BloodTestItem | null>(null);
  const [isVerificationOpen, setIsVerificationOpen] = useState(analysis.has_uncertain_values);

  const { metadata, summary, parameters } = analysis;

  const scrollToTable = () => {
    const el = document.getElementById('findings-table');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="py-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-in fade-in duration-200">
      {/* Top Header Card & Actions */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center space-x-2 text-xs font-semibold text-teal-800 bg-teal-50 px-3 py-1 rounded-full border border-teal-200 w-fit mb-3">
            <Sparkles className="w-3.5 h-3.5 text-teal-700" />
            <span>Clinical Biomarker Analysis • HemoInsight AI</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Laboratory Report Analysis
          </h1>

          {/* Metadata badges */}
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-600">
            <span className="flex items-center space-x-1.5 font-medium">
              <FileText className="w-4 h-4 text-teal-700" />
              <span>File: <b>{metadata.filename}</b> ({metadata.file_type})</span>
            </span>

            {metadata.patient_name && (
              <span className="flex items-center space-x-1.5">
                <User className="w-4 h-4 text-slate-400" />
                <span>Patient: <b>{metadata.patient_name}</b></span>
              </span>
            )}

            {metadata.collection_date && (
              <span className="flex items-center space-x-1.5">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span>Date: <b>{metadata.collection_date}</b></span>
              </span>
            )}

            {metadata.lab_name && (
              <span className="flex items-center space-x-1.5">
                <Building className="w-4 h-4 text-slate-400" />
                <span>Facility: <b>{metadata.lab_name}</b></span>
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => setIsVerificationOpen(true)}
            className="px-3.5 py-2 border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl transition-colors flex items-center space-x-1.5"
            title="Inspect or manually adjust extracted test names, values, or reference ranges"
          >
            <Edit3 className="w-3.5 h-3.5 text-slate-500" />
            <span>Verify & Edit Data</span>
          </button>

          <button
            onClick={onDownloadPdf}
            disabled={isDownloadingPdf}
            className="px-4 py-2 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow transition-colors flex items-center space-x-1.5 shadow-teal-700/20"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{isDownloadingPdf ? 'Generating PDF...' : 'Download PDF Report'}</span>
          </button>

          <button
            onClick={onDownloadCsv}
            className="px-3.5 py-2 border border-teal-200 bg-teal-50 hover:bg-teal-100 text-teal-800 text-xs font-semibold rounded-xl transition-colors flex items-center space-x-1.5"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-teal-700" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={onReset}
            className="px-3.5 py-2 border border-slate-200 hover:bg-slate-100 text-slate-600 text-xs font-semibold rounded-xl transition-colors flex items-center space-x-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Analyze Another</span>
          </button>
        </div>
      </div>

      {/* Prominent Overall Result Banner (Outcome A, B, or C) */}
      <OverallResultBanner
        summary={summary}
        onScrollToTable={scrollToTable}
        onOpenVerification={() => setIsVerificationOpen(true)}
      />

      {/* Correlated Clinical Symptoms Checklist for the Person */}
      {summary.patient_symptoms && summary.patient_symptoms.length > 0 && (
        <SymptomsChecklist
          symptoms={summary.patient_symptoms}
          affectedParameters={summary.affected_parameters}
        />
      )}

      {/* Summary Stat Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
        {/* Total Analyzed */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>Total Parameters</span>
            <FileText className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 mt-2">
            {summary.total_parameters}
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Extracted & categorized</span>
        </div>

        {/* Within Range */}
        <div className="bg-white p-4 rounded-xl border border-teal-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-teal-800 text-xs font-semibold">
            <span>Within Range</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-teal-900 mt-2">
            {summary.within_range_count}
          </div>
          <span className="text-[11px] text-teal-700 mt-1">Normal baseline</span>
        </div>

        {/* Low Results */}
        <div className="bg-white p-4 rounded-xl border border-blue-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-blue-800 text-xs font-semibold">
            <span>Low Results</span>
            <ArrowDownCircle className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-extrabold text-blue-900 mt-2">
            {summary.low_count}
          </div>
          <span className="text-[11px] text-blue-600 mt-1">Below lower limit</span>
        </div>

        {/* High Results */}
        <div className="bg-white p-4 rounded-xl border border-amber-200/80 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-amber-800 text-xs font-semibold">
            <span>High Results</span>
            <ArrowUpCircle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-extrabold text-amber-900 mt-2">
            {summary.high_count}
          </div>
          <span className="text-[11px] text-amber-700 mt-1">Above upper limit</span>
        </div>

        {/* Needs Review */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-slate-700 text-xs font-medium">
            <span>Needs Review</span>
            <AlertCircle className="w-4 h-4 text-rose-500" />
          </div>
          <div className={`text-2xl font-extrabold mt-2 ${summary.needs_review_count > 0 ? 'text-rose-600' : 'text-slate-800'}`}>
            {summary.needs_review_count}
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Missing range / check</span>
        </div>
      </div>

      {/* Detailed Findings Table */}
      <ParameterTable
        parameters={parameters}
        onSelectParameter={param => setSelectedParam(param)}
      />

      {/* AI Explanation of Abnormal Findings Section */}
      <ExplanationsSection
        parameters={parameters}
        onSelectParameter={param => setSelectedParam(param)}
      />

      {/* Medical Disclaimer Banner */}
      <MedicalDisclaimer />

      {/* Detail Slideout/Modal */}
      <ParameterDetailModal
        item={selectedParam}
        onClose={() => setSelectedParam(null)}
      />

      {/* Verification & Edit Modal */}
      <VerificationModal
        isOpen={isVerificationOpen}
        metadata={metadata}
        parameters={parameters}
        onClose={() => setIsVerificationOpen(false)}
        onConfirm={verifiedParams => {
          setIsVerificationOpen(false);
          onVerifyAndFinalize(metadata, verifiedParams);
        }}
      />
    </div>
  );
};
