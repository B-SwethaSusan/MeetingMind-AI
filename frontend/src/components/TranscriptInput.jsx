import FileUpload from './FileUpload'

export default function TranscriptInput({ transcript, onChange, onAnalyze, loading }) {
  return (
    <section className="input-panel card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">INPUT</p>
          <h2>Meeting transcript</h2>
        </div>
        <FileUpload onFile={onChange} />
      </div>
      <textarea
        value={transcript}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Paste your meeting notes or transcript here…"
        aria-label="Meeting transcript"
      />
      <div className="input-footer">
        <span>{transcript.trim().split(/\s+/).filter(Boolean).length} words</span>
        <button type="button" onClick={onAnalyze} disabled={loading || !transcript.trim()}>
          {loading ? 'Analyzing…' : 'Analyze meeting'}
        </button>
      </div>
    </section>
  )
}
