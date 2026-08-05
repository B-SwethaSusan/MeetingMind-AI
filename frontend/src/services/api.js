const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8001'

export async function analyzeTranscript(transcript) {
  const response = await fetch(`${API_URL}/meeting/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript }),
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Request failed (${response.status})`)
  }

  return response.json()
}

export async function askTranscriptQuestion(question) {
  const response = await fetch(`${API_URL}/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Question failed (${response.status})`)
  }

  return response.json()
}
