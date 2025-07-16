#!/bin/bash

# 设置检查间隔时间（秒）
CHECK_INTERVAL=3

# 设置GPU利用率阈值（%），低于此值认为GPU闲置
UTILIZATION_THRESHOLD=5

# 设置GPU内存使用阈值（MB），低于此值认为GPU闲置
MEMORY_THRESHOLD=100

# 检查nvidia-smi是否可用
if ! command -v nvidia-smi &> /dev/null; then
    echo "错误：nvidia-smi 未找到，请确保NVIDIA驱动已安装"
    exit 1
fi

# # 检查train.sh是否存在且可执行
# if [ ! -x "train.sh" ]; then
#     echo "错误：train.sh 不存在或不可执行"
#     exit 1
# fi

echo "开始监控GPU使用情况，检查间隔: ${CHECK_INTERVAL}秒"
echo "GPU利用率阈值: ${UTILIZATION_THRESHOLD}%"
echo "GPU内存使用阈值: ${MEMORY_THRESHOLD}MB"

while true; do
    # 获取GPU使用情况
    GPU_INFO=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits)
    
    ALL_IDLE=true
    
    # 检查每个GPU
    while IFS=, read -r util mem; do
        util=${util// /}
        mem=${mem// /}
        
        echo "GPU使用率: ${util}%, 显存使用: ${mem}MB"
        
        if [ "$util" -ge "$UTILIZATION_THRESHOLD" ] || [ "$mem" -ge "$MEMORY_THRESHOLD" ]; then
            ALL_IDLE=false
            break
        fi
    done <<< "$GPU_INFO"
    
    if $ALL_IDLE; then
        echo "所有GPU都处于闲置状态，开始运行train.sh"
        bash "run_scripts/run.sh"
        echo "train.sh 执行完成，退出监控"
        exit 0
    else
        echo "GPU正在使用中，等待下一次检查..."
    fi
    
    sleep $CHECK_INTERVAL
done