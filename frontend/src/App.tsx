import React, { useState } from 'react'

interface Ratios {
  [k: string]: number
}

interface UploadResponse {
  ticker?: string
  period?: string
  ratios: Ratios
  red_flags: { flags: string[] }
}

interface AnalyzeResponse {
  llm: { direction: string; risk: string; explanation: string }
  baseline: { direction: string; score: number }
  agreement: boolean
  ratios: Ratios
  red_flags: { flags: string[] }
}

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [upload, setUpload] = useState<UploadResponse | null>(null)
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onUpload = async () => {
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch('/api/upload', { method: 'POST', body: fd })
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as UploadResponse
      setUpload(data)
      setAnalysis(null)
    } catch (e: any) {
      setError(e.message ?? 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  const onAnalyze = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await fetch('/api/analyze', { method: 'POST' })
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as AnalyzeResponse
      setAnalysis(data)
    } catch (e: any) {
      setError(e.message ?? 'Analyze failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">LLM Financial Statement Copilot</h1>

      <div className="mb-4 p-4 border rounded">
        <input type="file" accept=".csv,.xlsx,.xls" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button className="ml-3 px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50" disabled={!file || busy} onClick={onUpload}>
          {busy ? 'Uploading…' : 'Upload & Parse'}
        </button>
      </div>

      {error && <div className="mb-3 text-red-700">{error}</div>}

      {upload && (
        <div className="mb-6">
          <h2 className="font-medium mb-2">Parsed Ratios {upload.ticker ? `for ${upload.ticker}` : ''}</h2>
          <table className="w-full text-sm border">
            <tbody>
              {Object.entries(upload.ratios).map(([k, v]) => (
                <tr key={k} className="even:bg-gray-50">
                  <td className="p-2 border w-1/2">{k}</td>
                  <td className="p-2 border">{typeof v === 'number' ? v.toFixed(4) : String(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {upload.red_flags.flags.length > 0 && (
            <div className="mt-2 text-amber-700">Red flags: {upload.red_flags.flags.join(', ')}</div>
          )}
        </div>
      )}

      <div className="mb-4">
        <button className="px-3 py-1 bg-emerald-600 text-white rounded disabled:opacity-50" disabled={!upload || busy} onClick={onAnalyze}>
          {busy ? 'Analyzing…' : 'Analyze (LLM + Baseline)'}
        </button>
      </div>

      {analysis && (
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 border rounded">
            <h3 className="font-medium mb-1">LLM</h3>
            <div>Direction: <b>{analysis.llm.direction.toUpperCase()}</b></div>
            <div>Risk: <b>{analysis.llm.risk.toUpperCase()}</b></div>
            <p className="mt-2 text-sm text-gray-700">{analysis.llm.explanation}</p>
          </div>
          <div className="p-4 border rounded">
            <h3 className="font-medium mb-1">Baseline</h3>
            <div>Direction: <b>{analysis.baseline.direction.toUpperCase()}</b></div>
            <div>Score (P(up)): {analysis.baseline.score.toFixed(3)}</div>
            <div className="mt-2">Agreement: <b>{analysis.agreement ? 'Yes' : 'No'}</b></div>
          </div>
          <div className="md:col-span-2 p-3 text-xs text-gray-600 border rounded">
            Disclaimer: Experimental tool for demonstration; not investment advice.
          </div>
        </div>
      )}
    </div>
  )
}
