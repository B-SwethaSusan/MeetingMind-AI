import { useState } from 'react'
import Header from './components/Header'
import TranscriptInput from './components/TranscriptInput'
import OutputViewer from './components/OutputViewer'
import { analyzeTranscript } from './services/api'

export default function App() {
  const [transcript, setTranscript] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleAnalyze() {
    setLoading(true)
    setError('')
    try {
      setAnalysis(await analyzeTranscript(transcript))
    } catch (err) {
      setAnalysis(null)
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page-shell">
      <Header />
      <section className="intro"><p className="eyebrow">TURN CONVERSATION INTO CLARITY</p><h2>Find the decisions<br />hidden in your meetings.</h2><p>Paste a transcript, run it through your local model, and get an actionable brief.</p></section>
      <div className="workspace">
        <TranscriptInput transcript={transcript} onChange={setTranscript} onAnalyze={handleAnalyze} loading={loading} />
        <OutputViewer analysis={analysis} error={error} />
      </div>
    </main>
  )
}
