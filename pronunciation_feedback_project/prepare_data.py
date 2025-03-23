from src.data_preparer import DataPreparer

def main():
    print("Starting data preparation...")
    preparer = DataPreparer()
    print("Data preparation completed. Database saved to data/database.json")

if __name__ == "__main__":
    main()