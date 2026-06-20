import re

FILLER_WORDS = [
    "um", "umm", "uh", "uhh", "like", "you know", "basically",
    "actually", "literally", "kind of", "sort of", "i mean",
    "so yeah", "right", "well", "kinda", "idk", "Idk", "obv",
    "just", "seriously", "totally", "clearly", "honestly", "really"
    "sorry", "Sorry", "cuz"
]

def detect_fillers(text):
  text_lower = text.lower()
  found = {}

  for word in FILLER_WORDS:
    # \b means whole word match, not part of another word
    pattern = r'\b' + re.escape(word) + r'\b'
    count = len(re.findall(pattern, text_lower))
    if count > 0:
      found[word] = count

  total = sum(found.values())
  return {
    "total_fillers": total,
    "breakdown": found
  }