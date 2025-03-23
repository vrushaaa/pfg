from src.database import Database
from src.analysis_gen import AnalysisGenerator

class DataPreparer:
    def __init__(self):
        self.db = Database()
        self.analysis_gen = AnalysisGenerator()
        
        # Generate and save analysis feedback for all utterances
        utterances_to_process = self.db.data["utterances"]
        print(f"Processing all {len(utterances_to_process)} utterances for all speakers")
        
        # Process utterances in batches to reduce memory and I/O overhead
        batch_size = 100  # Process 100 utterances at a time
        for i in range(0, len(utterances_to_process), batch_size):
            batch = utterances_to_process[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1} of {len(utterances_to_process) // batch_size + 1} "
                  f"({len(batch)} utterances)")
            for utt in batch:
                utt_id = utt["utt_id"]
                text = utt["text"]
                scores = self.db.get_scores(utt_id)
                if scores:
                    if utt["analysis_feedback"] is None:  # Only generate if not already present
                        analysis_feedback = self.analysis_gen.generate_analysis(utt_id, text, scores)
                        print(f"Generated analysis feedback for utterance {utt_id}")
                        self.db.save_analysis_feedback(utt_id, analysis_feedback, batch=True)
                    else:
                        print(f"Analysis feedback already exists for utterance {utt_id}")
                else:
                    print(f"No scores found for utterance {utt_id}, skipping analysis feedback generation")
            
            # Save the batch to disk
            print(f"Saving batch {i // batch_size + 1}")
            self.db.batch_save()