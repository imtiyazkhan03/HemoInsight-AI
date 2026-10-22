import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, AlertCircle, X, ArrowRight, ShieldCheck, RefreshCw, FileSpreadsheet, Image as ImageIcon } from 'lucide-react';
import { SampleReport } from '../types';

interface UploadSectionProps {
  onAnalyzeFile: (file: File) => void;
  onSelectSample: (sample: SampleReport) => void;
  sampleReports: SampleReport[];
  isAnalyzing: boolean;
  analysisStepText: string;
}

export const UploadSection: React.FC<UploadSectionProps> = ({
  onAnalyzeFile,
  onSelectSample,
  sampleReports,
  isAnalyzing,
  analysisStepText,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedExtensions = ['pdf', 'csv', 'png', 'jpg', 'jpeg'];
  const maxSizeBytes = 25 * 1024 * 1024; // 25 MB

  const validateAndSetFile = (file: File) => {
    setErrorMsg(null);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !allowedExtensions.includes(ext)) {
      setErrorMsg(`Unsupported file type (.${ext || 'unknown'}). Please upload a PDF, CSV, PNG, JPG, or JPEG file.`);
      return;
    }
    if (file.size > maxSizeBytes) {
      setErrorMsg(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the 25 MB maximum limit.`);
      return;
    }
    setSelectedFile(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setErrorMsg(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleTriggerAnalyze = () => {
    if (selectedFile) {
      onAnalyzeFile(selectedFile);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'csv') return <FileSpreadsheet className="w-8 h-8 text-emerald-600" />;
    if (['png', 'jpg', 'jpeg'].includes(ext || '')) return <ImageIcon className="w-8 h-8 text-blue-600" />;
    return <FileText className="w-8 h-8 text-teal-700" />;
  };

  return (
    <section id="upload-section" className="py-12 bg-slate-50 border-y border-slate-200">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        {/* Header Title */}
        <div className="text-center mb-8">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700 bg-teal-100/70 px-3 py-1 rounded-full border border-teal-200">
            Automated Laboratory Analysis
          </span>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-3">
            Upload Your Blood Test Report
          </h2>
          <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto leading-relaxed">
            Upload your laboratory report. We will extract the available test values, compare them with the reference ranges shown in your report, and explain any findings that may need attention.
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          {!selectedFile ? (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all ${
                dragActive
                  ? 'border-teal-600 bg-teal-50/50 scale-[1.005]'
                  : 'border-slate-300 hover:border-teal-600 hover:bg-slate-50/70'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.csv,.png,.jpg,.jpeg"
                onChange={handleFileChange}
              />

              <div className="w-16 h-16 rounded-2xl bg-teal-50 text-teal-700 flex items-center justify-center mx-auto mb-4 border border-teal-100 shadow-sm">
                <UploadCloud className="w-8 h-8" />
              </div>

              <h3 className="text-base font-bold text-slate-800">
                Drag and drop your blood report here, or <span className="text-teal-700 underline">browse files</span>
              </h3>
              <p className="text-xs text-slate-500 mt-1.5">
                Supported file types: <b>PDF</b> (digital or scanned), <b>CSV</b>, <b>PNG</b>, <b>JPG</b>, <b>JPEG</b> (Max: 25 MB)
              </p>

              <div className="mt-6 flex items-center justify-center space-x-6 text-xs text-slate-400">
                <span className="flex items-center space-x-1">
                  <ShieldCheck className="w-4 h-4 text-teal-700" />
                  <span>Private & Educational</span>
                </span>
                <span>•</span>
                <span>Automated OCR Parsing</span>
                <span>•</span>
                <span>Range Verification</span>
              </div>
            </div>
          ) : (
            /* Selected File State */
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-teal-50/60 border border-teal-200 rounded-xl">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center shadow-sm border border-teal-100">
                    {getFileIcon(selectedFile.name)}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 truncate max-w-xs sm:max-w-md">
                      {selectedFile.name}
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Ready for extraction
                    </p>
                  </div>
                </div>

                {!isAnalyzing && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-200/60 rounded-lg transition-colors"
                    >
                      Replace
                    </button>
                    <button
                      onClick={handleRemoveFile}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                      title="Remove file"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                )}
              </div>

              {/* Hidden file input for Replace */}
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.csv,.png,.jpg,.jpeg"
                onChange={handleFileChange}
              />

              {/* Progress / Analyzing State */}
              {isAnalyzing && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                    <span className="flex items-center space-x-2">
                      <RefreshCw className="w-4 h-4 text-teal-700 animate-spin" />
                      <span>{analysisStepText || 'Processing blood report...'}</span>
                    </span>
                    <span className="text-teal-700">In Progress</span>
                  </div>
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div className="bg-teal-700 h-full rounded-full animate-pulse w-3/4 transition-all duration-300" />
                  </div>
                </div>
              )}

              {/* Analyze CTA */}
              {!isAnalyzing && (
                <div className="flex justify-end">
                  <button
                    onClick={handleTriggerAnalyze}
                    className="w-full sm:w-auto px-8 py-3 bg-teal-700 hover:bg-teal-800 text-white text-sm font-bold rounded-xl shadow-md shadow-teal-700/20 hover:shadow-teal-700/30 transition-all flex items-center justify-center space-x-2"
                  >
                    <span>Analyze Report</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Validation Error Message */}
          {errorMsg && (
            <div className="mt-4 p-3.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs flex items-start space-x-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Instant Sample Reports (One-Click Testing for Evaluators) */}
        {sampleReports && sampleReports.length > 0 && (
          <div className="mt-10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-800">
                  Or Test Immediately With a Synthetic Sample Report:
                </h3>
                <p className="text-xs text-slate-500">
                  Click any sample below to run instant verification and analysis without uploading your own file.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sampleReports.map(sample => (
                <div
                  key={sample.id}
                  onClick={() => onSelectSample(sample)}
                  className="bg-white border border-slate-200 hover:border-teal-500 hover:shadow-md p-4 rounded-xl cursor-pointer transition-all group flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <span className="text-xs font-bold text-slate-900 group-hover:text-teal-700 transition-colors">
                        {sample.title}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded shrink-0 ${
                        sample.outcome_preview.includes('No Out')
                          ? 'bg-emerald-100 text-emerald-800'
                          : sample.outcome_preview.includes('Unable')
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {sample.outcome_preview}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-2">
                      {sample.description}
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-teal-700 font-semibold">
                    <span>{sample.parameters.length} Test Parameters</span>
                    <span className="group-hover:translate-x-0.5 transition-transform flex items-center space-x-1">
                      <span>Load Sample</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
