import json
import os
from statistics import mean

class Database:
    def __init__(self, scores_detail_path="data/speechocean762-main/resource/scores-detail.json",
                 scores_path="data/speechocean762-main/resource/scores.json",
                 text_phone_path="data/speechocean762-main/resource/text-phone",
                 lexicon_path="data/speechocean762-main/resource/lexicon.txt",
                 utt2spk_path="data/speechocean762-main/train/utt2spk"):
        self.database_path = "data/database.json"
        
        # Check if the database file already exists
        if os.path.exists(self.database_path):
            print(f"Loading precomputed database from {self.database_path}")
            with open(self.database_path, "r") as f:
                self.data = json.load(f)
            
            # Convert speakers from list to dictionary if necessary
            if isinstance(self.data["speakers"], list):
                speaker_dict = {}
                for speaker_id in self.data["speakers"]:
                    # Find all utterances for this speaker
                    utt_ids = [utt["utt_id"] for utt in self.data["utterances"] if utt["speaker_id"] == speaker_id]
                    speaker_dict[speaker_id] = sorted(utt_ids)
                self.data["speakers"] = speaker_dict
            
            # Convert utterances from list to dictionary if necessary
            if isinstance(self.data["utterances"], list):
                utt_dict = {}
                for utt in self.data["utterances"]:
                    utt_id = utt["utt_id"]
                    utt_dict[utt_id] = utt
                self.data["utterances"] = utt_dict
                # Save the updated database to ensure the new format is used going forward
                self.batch_save()
            
            print(f"Loaded {len(self.data['utterances'])} utterances for {len(self.data['speakers'])} speakers")
            speaker_0001_utts = self.data["speakers"].get("0001", [])
            print(f"Utterances for '0001': {len(speaker_0001_utts)} - {', '.join(speaker_0001_utts)}")
            return
        
        # If the database doesn't exist, build it
        print("Building database from scratch...")
        
        # Load utt2spk
        self.utt2spk = {}
        with open(utt2spk_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 2:
                    print(f"Invalid utt2spk line: {line.strip()}")
                    continue
                utt_id, spk_id = parts
                self.utt2spk[utt_id] = spk_id
        print(f"Loaded {len(self.utt2spk)} utt2spk mappings. Sample: {list(self.utt2spk.items())[:5]}")
        
        # Load scores-detail.json
        with open(scores_detail_path, "r") as f:
            self.scores_detail = json.load(f)
        
        # Load scores.json
        with open(scores_path, "r") as f:
            self.scores = json.load(f)
        
        # Load text-phone
        self.text_phone = {}
        with open(text_phone_path, "r") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    utt_id, phones = parts
                    self.text_phone[utt_id] = phones
        
        # Load lexicon.txt
        self.lexicon = {}
        with open(lexicon_path, "r") as f:
            for line in f:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    word, phones = parts
                    self.lexicon[word] = phones
        
        # Build database
        self.data = {
            "speakers": {},
            "utterances": {}
        }
        
        for utt_id in self.scores_detail.keys():
            speaker_id = self.utt2spk.get(utt_id, utt_id[:5])
            text = self.scores_detail[utt_id]["text"]
            
            # Build scores for the utterance
            score_entry = {
                "accuracy": mean(self.scores_detail[utt_id]["accuracy"]) if isinstance(self.scores_detail[utt_id]["accuracy"], list) else self.scores_detail[utt_id]["accuracy"],
                "completeness": mean(self.scores_detail[utt_id]["completeness"]) if isinstance(self.scores_detail[utt_id]["completeness"], list) else self.scores_detail[utt_id]["completeness"],
                "fluency": mean(self.scores_detail[utt_id]["fluency"]) if isinstance(self.scores_detail[utt_id]["fluency"], list) else self.scores_detail[utt_id]["fluency"],
                "prosodic": mean(self.scores_detail[utt_id]["prosodic"]) if isinstance(self.scores_detail[utt_id]["prosodic"], list) else self.scores_detail[utt_id]["prosodic"],
                "total": mean(self.scores_detail[utt_id]["total"]) if isinstance(self.scores_detail[utt_id]["total"], list) else self.scores_detail[utt_id]["total"]
            }
            
            word_scores = []
            for word in self.scores_detail[utt_id].get("words", []):
                word_entry = {
                    "text": word["text"],
                    "accuracy": mean(word["accuracy"]) if isinstance(word["accuracy"], list) else word["accuracy"],
                    "stress": mean(word["stress"]) if isinstance(word["stress"], list) else word["stress"],
                    "total": mean(word["total"]) if isinstance(word["total"], list) else word["total"],
                    "phones": word["ref-phones"].split(),
                    "phones-accuracy": self._parse_phoneme_scores(word["phones"], word["ref-phones"])
                }
                if any(isinstance(p, str) and any(c in p for c in "(){}[]") for p in word["phones"]):
                    word_entry["mispronunciations"] = self._detect_mispronunciations(word["ref-phones"], word["phones"])
                word_scores.append(word_entry)
            score_entry["word_scores"] = word_scores
            
            # Add utterance to the utterances dictionary
            self.data["utterances"][utt_id] = {
                "utt_id": utt_id,
                "speaker_id": speaker_id,
                "text": text,
                "audio_path": f"WAVE/SPEAKER{speaker_id}/{utt_id}.wav",
                "text_phone": self.text_phone.get(utt_id, ""),
                "scores": score_entry,
                "analysis_feedback": None  # Placeholder for analysis feedback
            }
            
            # Update the speakers dictionary
            if speaker_id not in self.data["speakers"]:
                self.data["speakers"][speaker_id] = []
            self.data["speakers"][speaker_id].append(utt_id)
            self.data["speakers"][speaker_id].sort()
        
        print(f"Loaded {len(self.data['utterances'])} utterances for {len(self.data['speakers'])} speakers")
        speaker_0001_utts = self.data["speakers"].get("0001", [])
        print(f"Utterances for '0001': {len(speaker_0001_utts)} - {', '.join(speaker_0001_utts)}")
        
        # Save the initial database to a file
        self.batch_save()
    
    def _parse_phoneme_scores(self, phones_list, ref_phones):
        ref_phones = ref_phones.split()
        scores = [[] for _ in ref_phones]
        for expert_phones in phones_list:
            phones = expert_phones.split()
            # Ensure we don’t exceed the length of ref_phones
            for i in range(min(len(phones), len(ref_phones))):
                phone = phones[i]
                if "(" in phone and ")" in phone:
                    scores[i].append(0)
                elif "{" in phone and "}" in phone:
                    scores[i].append(1)
                else:
                    scores[i].append(2)
        # Ensure scores list matches the length of ref_phones
        return [mean(s) if s else 2.0 for s in scores]  # Default to 2.0 if no scores for a phoneme
    
    def _detect_mispronunciations(self, ref_phones, phones_list):
        mispronunciations = []
        ref = ref_phones.split()
        for i in range(len(ref)):
            pronounced_counts = {"<unk>": 0, "correct": 0, "inserted": {}}
            for expert_phones in phones_list:
                phones = expert_phones.split()
                if i >= len(phones):
                    continue
                pronounced = phones[i]
                if "(" in pronounced and ")" in pronounced:
                    pronounced_counts["<unk>"] += 1
                elif "[" in pronounced and "]" in pronounced:
                    inserted = pronounced.strip("[]")
                    pronounced_counts["inserted"][inserted] = pronounced_counts["inserted"].get(inserted, 0) + 1
                elif "{" not in pronounced and "}" not in pronounced:
                    pronounced_counts["correct"] += 1
            if pronounced_counts["<unk>"] > 0:
                mispronunciations.append({"canonical-phone": ref[i], "index": i, "pronounced-phone": "<unk>"})
            if pronounced_counts["inserted"]:
                most_common = max(pronounced_counts["inserted"].items(), key=lambda x: x[1])[0]
                if pronounced_counts["inserted"][most_common] > 0:
                    mispronunciations.append({"canonical-phone": ref[i], "index": i, "pronounced-phone": most_common})
        return mispronunciations
    
    def insert_utterance(self, utt_id, speaker_id, text, scores, analysis_feedback):
        """
        Insert a new utterance into the database.
        
        Args:
            utt_id (str): Utterance ID.
            speaker_id (str): Speaker ID.
            text (str): The spoken text.
            scores (dict): Scores for the utterance.
            analysis_feedback (str): Analysis feedback for the utterance.
        """
        # Add the utterance to the utterances dictionary
        self.data["utterances"][utt_id] = {
            "utt_id": utt_id,
            "speaker_id": speaker_id,
            "text": text,
            "audio_path": f"WAVE/SPEAKER{speaker_id}/{utt_id}.wav",
            "text_phone": "",  # Not available for new utterances
            "scores": scores,
            "analysis_feedback": analysis_feedback
        }
        
        # Update the speakers dictionary
        if speaker_id not in self.data["speakers"]:
            self.data["speakers"][speaker_id] = []
        if utt_id not in self.data["speakers"][speaker_id]:
            self.data["speakers"][speaker_id].append(utt_id)
            self.data["speakers"][speaker_id].sort()
        
        # Save the updated database
        self.batch_save()
    
    def get_speaker_utterances(self, speaker_id):
        utt_ids = self.data["speakers"].get(speaker_id, [])
        return [self.data["utterances"][utt_id] for utt_id in utt_ids]
    
    def get_scores(self, utt_id):
        utt = self.data["utterances"].get(utt_id)
        return utt["scores"] if utt else None
    
    def get_speaker_history(self, speaker_id):
        return self.get_speaker_utterances(speaker_id)
    
    def get_speaker_analysis_history(self, speaker_id):
        utterances = self.get_speaker_utterances(speaker_id)
        return [utt["analysis_feedback"] for utt in utterances]
    
    def get_analysis_feedback(self, utt_id):
        utt = self.data["utterances"].get(utt_id)
        return utt["analysis_feedback"] if utt else None
    
    def save_analysis_feedback(self, utt_id, feedback, batch=False):
        if utt_id in self.data["utterances"]:
            self.data["utterances"][utt_id]["analysis_feedback"] = feedback
            print(f"Saved analysis feedback for utterance {utt_id}: {feedback[:50]}...")
        if not batch:
            print(f"Non-batch save: Writing database for utterance {utt_id}")
            self.batch_save()
    
    def batch_save(self):
        """Save all data to files in a single operation."""
        print("Batch saving database...")
        # Debug: Count how many utterances have non-null analysis feedback
        non_null_feedbacks = sum(1 for utt in self.data["utterances"].values() if utt["analysis_feedback"] is not None)
        print(f"Number of utterances with analysis feedback: {non_null_feedbacks}")
        with open(self.database_path, "w") as f:
            json.dump(self.data, f, indent=2)
        print("Database saved successfully")