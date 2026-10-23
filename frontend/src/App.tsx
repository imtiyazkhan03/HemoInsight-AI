import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LandingPage } from './components/LandingPage';
import { UploadSection } from './components/UploadSection';
import { ResultsDashboard } from './components/ResultsDashboard';
import { Footer } from './components/Footer';
import { 
  AnalysisResponse, 
  SampleReport, 
  ReportMetadata, 
  BloodTestItem 
} from './types';
import { 
  checkApiHealth, 
  uploadAndAnalyzeReport, 
  verifyAndFinalizeReport, 
  downloadCsvReport, 
  downloadPdfReport, 
  getSampleReports 
} from './services/api';

export function App() {
  const [currentView, setCurrentView] = useState<'landing' | 'upload' | 'results'>('landing');
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [sampleReports, setSampleReports] = useState<SampleReport[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  
  // Loading & Step states
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysisStepText, setAnalysisStepText] = useState<string>('');
  const [isDownloadingPdf, setIsDownloadingPdf] = useState<boolean>(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Check health and fetch samples on mount with auto-retry for cloud cold starts
  useEffect(() => {
    let intervalId: any = null;

    const checkAndLoad = async () => {
      const isOnline = await checkApiHealth();
      setIsBackendOnline(isOnline);
      if (isOnline) {
        try {
          const samples = await getSampleReports();
          setSampleReports(samples);
        } catch (err) {
          console.warn('Could not fetch sample reports:', err);
        }
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      }
    };

    checkAndLoad();
    // Poll every 4 seconds until backend wakes up from cold sleep
    intervalId = setInterval(checkAndLoad, 4000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  const handleAnalyzeFile = async (file: File) => {
    setIsAnalyzing(true);
    setGlobalError(null);
    setAnalysisStepText('Extracting laboratory parameters & reading report data...');

    let stepTimer1: any = null;
    try {
      stepTimer1 = setTimeout(() => {
        setAnalysisStepText('Validating observed values against biological reference intervals...');
      }, 500);

      const result = await uploadAndAnalyzeReport(file);
      if (stepTimer1) clearTimeout(stepTimer1);

      setAnalysisStepText('Compiling plain-language medical context & doctor questions...');
      await new Promise(r => setTimeout(r, 300));

      setAnalysisResult(result);
      setCurrentView('results');
      setIsAnalyzing(false);
      setAnalysisStepText('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      if (stepTimer1) clearTimeout(stepTimer1);
      console.error(err);
      setGlobalError(err.message || 'Failed to analyze blood report.');
      setIsAnalyzing(false);
      setAnalysisStepText('');
    }
  };

  const handleSelectSample = async (sample: SampleReport) => {
    setIsAnalyzing(true);
    setGlobalError(null);
    setAnalysisStepText(`Loading sample: ${sample.title}...`);

    try {
      const meta: ReportMetadata = {
        filename: sample.filename,
        file_type: sample.filename.endsWith('.pdf') ? 'PDF' : 'CSV',
        patient_name: 'Sample Patient',
        collection_date: 'Current',
        lab_name: 'Apex Diagnostic Laboratories',
      };

      const result = await verifyAndFinalizeReport(meta, sample.parameters);

      setAnalysisResult(result);
      setCurrentView('results');
      setIsAnalyzing(false);
      setAnalysisStepText('');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      console.error(err);
      setGlobalError(err.message || 'Failed to analyze sample report.');
      setIsAnalyzing(false);
      setAnalysisStepText('');
    }
  };

  const handleVerifyAndFinalize = async (metadata: ReportMetadata, verifiedParams: BloodTestItem[]) => {
    setIsAnalyzing(true);
    try {
      const updated = await verifyAndFinalizeReport(metadata, verifiedParams);
      setAnalysisResult(updated);
    } catch (err: any) {
      console.error(err);
      alert('Error updating verified report: ' + (err.message || 'Unknown error'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadCsv = async () => {
    if (!analysisResult) return;
    try {
      await downloadCsvReport(analysisResult);
    } catch (err: any) {
      alert('Could not download CSV: ' + err.message);
    }
  };

  const handleDownloadPdf = async () => {
    if (!analysisResult) return;
    setIsDownloadingPdf(true);
    try {
      await downloadPdfReport(analysisResult);
    } catch (err: any) {
      alert('Could not download PDF summary: ' + err.message);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setCurrentView('upload');
    setGlobalError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigate = (section: 'landing' | 'upload' | 'samples' | 'how-it-works') => {
    if (section === 'landing') {
      setCurrentView('landing');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (section === 'upload') {
      setCurrentView('upload');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (section === 'samples') {
      if (currentView === 'results') {
        setCurrentView('landing');
      }
      setTimeout(() => {
        const el = document.getElementById('sample-reports');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } else if (section === 'how-it-works') {
      if (currentView === 'results') {
        setCurrentView('landing');
      }
      setTimeout(() => {
        const el = document.getElementById('how-it-works');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      {/* Top Navigation */}
      <Navbar onNavigate={handleNavigate} isBackendOnline={isBackendOnline} />

      {/* Global Error Banner */}
      {globalError && (
        <div className="bg-rose-50 border-b border-rose-200 px-4 py-3 text-center text-xs font-semibold text-rose-800">
          {globalError}
        </div>
      )}

      {/* Main Content Sections */}
      <main className="flex-1">
        {currentView === 'landing' && (
          <>
            <LandingPage
              onStartAnalysis={() => {
                setCurrentView('upload');
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              onSelectSample={handleSelectSample}
              sampleReports={sampleReports}
            />

            {/* Direct upload dropzone on landing page as well */}
            <UploadSection
              onAnalyzeFile={handleAnalyzeFile}
              onSelectSample={handleSelectSample}
              sampleReports={sampleReports}
              isAnalyzing={isAnalyzing}
              analysisStepText={analysisStepText}
            />
          </>
        )}

        {currentView === 'upload' && (
          <div className="pt-8">
            <UploadSection
              onAnalyzeFile={handleAnalyzeFile}
              onSelectSample={handleSelectSample}
              sampleReports={sampleReports}
              isAnalyzing={isAnalyzing}
              analysisStepText={analysisStepText}
            />
          </div>
        )}

        {currentView === 'results' && analysisResult && (
          <ResultsDashboard
            analysis={analysisResult}
            onReset={handleReset}
            onDownloadCsv={handleDownloadCsv}
            onDownloadPdf={handleDownloadPdf}
            onVerifyAndFinalize={handleVerifyAndFinalize}
            isDownloadingPdf={isDownloadingPdf}
          />
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
