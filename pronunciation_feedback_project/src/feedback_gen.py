import json
import os
from src.database import Database
from src.personalized_gen import PersonalizedGenerator

class FeedbackGenerator:
    def __init__(self, token=None):
        # Load the precomputed database
        if not os.path.exists("data/database.json"):
            raise FileNotFoundError("Database file 'data/database.json' not found. Run prepare_data.py first.")
        
        self.db = Database()
        self.personalized_gen = PersonalizedGenerator(token=token)
        self.personalized_feedback_file = "data/personalized_feedback.json"
        try:
            with open(self.personalized_feedback_file, "r") as f:
                self.personalized_feedback = json.load(f)
        except FileNotFoundError:
            self.personalized_feedback = []
    
    def generate_analysis(self, utt_id, speaker_id=None, text=None, scores=None):
        """
        Generate or retrieve analysis feedback for an utterance.
        If the utterance is new (i.e., utt_id is not in the database), generate feedback and store it.
        
        Args:
            utt_id (str): Utterance ID.
            speaker_id (str, optional): Speaker ID (required for new utterances).
            text (str, optional): The spoken text (required for new utterances).
            scores (dict, optional): Scores for the utterance (required for new utterances).
        
        Returns:
            str: Analysis feedback.
        """
        # Check if the utterance already exists in the database
        analysis = self.db.get_analysis_feedback(utt_id)
        if analysis is not None:
            return analysis
        
        # If the utterance is new, ensure all required inputs are provided
        if not all([speaker_id, text, scores]):
            return f"Cannot generate analysis feedback for new utterance {utt_id}. Missing required inputs: speaker_id, text, or scores."
        
        # Generate analysis feedback for the new utterance
        feedback = [f"Your sentence '{text}' scores:"]
        feedback.append(f"- Accuracy {scores['accuracy']:.1f}: {'Good' if scores['accuracy'] >= 7 else 'Needs improvement'}, {'few' if scores['accuracy'] >= 7 else 'several'} pronunciation mistakes.")
        feedback.append(f"- Completeness {scores['completeness']:.1f}: {'All' if scores['completeness'] == 1.0 else 'Some'} words pronounced.")
        feedback.append(f"- Fluency {scores['fluency']:.1f}: {'Fluent' if scores['fluency'] >= 7 else 'Needs work'}, {'no noticeable pauses' if scores['fluency'] >= 7 else 'some pauses'}.")
        feedback.append(f"- Prosodic {scores['prosodic']:.1f}: {'Nearly correct' if scores['prosodic'] >= 7 else 'Needs improvement'} intonation, {'little' if scores['prosodic'] >= 7 else 'some'} stammering.")
        
        for word_score in scores["word_scores"]:
            word = word_score["word"]
            phones = word_score.get("phones", [])
            phones_accuracy = word_score.get("phones-accuracy", [])
            stress = word_score.get("stress", 0.0)
            mispronunciations = word_score.get("mispronunciations", [])
            
            feedback.append(f"- '{word}' (accuracy: {word_score['accuracy']:.1f}, stress: {stress:.1f}):")
            for mis in mispronunciations:
                feedback.append(f"  You said '{mis['produced-phone']}' instead of '{mis['canonical-phone']}'. Focus on '{mis['canonical-phone']}'—heavy accent pronunciation.")
        
        analysis_feedback = "\n".join(feedback)
        
        # Store the new utterance in the database
        self.db.insert_utterance(utt_id, speaker_id, text, scores, analysis_feedback)
        
        return analysis_feedback
    
    def generate_personalized(self, speaker_id, current_utt_id):
        """
        Generate personalized feedback for a speaker.
        
        Args:
            speaker_id (str): Speaker ID.
            current_utt_id (str): Current utterance ID.
        
        Returns:
            str: Personalized feedback.
        """
        feedback = self.personalized_gen.generate_personalized(self.db, speaker_id, current_utt_id)
        self._save_personalized_feedback(speaker_id, feedback)
        return feedback
    
    def _save_personalized_feedback(self, speaker_id, feedback):
        """
        Save personalized feedback to a separate file (not the database).
        
        Args:
            speaker_id (str): Speaker ID.
            feedback (str): Personalized feedback.
        """
        self.personalized_feedback.append({"speaker_id": speaker_id, "personalized_feedback": feedback})
        with open(self.personalized_feedback_file, "w") as f:
            json.dump(self.personalized_feedback, f, indent=2)