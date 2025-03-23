# Not needed don not use

from src.feedback_gen import FeedbackGenerator

def main():
    fg = FeedbackGenerator(speaker_id_to_process=None)  # Process all speakers
    print("Analysis Feedback for 000010035:")
    print(fg.generate_analysis("000010035"))
    print("\nAnalysis Feedback for 000010011:")
    print(fg.generate_analysis("000010011"))
    print("\nPersonalized Feedback:")
    print(fg.generate_personalized("0001", "000010173"))

if __name__ == "__main__":
    main()