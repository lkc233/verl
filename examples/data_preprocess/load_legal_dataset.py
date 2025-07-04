from datasets import load_dataset

# Specify the path to the directory containing the Parquet files
dataset_path = "/home/luokc/research/repos/legal-reasoning-question-decompose/rl/verl/data/jec_qa_search_filtered/"

# Load the dataset from the Parquet files
dataset = load_dataset('parquet', data_files={'train': f'{dataset_path}/train.parquet', 'test': f'{dataset_path}/test.parquet'})

# Access the train and test splits
train_dataset = dataset['train']
test_dataset = dataset['test']

# Iterate over the train set
print("Iterating over the train set:")
for example in train_dataset:
    # Process each example as needed
    print(example)

# Iterate over the test set
print("\nIterating over the test set:")
for example in test_dataset:
    # Process each example as needed
    print(example)
