# personalized_feedback-generation
# Pronunciation Feedback Project
A RAG-based system for generating personalized pronunciation feedback using speechocean762 data.

## Setup
1. Create venv: `python3 -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install deps: `pip install -r requirements.txt`
4. Run: `python main.py`

## Features
- Analyzes scores from speechocean762 dataset.
- Provides personalized feedback with improvement tips.

Repo structure:
pronunciation_feedback_project/
├── venv/                  # Virtual environment
├── data/                  # Store your dataset and dummy DB
│   ├── speechocean762/    # Extracted ZIP contents (e.g., scores.json)
│   └── dummy_db.json      # Our dummy database
├── src/                   # Source code
│   ├── __init__.py
│   ├── rag_setup.py       # RAG retrieval and embedding logic
│   ├── feedback_gen.py    # Feedback generation logic
│   └── database.py        # Database handling
├── README.md              # Project documentation
└── main.py                # Entry point

 download the apeechocean dataset and put it in data folder

I'm glad you're happy with the outcome! Since the script is working well with input validation and you don't need batch processing right now, I'll focus on creating a detailed `README.md` file with documentation for your pronunciation feedback project. The documentation will include an overview of the project, setup instructions, usage examples, file structure, and details about the input validation and output.

Below is the `README.md` content written in Markdown (`.md`) format. You can copy this into a `README.md` file in your project directory.

---

# Pronunciation Feedback Project

## Overview

The Pronunciation Feedback Project is a Python-based tool designed to provide detailed pronunciation feedback for non-native English speakers. It analyzes spoken utterances, generates analysis feedback for individual utterances, and provides personalized feedback for speakers based on their pronunciation history. The project leverages a precomputed database of utterances, integrates with the Hugging Face Inference API for generating personalized feedback, and includes robust input validation to ensure reliable operation.

### Features
- **Analysis Feedback**: Provides detailed feedback on pronunciation accuracy, fluency, prosodic features, and completeness for each utterance, including specific phoneme-level mispronunciations.
- **Personalized Feedback**: Generates encouraging, personalized feedback for speakers based on their pronunciation history, focusing on strengths and areas for improvement with practical tips.
- **Input Validation**: Ensures all inputs (numerical scores and JSON data) are valid, providing user-friendly error messages for invalid inputs.
- **Database Integration**: Stores utterance data and feedback in a JSON database (`data/database.json`) for persistence and retrieval.
- **Hugging Face Inference API**: Uses the `google/gemma-2-2b-it` model to generate personalized feedback with retry logic for robustness.

## Prerequisites

Before running the project, ensure you have the following:

- **Python 3.6+**: The project is written in Python and requires a compatible version.
- **Required Python Packages**:
  - `huggingface_hub`: For interacting with the Hugging Face Inference API.
  - `statistics`: For calculating mean scores (part of Python's standard library).
  Install the required package using:
  ```bash
  pip install huggingface_hub
  ```
- **Hugging Face API Token**: You need a Hugging Face API token to use the Inference API. You can obtain one by signing up at [Hugging Face](https://huggingface.co) and generating a token under your account settings. The token used in the script is `ur hugging face token` (replace with your own token if needed).
- **Dataset Files**: The project uses the `speechocean762` dataset for building the initial database. Ensure the following files are present in the specified directories:
  - `data/speechocean762-main/resource/scores-detail.json`
  - `data/speechocean762-main/resource/scores.json`
  - `data/speechocean762-main/resource/text-phone`
  - `data/speechocean762-main/resource/lexicon.txt`
  - `data/speechocean762-main/train/utt2spk`

## Setup

1. **Clone the Repository** (if applicable):
   If the project is hosted in a repository, clone it to your local machine:
   ```bash
   git clone <repository-url>
   cd pronunciation_feedback_project
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   Create and activate a virtual environment to manage dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install huggingface_hub
   ```

4. **Verify Dataset Files**:
   Ensure the `speechocean762` dataset files are in the `data/speechocean762-main/` directory as specified above. If the database (`data/database.json`) does not exist, the script will build it automatically on the first run.

5. **Update API Token** (if necessary):
   The script uses a Hugging Face API token in `generate_feedback.py`. If you need to use a different token, update the `token` parameter in the `FeedbackGenerator` initialization:
   ```python
   fg = FeedbackGenerator(token="your_hugging_face_api_token")
   ```

## Usage

The script (`generate_feedback.py`) can be run from the command line to generate pronunciation feedback for a single utterance. It accepts several required arguments to specify the utterance details and scores.

### Command-Line Arguments
| Argument         | Description                                                                 | Example Value                                                                 |
|------------------|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `--speaker_id`   | Speaker ID (e.g., `0001`)                                                  | `0001`                                                                        |
| `--utt_id`       | Utterance ID (e.g., `000010200`)                                           | `000010200`                                                                   |
| `--text`         | The spoken text (e.g., `HELLO WORLD`)                                      | `HELLO WORLD`                                                                 |
| `--accuracy`     | Accuracy score (0-10) for the utterance                                    | `7.5`                                                                         |
| `--fluency`      | Fluency score (0-10) for the utterance                                     | `8.0`                                                                         |
| `--prosodic`     | Prosodic score (0-10) for the utterance                                    | `7.8`                                                                         |
| `--completeness` | Completeness score (0-10) for the utterance                                | `1.0`                                                                         |
| `--word_scores`  | JSON string of word scores, including phoneme-level details and mispronunciations | `'[{"word": "HELLO", "accuracy": 7.0, "stress": 8.0, "phones": ["HH", "EH1", "L", "OW0"], "phones-accuracy": [2.0, 1.0, 2.0, 2.0], "mispronunciations": [{"canonical-phone": "EH1", "produced-phone": "<unk>"}]}]'` |

### Example Command
Run the script with the following command to generate feedback for a single utterance:

```bash
python generate_feedback.py --speaker_id 0001 --utt_id 000010200 --text "HELLO WORLD" --accuracy 7.5 --fluency 8.0 --prosodic 7.8 --completeness 1.0 --word_scores '[{"word": "HELLO", "accuracy": 7.0, "stress": 8.0, "phones": ["HH", "EH1", "L", "OW0"], "phones-accuracy": [2.0, 1.0, 2.0, 2.0], "mispronunciations": [{"canonical-phone": "EH1", "produced-phone": "<unk>"}]}, {"word": "WORLD", "accuracy": 6.5, "stress": 7.5, "phones": ["W", "ER1", "L", "D"], "phones-accuracy": [2.0, 1.0, 2.0, 2.0], "mispronunciations": [{"canonical-phone": "ER1", "produced-phone": "<unk>"}]}]'
```

### Example Output
The script will generate analysis feedback for the utterance and personalized feedback for the speaker:

```
Starting feedback generation...
Loading precomputed database from data/database.json
Loaded 5001 utterances for 250 speakers
Utterances for '0001': 21 - 000010011, 000010035, 000010053, 000010063, 000010069, 000010075, 000010089, 000010095, 000010106, 000010113, 000010115, 000010121, 000010122, 000010133, 000010135, 000010140, 000010145, 000010149, 000010168, 000010173, 000010200
Initializing Inference API client for google/gemma-2-2b-it...
Inference API client initialized successfully

Analysis Feedback for 000010200:
Your sentence 'HELLO WORLD' scores:
- Accuracy 7.5: Good, few pronunciation mistakes.
- Completeness 1.0: All words pronounced.
- Fluency 8.0: Fluent, no noticeable pauses.
- Prosodic 7.8: Nearly correct intonation, little stammering.
- 'HELLO' (accuracy: 7.0, stress: 8.0):
  You said '<unk>' instead of 'EH1'. Focus on 'EH1'—heavy accent pronunciation.
- 'WORLD' (accuracy: 6.5, stress: 7.5):
  You said '<unk>' instead of 'ER1'. Focus on 'ER1'—heavy accent pronunciation.

Personalized Feedback for Speaker 0001:
You're doing a fantastic job! Your pronunciation is very accurate, and you have a natural fluency in your speech. You've identified some areas where you'd like to improve, particularly with the 'R', 'TH', and 'AA0' sounds. Using online resources like Forvo (https://forvo.com) and YouGlish (https://youglish.com) can be incredibly helpful—listen to native speakers pronounce these sounds, focusing on their tongue placement and the rhythm of the words.
```

### Input Validation
The script includes robust input validation to ensure reliable operation:
- **Numerical Scores**: All scores (`accuracy`, `fluency`, `prosodic`, `completeness`) must be floats between 0 and 10.
- **Word Scores JSON**:
  - Must be a valid JSON list of word score objects.
  - Each word score object must include required fields: `word`, `accuracy`, `stress`, `phones`, `phones-accuracy`, and `mispronunciations`.
  - `accuracy` and `stress` must be between 0 and 10.
  - `phones` and `phones-accuracy` arrays must have the same length, and `phones-accuracy` values must be between 0 and 2.
  - `mispronunciations` entries must include `canonical-phone` and `produced-phone`.

#### Example of Invalid Input
If you provide an invalid `--accuracy` value:

```bash
python generate_feedback.py --speaker_id 0001 --utt_id 000010201 --text "HELLO WORLD" --accuracy 15 --fluency 8.0 --prosodic 7.8 --completeness 1.0 --word_scores '[{"word": "HELLO", "accuracy": 7.0, "stress": 8.0, "phones": ["HH", "EH1", "L", "OW0"], "phones-accuracy": [2.0, 1.0, 2.0, 2.0], "mispronunciations": [{"canonical-phone": "EH1", "produced-phone": "<unk>"}]}]'
```

**Output**:
```
usage: generate_feedback.py [-h] --speaker_id SPEAKER_ID --utt_id UTT_ID --text TEXT --accuracy ACCURACY --fluency FLUENCY --prosodic PROSODIC --completeness COMPLETENESS --word_scores WORD_SCORES
generate_feedback.py: error: argument --accuracy: Invalid accuracy: accuracy must be between 0 and 10, got 15.0
```

## File Structure

The project directory is structured as follows:

```
pronunciation_feedback_project/
│
├── data/
│   ├── database.json                  # Precomputed database of utterances and feedback
│   ├── personalized_feedback.json     # Personalized feedback for speakers
│   └── speechocean762-main/           # Dataset directory
│       ├── resource/
│       │   ├── scores-detail.json     # Detailed scores for utterances
│       │   ├── scores.json            # Overall scores for utterances
│       │   ├── text-phone             # Text-to-phone mappings
│       │   └── lexicon.txt            # Lexicon for word-to-phone mappings
│       └── train/
│           └── utt2spk                # Utterance-to-speaker mappings
│
├── src/
│   ├── database.py                    # Database management (loading, saving, and querying)
│   ├── feedback_gen.py                # Main feedback generation logic
│   └── personalized_gen.py            # Personalized feedback generation using Hugging Face API
│
├── generate_feedback.py               # Main script to run the feedback generation
└── README.md                          # Project documentation
```

## Output Files

- **`data/database.json`**:
  - Stores the database of utterances, including their scores, analysis feedback, and speaker mappings.
  - Updated whenever a new utterance is processed.
  - Example structure:
    ```json
    {
      "speakers": {
        "0001": ["000010011", "000010035", ..., "000010200"],
        ...
      },
      "utterances": {
        "000010200": {
          "utt_id": "000010200",
          "speaker_id": "0001",
          "text": "HELLO WORLD",
          "audio_path": "WAVE/SPEAKER0001/000010200.wav",
          "text_phone": "",
          "scores": {
            "accuracy": 7.5,
            "fluency": 8.0,
            "prosodic": 7.8,
            "completeness": 1.0,
            "word_scores": [...]
          },
          "analysis_feedback": "Your sentence 'HELLO WORLD' scores: ..."
        },
        ...
      }
    }
    ```

- **`data/personalized_feedback.json`**:
  - Stores personalized feedback for each speaker.
  - Updated whenever personalized feedback is generated.
  - Example structure:
    ```json
    [
      {
        "speaker_id": "0001",
        "personalized_feedback": "You're doing a fantastic job! ..."
      },
      ...
    ]
    ```

## Troubleshooting

- **Hugging Face API Errors**:
  - If the script fails to generate personalized feedback due to API issues, it will retry up to 3 times with a 5-second delay between attempts. Ensure your API token is valid and you have internet connectivity.
- **Missing Dataset Files**:
  - If the `speechocean762` dataset files are missing, the script will fail to build the database. Ensure all required files are in the `data/speechocean762-main/` directory.
- **Invalid Input**:
  - The script includes input validation to catch invalid inputs. Check the error message for details on how to fix the input (e.g., ensure scores are between 0 and 10, or fix the JSON syntax in `--word_scores`).

## Future Enhancements

- **Batch Processing**: Add support for processing multiple utterances at once via a JSON file input.
- **Phoneme Tips Enhancement**: Include more detailed phoneme practice tips, such as minimal pair exercises or tongue placement diagrams.
- **Logging**: Add logging to track script execution, API calls, and errors for better debugging.
- **User Interface**: Create a simple CLI or web interface to make the script more user-friendly.

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as needed.

## Acknowledgments

- The project uses the `speechocean762` dataset for building the initial database.
- Personalized feedback is generated using the `google/gemma-2-2b-it` model via the Hugging Face Inference API.
- Special thanks to the open-source community for providing the tools and resources that made this project possible.

---

This `README.md` provides comprehensive documentation for your project, covering setup, usage, file structure, and more. You can copy this content into a `README.md` file in your project directory, and it will render nicely on platforms like GitHub.

### Next Steps
The project is now well-documented and ready for use. If you’d like to explore any of the future enhancements mentioned in the `README.md` (e.g., phoneme tips enhancement, logging, or a user interface), or if you have any other requests, let me know! 😊

 