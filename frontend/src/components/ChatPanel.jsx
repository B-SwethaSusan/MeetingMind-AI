import { useState } from 'react'
import { askTranscriptQuestion } from '../services/api'

export default function ChatPanel({ enabled }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [evidence, setEvidence] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function askQuestion(event) {
    event.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    try {
      const result = await askTranscriptQuestion(question.trim())
      setAnswer(result.answer)
      setEvidence(result.evidence ?? '')
    } catch (err) {
      setAnswer('')
      setEvidence('')
      setError(err instanceof Error ? err.message : 'Unable to answer the question.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="chat-panel">
      <p className="eyebrow">TRANSCRIPT Q&A</p>
      <h3>Ask a follow-up</h3>
      <form onSubmit={askQuestion}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Who owns the report?"
          disabled={!enabled || loading}
        />
        <button type="submit" disabled={!enabled || loading || !question.trim()}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>
      {!enabled && <p className="muted">Analyze a transcript first to enable Q&A.</p>}
      {answer && <p className="chat-answer">{answer}</p>}
      {evidence && <p className="chat-evidence">Evidence: “{evidence}”</p>}
      {error && <p className="chat-error">{error}</p>}
    </section>
  )
}
