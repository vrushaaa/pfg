# from sentence_transformers import SentenceTransformer

SCORE_MEANINGS = {
    "accuracy": {
        "9-10": "Excellent, no obvious mistakes",
        "7-8": "Good, few pronunciation mistakes",
        "5-6": "Understandable, many mistakes and accent",
        "3-4": "Poor, serious mistakes",
        "0-2": "Extremely poor, barely recognizable"
    },
    "completeness": {
        "1.0": "All words pronounced",
        "0.8-0.9": "Most words pronounced",
        "0.0-0.7": "Significant omissions"
    },
    "fluency": {
        "8-10": "Fluent, no noticeable pauses",
        "6-7": "Generally fluent, few pauses",
        "4-5": "A little influent, many pauses",
        "0-3": "Very influent, lots of pauses"
    },
    "prosodic": {
        "9-10": "Correct intonation, native-like rhythm",
        "7-8": "Nearly correct intonation, little stammering",
        "5-6": "Unstable speed, poor rhythm",
        "3-4": "Too fast/slow, no rhythm",
        "0-2": "Poor intonation, lots of pauses"
    }
}

class RAGSetup:
    def __init__(self):
        self.meanings = SCORE_MEANINGS
    
    def _get_range(self, param, score):
        ranges = self.meanings[param]
        score = float(score)
        for range_str, desc in ranges.items():
            if "-" in range_str:
                low, high = map(float, range_str.split("-"))
                if low <= score <= high + 0.999:
                    return desc
            else:
                if abs(float(range_str) - score) < 0.001:
                    return desc
        return "Score out of range"
    
    def retrieve(self, query):
        param, score = query.split(": ")
        return self._get_range(param, score)