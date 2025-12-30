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

interface ComparisonMetrics {
  metric_name: string
  current_value: number
  previous_value?: number
  change_percent?: number
}

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [upload, setUpload] = useState<UploadResponse | null>(null)
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [comparison, setComparison] = useState<ComparisonMetrics[] | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [darkMode, setDarkMode] = useState(false)

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
      // Fetch comparison
      try {
        const compRes = await fetch('/api/compare')
        if (compRes.ok) {
          const compData = await compRes.json()
          setComparison(compData)
        }
      } catch (e) {
        // Comparison optional
      }
    } catch (e: any) {
      setError(e.message ?? 'Analyze failed')
    } finally {
      setBusy(false)
    }
  }

  const onExport = async (format: 'csv' | 'json') => {
    try {
      const res = await fetch(`/api/export/${format}`)
      if (!res.ok) throw new Error('Export failed')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `financial_analysis.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e: any) {
      setError(e.message ?? 'Export failed')
    }
  }

  return (
    <div className={`${darkMode ? 'dark bg-gray-900 text-white' : 'bg-white text-gray-900'} min-h-screen transition-colors`}>
      <div className="min-h-screen p-6 max-w-6xl mx-auto">
        {/* Header with Dark Mode Toggle */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">💰 Financial Analysis Copilot</h1>
            <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>LLM-powered financial statement analysis</p>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            {darkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>

        {/* Upload Section */}
        <div className={`mb-8 p-6 border-2 rounded-lg ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-blue-200 bg-blue-50'}`}>
          <h2 className="text-lg font-semibold mb-4">📁 Upload Financial Data</h2>
          <div className="flex gap-3 items-center">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className={`px-3 py-2 rounded ${darkMode ? 'bg-gray-700 border-gray-600' : 'border'}`}
            />
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              disabled={!file || busy}
              onClick={onUpload}
            >
              {busy ? '⏳ Uploading…' : '📤 Upload & Parse'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            ⚠️ {error}
          </div>
        )}

        {/* Ratios Display */}
        {upload && (
          <div className={`mb-8 p-6 rounded-lg border-2 ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">📊 Financial Ratios {upload.ticker ? `(${upload.ticker})` : ''}</h2>
              {analysis && (
                <div className="flex gap-2">
                  <button
                    onClick={() => onExport('csv')}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                  >
                    📥 CSV
                  </button>
                  <button
                    onClick={() => onExport('json')}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                  >
                    📥 JSON
                  </button>
                </div>
              )}
            </div>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              {Object.entries(upload.ratios).map(([k, v]) => (
                <div key={k} className={`p-3 rounded ${darkMode ? 'bg-gray-700' : 'bg-white border'}`}>
                  <div className="text-xs font-medium opacity-75">{k.replace(/_/g, ' ')}</div>
                  <div className="text-lg font-bold">{typeof v === 'number' ? v.toFixed(3) : String(v)}</div>
                </div>
              ))}
            </div>
            {upload.red_flags.flags.length > 0 && (
              <div className={`p-3 rounded ${darkMode ? 'bg-amber-900/30 border border-amber-700' : 'bg-amber-50 border border-amber-200'}`}>
                <div className="font-semibold text-amber-700 dark:text-amber-200">⚠️ Red Flags Detected:</div>
                <ul className="list-disc pl-5 text-sm mt-2">
                  {upload.red_flags.flags.map((flag) => (
                    <li key={flag} className="opacity-90">
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Analysis Button */}
        <div className="mb-6">
          <button
            className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            disabled={!upload || busy}
            onClick={onAnalyze}
          >
            {busy ? '⏳ Analyzing…' : '🔍 Analyze (LLM + Baseline)'}
          </button>
        </div>

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* LLM vs Baseline Comparison */}
            <div className="grid md:grid-cols-2 gap-6">
              <div
                className={`p-6 rounded-lg border-2 transition-all ${
                  analysis.agreement
                    ? darkMode
                      ? 'border-green-700 bg-green-900/20'
                      : 'border-green-300 bg-green-50'
                    : darkMode
                    ? 'border-orange-700 bg-orange-900/20'
                    : 'border-orange-300 bg-orange-50'
                }`}
              >
                <h3 className="font-bold text-lg mb-3">🤖 LLM Analysis</h3>
                <div className="space-y-2">
                  <div>
                    <span className="opacity-75">Direction:</span>
                    <span className="ml-2 font-bold text-lg">
                      {analysis.llm.direction === 'up' && '📈'}
                      {analysis.llm.direction === 'down' && '📉'}
                      {analysis.llm.direction === 'flat' && '➡️'} {analysis.llm.direction.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <span className="opacity-75">Risk Level:</span>
                    <span className={`ml-2 font-bold uppercase ${
                      analysis.llm.risk === 'high' ? 'text-red-600 dark:text-red-400' :
                      analysis.llm.risk === 'medium' ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-green-600 dark:text-green-400'
                    }`}>
                      {analysis.llm.risk}
                    </span>
                  </div>
                  <p className="text-sm mt-4 italic opacity-90">&quot;{analysis.llm.explanation}&quot;</p>
                </div>
              </div>

              <div className={`p-6 rounded-lg border-2 ${darkMode ? 'border-indigo-700 bg-indigo-900/20' : 'border-indigo-300 bg-indigo-50'}`}>
                <h3 className="font-bold text-lg mb-3">📈 Baseline Model</h3>
                <div className="space-y-2">
                  <div>
                    <span className="opacity-75">Direction:</span>
                    <span className="ml-2 font-bold text-lg">
                      {analysis.baseline.direction === 'up' && '📈'}
                      {analysis.baseline.direction === 'down' && '📉'}
                      {analysis.baseline.direction === 'flat' && '➡️'} {analysis.baseline.direction.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <span className="opacity-75">Confidence (P(up)):</span>
                    <div className="mt-2 w-full bg-gray-300 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min(100, analysis.baseline.score * 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">{(analysis.baseline.score * 100).toFixed(1)}%</span>
                  </div>
                  <div className={`mt-4 p-3 rounded font-semibold ${analysis.agreement ? 'bg-green-200 dark:bg-green-900/40' : 'bg-orange-200 dark:bg-orange-900/40'}`}>
                    {analysis.agreement ? '✅ Models Agree' : '❌ Models Disagree'}
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics Comparison */}
            {comparison && comparison.length > 0 && (
              <div className={`p-6 rounded-lg border-2 ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
                <h3 className="font-bold text-lg mb-4">📊 Metrics Comparison vs Previous</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {comparison.map((metric) => (
                    <div key={metric.metric_name} className={`p-4 rounded ${darkMode ? 'bg-gray-700' : 'bg-white border'}`}>
                      <div className="font-semibold text-sm opacity-75">{metric.metric_name.replace(/_/g, ' ')}</div>
                      <div className="text-lg font-bold">{metric.current_value.toFixed(3)}</div>
                      {metric.change_percent !== undefined && (
                        <div className={`text-sm font-semibold mt-1 ${
                          (metric.change_percent ?? 0) > 0 ? 'text-green-600 dark:text-green-400' : 
                          (metric.change_percent ?? 0) < 0 ? 'text-red-600 dark:text-red-400' : ''
                        }`}>
                          {(metric.change_percent ?? 0) > 0 ? '↑' : (metric.change_percent ?? 0) < 0 ? '↓' : '→'} {Math.abs(metric.change_percent ?? 0).toFixed(1)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div className={`p-4 rounded-lg text-xs border ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-300 bg-gray-100'} opacity-75`}>
              ⚠️ <strong>Disclaimer:</strong> This is an experimental tool for demonstration purposes only. Not intended as investment advice.
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
