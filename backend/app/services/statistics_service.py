import re
from collections import defaultdict
from typing import List, Dict


class StatisticsService:

    # --- Same-line speaker header ---
    #   "Alice: hi"
    #   "Alice - hi"
    #   "Alice (Manager): hi"
    #   "[09:00] Alice: hi"
    #   "[09:00] Alice (Manager): hi"
    # Capture group 1 = speaker name, group 2 = spoken text.
    SPEAKER_PATTERN = re.compile(
        r"""^\s*
            (?:[\[\(]\s*[\d:.\-\s]+\s*[\]\)]\s*)?       # optional [time] or (time) prefix
            ([A-Za-z][A-Za-z .'\-]{0,40}?)               # speaker name (lazy)
            (?:\s*\([A-Za-z][A-Za-z &/.'\-]{0,40}\))?     # optional (Role) suffix
            \s*(?::|-|–|—)\s*                             # separator
            (.+)$                                          # spoken text
        """,
        re.VERBOSE
    )

    # --- Standalone speaker header (next line is the speech) ---
    #   "Alice:"
    #   "Alice (Manager):"
    #   "Alice -"
    STANDALONE_SPEAKER_PATTERN = re.compile(
        r"""^\s*
            (?:[\[\(]\s*[\d:.\-\s]+\s*[\]\)]\s*)?       # optional [time] or (time) prefix
            ([A-Za-z][A-Za-z .'\-]{0,40}?)               # speaker name (lazy)
            (?:\s*\([A-Za-z][A-Za-z &/.'\-]{0,40}\))?     # optional (Role) suffix
            \s*(?::|-|–|—)\s*                             # trailing separator
            $
        """,
        re.VERBOSE
    )

    INVALID_SPEAKERS = {
        "meeting date",
        "department",
        "participants",
        "attendees",
        "agenda",
        "time",
        "location",
        "meeting concluded",
        "meeting ended",
        "summary",
        "notes",
        "date",
        "topic",
        "subject",
        "minute",
        "minutes",
        "duration",
    }

    def _looks_like_a_name(self, speaker: str) -> bool:
        """
        A reasonable person name:
        - 1 to 3 whitespace-separated tokens
        - each token starts with a letter and contains only letters,
          dots, apostrophes, or hyphens
        """
        tokens = speaker.split()
        if not tokens or len(tokens) > 3:
            return False
        for t in tokens:
            if not re.match(r"^[A-Za-z][A-Za-z.'\-]*$", t):
                return False
        return True

    def _clean_speaker(self, raw: str) -> str:
        speaker = raw.strip().rstrip(" .")
        if speaker.lower() in self.INVALID_SPEAKERS:
            return ""
        if not self._looks_like_a_name(speaker):
            return ""
        return speaker

    def _count_words(self, text: str) -> int:
        return len(re.findall(r"\b[\w'-]+\b", text))

    def calculate_speaker_statistics(self, transcript: str) -> List[Dict]:

        speaker_words: Dict[str, int] = defaultdict(int)

        lines = transcript.splitlines()
        i = 0
        n = len(lines)

        while i < n:

            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # ---- Case 1: same-line speaker ("Alice: hi") ----
            same_line = self.SPEAKER_PATTERN.match(line)
            if same_line:
                speaker = self._clean_speaker(same_line.group(1))
                speech = same_line.group(2).strip()
                if speaker:
                    words = self._count_words(speech)
                    if words:
                        speaker_words[speaker] += words
                i += 1
                continue

            # ---- Case 2: standalone speaker header ("Alice:") ----
            standalone = self.STANDALONE_SPEAKER_PATTERN.match(line)
            if standalone:
                speaker = self._clean_speaker(standalone.group(1))
                if speaker:
                    # Collect the speech: all subsequent non-empty lines until
                    # the next standalone header, the end of the transcript,
                    # or any line that begins with a new speaker header.
                    j = i + 1
                    speech_lines: List[str] = []
                    while j < n:
                        nxt = lines[j].strip()
                        if not nxt:
                            j += 1
                            continue
                        if self.STANDALONE_SPEAKER_PATTERN.match(nxt):
                            break
                        if self.SPEAKER_PATTERN.match(nxt):
                            break
                        speech_lines.append(nxt)
                        j += 1
                    speech = " ".join(speech_lines).strip()
                    words = self._count_words(speech)
                    if words:
                        speaker_words[speaker] += words
                    i = j
                    continue

            # Not a speaker line at all — skip it.
            i += 1

        if not speaker_words:
            return []

        total_words = sum(speaker_words.values())

        # Round to nearest int, then adjust so the sum is exactly 100.
        # The largest speaker absorbs the rounding remainder.
        speakers_sorted = sorted(
            speaker_words.items(),
            key=lambda kv: kv[1],
            reverse=True
        )

        percentages: List[tuple] = []
        running_total = 0
        last_index = len(speakers_sorted) - 1

        for i_idx, (speaker, _count) in enumerate(speakers_sorted):
            if i_idx == last_index:
                percent = 100 - running_total
            else:
                percent = round((_count / total_words) * 100)
                running_total += percent
            percentages.append((speaker, percent))

        return [
            {"name": speaker, "percentage": percent}
            for speaker, percent in percentages
        ]
