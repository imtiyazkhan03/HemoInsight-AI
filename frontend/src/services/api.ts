import { AnalysisResponse, BloodTestItem, ReportMetadata, SampleReport } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '');

async function apiFetch(path: string, options?: RequestInit): Promise<Response> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const res = await fetch(url, options);
    return res;
  } catch (primaryErr) {
    // In local development, if relative fetch fails, try direct local port 8000 fallback
    if (
      !API_BASE_URL &&
      typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ) {
      try {
        return await fetch(`http://127.0.0.1:8000${path}`, options);
      } catch {
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

async function extractErrorMessage(res: Response, fallback: string): Promise<string> {
  if (res.status === 502 || res.status === 503 || res.status === 504) {
    return `Backend server is temporarily waking up or redeploying (HTTP ${res.status}). Please wait 15–30 seconds and retry.`;
  }
  if (res.status === 413) {
    return 'The uploaded file exceeds the maximum allowed upload size. Please upload a smaller file.';
  }
  if (res.status === 404) {
    return 'The requested API endpoint was not found (HTTP 404). Please ensure the backend is running.';
  }

  try {
    const errData = await res.json();
    if (typeof errData.detail === 'string') {
      return errData.detail;
    }
    if (Array.isArray(errData.detail)) {
      return errData.detail.map((d: any) => d.msg || JSON.stringify(d)).join('; ');
    }
    if (errData.message) {
      return errData.message;
    }
  } catch {
    // If response was not JSON (e.g. gateway HTML or plain text)
    try {
      const text = await res.text();
      if (text && text.length < 150 && !text.includes('<html') && !text.includes('<!DOCTYPE')) {
        return text.trim();
      }
    } catch {
      // ignore
    }
  }

  return `${fallback} (HTTP ${res.status}: ${res.statusText || 'Server Error'})`;
}

export async function uploadAndAnalyzeReport(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await apiFetch('/api/analyze/upload', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorMsg = await extractErrorMessage(res, 'Failed to analyze report');
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
    const errorMsg = await extractErrorMessage(res, 'Failed to finalize report');
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

export async function correlateConditions(
  parameters: BloodTestItem[],
  selectedSymptoms: string[]
): Promise<import('../types').AssociatedCondition[]> {
  const res = await apiFetch('/api/analyze/correlate-conditions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parameters, selected_symptoms: selectedSymptoms }),
  });

  if (!res.ok) throw new Error('Failed to correlate conditions');
  return res.json();
}
