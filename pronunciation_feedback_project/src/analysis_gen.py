from src.rag_setup import RAGSetup

class AnalysisGenerator:
    def __init__(self):
        self.rag = RAGSetup()
    
    def generate_analysis(self, utt_id, text, scores):
        """
        Generate analysis feedback for a given utterance.
        
        Args:
            utt_id (str): Utterance ID.
            text (str): The text of the utterance.
            scores (dict): Scores for the utterance, including word-level scores.
        
        Returns:
            str: The generated analysis feedback.
        """
        feedback = f"Your sentence ‘{text}’ scores:\n"
        feedback += f"- Accuracy {scores['accuracy']:.1f}: {self.rag.retrieve(f'accuracy: {scores['accuracy']}')}.\n"
        feedback += f"- Completeness {scores['completeness']:.1f}: {self.rag.retrieve(f'completeness: {scores['completeness']}')}.\n"
        feedback += f"- Fluency {scores['fluency']:.1f}: {self.rag.retrieve(f'fluency: {scores['fluency']}')}.\n"
        feedback += f"- Prosodic {scores['prosodic']:.1f}: {self.rag.retrieve(f'prosodic: {scores['prosodic']}')}.\n"
        
        for word in scores["word_scores"]:
            if word["accuracy"] < 8 or word["stress"] < 10:
                feedback += f"- ‘{word['text']}’ (accuracy: {word['accuracy']:.1f}, stress: {word['stress']:.1f}): "
                if "mispronunciations" in word and word["mispronunciations"]:
                    for mis in word["mispronunciations"]:
                        feedback += f"You said ‘{mis['pronounced-phone']}’ instead of ‘{mis['canonical-phone']}’. "
                else:
                    feedback += "Some phonemes need work. "
                
                # Ensure phones and phones-accuracy have the same length
                if len(word["phones"]) != len(word["phones-accuracy"]):
                    print(f"Warning: Mismatch in utterance {utt_id}, word '{word['text']}': "
                          f"phones={word['phones']}, phones-accuracy={word['phones-accuracy']}")
                    continue  # Skip this word to avoid IndexError
                
                for i, score in enumerate(word["phones-accuracy"]):
                    if score < 1.5:
                        phone = word["phones"][i]
                        feedback += f"Focus on ‘{phone}’—{'heavy accent' if 0.5 <= score < 1.5 else 'incorrect'} pronunciation.\n"
        
        return feedback