export default function Header() {
  return (
    <header className="site-header">
      <div className="mark" aria-hidden="true">M</div>
      <div>
        <p className="eyebrow">LOCAL AI WORKSPACE</p>
        <h1>Meeting Lens</h1>
      </div>
      <span className="local-status"><i /> Ollama local</span>
    </header>
  )
}
