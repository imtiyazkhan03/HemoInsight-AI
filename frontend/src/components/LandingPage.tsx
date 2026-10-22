import React from 'react';
import { 
  ArrowRight, ShieldCheck, CheckCircle2, Cpu, 
  Sparkles, FileText 
} from 'lucide-react';
import { SampleReport } from '../types';

interface LandingPageProps {
  onStartAnalysis: () => void;
  onSelectSample: (sample: SampleReport) => void;
  sampleReports: SampleReport[];
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartAnalysis,
  onSelectSample,
  sampleReports,
}) => {
  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 overflow-hidden bg-gradient-to-b from-white via-teal-50/20 to-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Column: Hero Text */}
            <div className="lg:col-span-7 space-y-6 text-left">
              <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-teal-100 text-teal-900 text-xs font-semibold border border-teal-200">
                <Sparkles className="w-4 h-4 text-teal-700" />
                <span>Smart Blood Report Analyzer • Academic Experiment 9</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
                Your Blood Report, <br className="hidden sm:inline" />
                <span className="text-teal-700 bg-clip-text">Explained in Simple Language.</span>
              </h1>

              <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl font-normal">
                Upload your blood test report to understand your laboratory results, identify values outside their reference ranges, and discover what they may mean.
              </p>

              {/* CTAs */}
              <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                <button
                  onClick={onStartAnalysis}
                  className="px-7 py-3.5 bg-teal-700 hover:bg-teal-800 text-white font-bold rounded-xl shadow-lg shadow-teal-700/25 hover:shadow-teal-700/35 transition-all flex items-center justify-center space-x-2.5 text-base"
                >
                  <span>Analyze My Blood Report</span>
                  <ArrowRight className="w-5 h-5" />
                </button>

                <a
                  href="#how-it-works"
                  className="px-6 py-3.5 bg-white hover:bg-slate-100 text-slate-700 font-semibold rounded-xl border border-slate-300 shadow-sm transition-colors text-center text-base"
                >
                  How It Works
                </a>
              </div>

              {/* Trust Badges */}
              <div className="pt-6 border-t border-slate-200/80 flex flex-wrap items-center gap-6 text-xs text-slate-500">
                <span className="flex items-center space-x-1.5 font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>PyMuPDF & Tesseract Extraction</span>
                </span>
                <span className="flex items-center space-x-1.5 font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Lab Range Verification</span>
                </span>
                <span className="flex items-center space-x-1.5 font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Plain-Language AI Insights</span>
                </span>
              </div>
            </div>

            {/* Right Column: Laboratory Transformation Illustration */}
            <div className="lg:col-span-5 relative">
              <div className="relative mx-auto max-w-md bg-white rounded-3xl shadow-xl border border-slate-200/90 p-5 space-y-4">
                {/* Header mock */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-rose-400" />
                    <div className="w-3 h-3 rounded-full bg-amber-400" />
                    <div className="w-3 h-3 rounded-full bg-emerald-400" />
                    <span className="text-[11px] font-semibold text-slate-400 ml-2">HemoInsight AI Transformation Engine</span>
                  </div>
                  <span className="text-[10px] bg-teal-100 text-teal-800 font-bold px-2 py-0.5 rounded-full">Live Demo</span>
                </div>

                {/* Raw Report Preview card */}
                <div className="bg-slate-50 rounded-xl p-3 border border-slate-200 text-left">
                  <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                    <span className="font-semibold flex items-center space-x-1">
                      <FileText className="w-3.5 h-3.5 text-slate-400" />
                      <span>Original Paper / PDF Report</span>
                    </span>
                    <span className="font-mono text-[10px]">Extracted</span>
                  </div>
                  <div className="font-mono text-[11px] text-slate-600 bg-white p-2 rounded border border-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span>Hemoglobin ........... 10.4 g/dL</span>
                      <span className="text-blue-700 font-bold">(12.0 - 16.0) LOW</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Platelets ............ 128 x10^3</span>
                      <span className="text-blue-700 font-bold">(150 - 450) LOW</span>
                    </div>
                  </div>
                </div>

                {/* Transformation Arrow */}
                <div className="flex items-center justify-center my-1">
                  <div className="w-8 h-8 rounded-full bg-teal-700 text-white flex items-center justify-center shadow-md shadow-teal-700/20">
                    <Cpu className="w-4 h-4 animate-pulse" />
                  </div>
                </div>

                {/* Transformed Result Card Mock */}
                <div className="bg-teal-50/80 rounded-xl p-3.5 border border-teal-200 text-left space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-teal-900">Easy-to-Understand AI Dashboard</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 bg-amber-100 text-amber-900 rounded-md">
                      2 Results Outside Range
                    </span>
                  </div>
                  <div className="bg-white rounded-lg p-2.5 border border-teal-100 space-y-1.5 shadow-sm text-xs">
                    <div className="flex items-center justify-between font-bold text-slate-800">
                      <span>Hemoglobin: 10.4 g/dL</span>
                      <span className="text-blue-600 text-[11px]">Below Reference</span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden flex">
                      <div className="w-1/4 bg-blue-500" />
                      <div className="w-1/2 bg-emerald-400" />
                      <div className="w-1/4 bg-amber-400" />
                    </div>
                    <p className="text-[11px] text-slate-600 leading-tight">
                      "Lower than the laboratory reference range. Can be associated with iron deficiency or temporary fatigue."
                    </p>
                  </div>
                </div>

                <div className="text-[10px] text-center text-slate-400">
                  Instant comparison against supplied laboratory biological intervals
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three Step Workflow Explanation */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-700 bg-teal-100/70 px-3 py-1 rounded-full border border-teal-200">
            Intuitive 3-Step Process
          </span>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mt-3">
            How VitalScan AI Works
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            Translating complex clinical lab sheets into actionable, clear health literacy in seconds.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Step 1 */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm hover:border-teal-400 transition-all group text-left">
            <div className="w-12 h-12 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center font-extrabold text-lg mb-5 group-hover:bg-teal-700 group-hover:text-white transition-colors">
              1
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Upload Your Report</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Upload your blood test report in PDF, PNG, JPG, JPEG, or CSV format. Our engine reads embedded text with PyMuPDF or runs preprocessed OCR on scanned documents.
            </p>
          </div>

          {/* Step 2 */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm hover:border-teal-400 transition-all group text-left">
            <div className="w-12 h-12 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center font-extrabold text-lg mb-5 group-hover:bg-teal-700 group-hover:text-white transition-colors">
              2
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Analyze & Validate</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              The backend extracts test names, numerical values, units, and laboratory reference ranges. Uncertain readings are flagged so you can verify or edit them prior to classification.
            </p>
          </div>

          {/* Step 3 */}
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm hover:border-teal-400 transition-all group text-left">
            <div className="w-12 h-12 rounded-xl bg-teal-100 text-teal-800 flex items-center justify-center font-extrabold text-lg mb-5 group-hover:bg-teal-700 group-hover:text-white transition-colors">
              3
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Understand Your Findings</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Discover which parameters are within range, low, or high. Read plain-language medical context and questions for your doctor, and download a structured PDF report.
            </p>
          </div>
        </div>
      </section>

      {/* Preloaded Sample Reports Section */}
      {sampleReports && sampleReports.length > 0 && (
        <section id="sample-reports" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-teal-900 to-slate-900 rounded-3xl p-8 sm:p-12 text-white shadow-xl text-left">
            <div className="max-w-2xl mb-8">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-300 bg-teal-800/80 px-3 py-1 rounded-full border border-teal-700">
                Evaluation Test Suite
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight mt-3">
                Try HemoInsight AI With Preconfigured Sample Reports
              </h2>
              <p className="text-sm text-slate-300 mt-2">
                Evaluate different clinical scenarios instantly with one click:
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {sampleReports.map(sample => (
                <div
                  key={sample.id}
                  onClick={() => onSelectSample(sample)}
                  className="bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-teal-400 p-5 rounded-2xl cursor-pointer transition-all flex flex-col justify-between group"
                >
                  <div>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full inline-block mb-2 ${
                      sample.outcome_preview.includes('No Out')
                        ? 'bg-emerald-900/90 text-emerald-200 border border-emerald-700'
                        : sample.outcome_preview.includes('Unable')
                        ? 'bg-rose-900/90 text-rose-200 border border-rose-700'
                        : 'bg-amber-900/90 text-amber-200 border border-amber-700'
                    }`}>
                      {sample.outcome_preview}
                    </span>
                    <h4 className="text-sm font-bold text-white group-hover:text-teal-300 transition-colors">
                      {sample.title}
                    </h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      {sample.description}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-700/60 flex items-center justify-between text-xs text-teal-400 font-semibold">
                    <span>{sample.parameters.length} Tests</span>
                    <span className="group-hover:translate-x-1 transition-transform flex items-center space-x-1">
                      <span>Analyze</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Privacy and Medical Disclaimer Card */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 text-left space-y-3 shadow-sm">
          <div className="flex items-center space-x-2 text-teal-800 font-bold text-sm">
            <ShieldCheck className="w-5 h-5 text-teal-700" />
            <span>Academic Integrity & Patient Privacy Notice</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            HemoInsight AI is built strictly for educational report comprehension. Uploaded documents are parsed in-memory and are never stored or sold to third parties. This software does not provide medical diagnosis or replace consultation with a licensed physician.
          </p>
        </div>
      </section>
    </div>
  );
};
