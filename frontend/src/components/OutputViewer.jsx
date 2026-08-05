import ChatPanel from './ChatPanel'

export default function OutputViewer({ analysis, error }) {
  if (error) {
    return <section className="result-panel card error"><h2>Could not analyze</h2><p>{error}</p><ChatPanel enabled={false} /></section>
  }

  if (!analysis) {
    return <section className="result-panel card empty"><p className="eyebrow">OUTPUT</p><h2>Your JSON analysis will appear here.</h2><p>Analyze a transcript to receive structured meeting data.</p><ChatPanel enabled={false} /></section>
  }

  return (
    <section className="result-panel card">
      <p className="eyebrow">ANALYSIS JSON</p>
      <pre className="json-output">{JSON.stringify(analysis, null, 2)}</pre>
      <ChatPanel enabled />
    </section>
  )
}
