from datasets import load_dataset
import json
# 加载数据集
dataset = load_dataset('parquet', data_files={
    'train': '/home/luokc/data/searchR1_processed_direct/train.parquet'
})

# 查看第一条训练数据
item = dataset['train'][0]

print(json.dumps(item, indent=2, ensure_ascii=False))

