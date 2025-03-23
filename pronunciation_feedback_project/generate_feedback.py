import argparse
import json
from src.feedback_gen import FeedbackGenerator

def validate_score(value, name):
    """Validate that a score is a float between 0 and 10."""
    try:
        score = float(value)
        if not 0 <= score <= 10:
            raise ValueError(f"{name} must be between 0 and 10, got {score}")
        return score
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid {name}: {str(e)}")

def validate_word_scores(value):
    """Validate the word_scores JSON string."""
    try:
        word_scores = json.loads(value)
        if not isinstance(word_scores, list):
            raise ValueError("word_scores must be a list of word score objects")
        
        required_fields = ["word", "accuracy", "stress", "phones", "phones-accuracy", "mispronunciations"]
        for i, word_score in enumerate(word_scores):
            # Check for required fields
            for field in required_fields:
                if field not in word_score:
                    raise ValueError(f"Word score at index {i} is missing required field: {field}")
            
            # Validate numerical fields
            if not 0 <= word_score["accuracy"] <= 10:
                raise ValueError(f"Word score at index {i} has invalid accuracy: {word_score['accuracy']} (must be between 0 and 10)")
            if not 0 <= word_score["stress"] <= 10:
                raise ValueError(f"Word score at index {i} has invalid stress: {word_score['stress']} (must be between 0 and 10)")
            
            # Validate phones and phones-accuracy
            if len(word_score["phones"]) != len(word_score["phones-accuracy"]):
                raise ValueError(f"Word score at index {i} has mismatched phones and phones-accuracy lengths")
            for score in word_score["phones-accuracy"]:
                if not 0 <= score <= 2:
                    raise ValueError(f"Word score at index {i} has invalid phones-accuracy value: {score} (must be between 0 and 2)")
            
            # Validate mispronunciations
            for mis in word_score["mispronunciations"]:
                if "canonical-phone" not in mis or "produced-phone" not in mis:
                    raise ValueError(f"Word score at index {i} has invalid mispronunciation: missing canonical-phone or produced-phone")
        
        return word_scores
    except (json.JSONDecodeError, ValueError) as e:
        raise argparse.ArgumentTypeError(f"Invalid word_scores JSON: {str(e)}")

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Generate pronunciation feedback for a new utterance.")
    parser.add_argument("--speaker_id", required=True, help="Speaker ID (e.g., 0001)")
    parser.add_argument("--utt_id", required=True, help="Utterance ID (e.g., 000010200)")
    parser.add_argument("--text", required=True, help="The spoken text (e.g., 'HELLO WORLD')")
    parser.add_argument("--accuracy", type=lambda x: validate_score(x, "accuracy"), required=True, help="Accuracy score (e.g., 7.5)")
    parser.add_argument("--fluency", type=lambda x: validate_score(x, "fluency"), required=True, help="Fluency score (e.g., 8.0)")
    parser.add_argument("--prosodic", type=lambda x: validate_score(x, "prosodic"), required=True, help="Prosodic score (e.g., 7.8)")
    parser.add_argument("--completeness", type=lambda x: validate_score(x, "completeness"), required=True, help="Completeness score (e.g., 1.0)")
    parser.add_argument("--word_scores", type=validate_word_scores, required=True, help="JSON string of word scores (e.g., '[{\"word\": \"HELLO\", \"accuracy\": 7.0, \"stress\": 8.0, \"phones\": [\"HH\", \"EH1\", \"L\", \"OW0\"], \"phones-accuracy\": [2.0, 1.0, 2.0, 2.0], \"mispronunciations\": [{\"canonical-phone\": \"EH1\", \"produced-phone\": \"<unk>\"}]}]')")
    
    args = parser.parse_args()
    
    print("Starting feedback generation...")
    fg = FeedbackGenerator(token="put_ur_huggingface_token")
    
    # Construct the scores dictionary
    scores = {
        "accuracy": args.accuracy,
        "fluency": args.fluency,
        "prosodic": args.prosodic,
        "completeness": args.completeness,
        "word_scores": args.word_scores
    }
    
    # Generate analysis feedback for the new utterance
    print(f"\nAnalysis Feedback for {args.utt_id}:")
    analysis_feedback = fg.generate_analysis(
        utt_id=args.utt_id,
        speaker_id=args.speaker_id,
        text=args.text,
        scores=scores
    )
    print(analysis_feedback)
    
    # Generate personalized feedback for the speaker
    print(f"\nPersonalized Feedback for Speaker {args.speaker_id}:")
    personalized_feedback = fg.generate_personalized(args.speaker_id, args.utt_id)
    print(personalized_feedback)

if __name__ == "__main__":
    main()