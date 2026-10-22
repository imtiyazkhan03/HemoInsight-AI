import { AnalysisResponse, BloodTestItem, ReportMetadata, SampleReport } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const res = await fetch(url, options);
    return res;
  } catch (primaryErr) {
    // If relative fetch fails, try direct 127.0.0.1:8000 fallback
    if (!API_BASE_URL) {
      try {
        return await fetch(`http://127.0.0.1:8000${path}`, options);
      } catch {
        // Also try localhost:8000
        try {
          return await fetch(`http://localhost:8000${path}`, options);
        } catch {
          throw primaryErr;
        }
      }
    }
    throw primaryErr;
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await apiFetch('/api/health');
    return res.ok;
  } catch {
    return false;
  }
}

export async function uploadAndAnalyzeReport(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await apiFetch('/api/analyze/upload', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let errorMsg = 'Failed to analyze report';
    try {
      const errData = await res.json();
      errorMsg = errData.detail || errorMsg;
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function verifyAndFinalizeReport(
  metadata: ReportMetadata,
  parameters: BloodTestItem[]
): Promise<AnalysisResponse> {
  const res = await apiFetch('/api/analyze/verify-and-finalize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metadata, parameters }),
  });

  if (!res.ok) {
    let errorMsg = 'Failed to finalize report';
    try {
      const errData = await res.json();
      errorMsg = errData.detail || errorMsg;
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export async function downloadCsvReport(analysis: AnalysisResponse): Promise<void> {
  const res = await apiFetch('/api/export/csv', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(analysis),
  });

  if (!res.ok) throw new Error('Could not download CSV export');

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `VitalScan_${analysis.metadata.filename.replace(/\.[^/.]+$/, '')}.csv`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadPdfReport(analysis: AnalysisResponse): Promise<void> {
  const res = await apiFetch('/api/export/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(analysis),
  });

  if (!res.ok) throw new Error('Could not download PDF summary');

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `VitalScan_${analysis.metadata.filename.replace(/\.[^/.]+$/, '')}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function getSampleReports(): Promise<SampleReport[]> {
  const res = await apiFetch('/api/samples');
  if (!res.ok) throw new Error('Failed to load sample reports');
  return res.json();
}
