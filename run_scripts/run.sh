# 定义时间戳函数
function now() {
    date '+%Y-%m-%d-%H-%M'
}
mkdir -p logs
# 设置 GPU 并运行，使用合适的日志路径
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export LD_LIBRARY_PATH=~/miniforge3/envs/decompose/lib:$LD_LIBRARY_PATH
bash examples/sglang_multiturn/search_r1_like/run_qwen2.5-7b_instruct_search_multiturn_legal_v4.sh trainer.experiment_name=qwen2.5-7b-it_rm-searchR1-like-sgl-multiturn-$(now) > logs/searchR1-like$(now).log 2>&1
