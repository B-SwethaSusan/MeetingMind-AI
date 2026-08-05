export default function FileUpload({ onFile }) {
  function readFile(event) {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = () => onFile(String(reader.result ?? ''))
    reader.readAsText(file)
  }

  return (
    <label className="file-upload">
      <input type="file" accept=".txt,text/plain" onChange={readFile} />
      <span>Upload a .txt transcript</span>
      <small>It stays in your browser until you analyze it.</small>
    </label>
  )
}
