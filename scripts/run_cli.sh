PROJECT_PATH="$(git rev-parse --show-toplevel)"
cd "${PROJECT_PATH}"

# Clear system_run.log on new run
rm -f system_run.log

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

export PYTHONIOENCODING=utf-8

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#     --workflow-dataset=STAR \
#     --workflow-type=flowchart --workflow-id=022 \
#     --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#     --bot-mode=react_bot --bot-llm-name=openai/gpt-oss-20b \
#     --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#     --bot-template-fn=baselines/flowbench.jinja \
#     --conversation-turn-limit=20 --log-utterence-time --log-to-db

# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#     --workflow-dataset=STAR \
#     --workflow-type=flowchart --workflow-id=022 \
#     --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#     --bot-mode=react_bot --bot-llm-name=openai/gpt-oss-20b \
#     --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#     --bot-template-fn=baselines/flowbench.jinja \
#     --conversation-turn-limit=20 --log-utterence-time --log-to-db

# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#    --workflow-dataset=STAR \
#    --workflow-type=flowchart --workflow-id=005 \
#    --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#    --bot-mode=state_react_bot --bot-llm-name=openai/gpt-oss-20b \
#    --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#    --bot-template-fn=baselines/state_flowbench.jinja \
#    --conversation-turn-limit=20 --log-utterence-time --log-to-db

CLI_ARGS=(
    --config=default.yaml
    --exp-version=defaultss
    --exp-mode=session
    --workflow-dataset=STAR
    --workflow-type=flowchart
    --workflow-id=005
    --user-mode=manual
    --user-llm-name=openai/qwen2.5-3b-instruct
    --user-profile-id=0
    --bot-mode=state_react_bot
    --bot-llm-name=openai/qwen2.5-3b-instruct
    --api-mode=real_api
    --api-llm-name=openai/qwen2.5-3b-instruct
    --bot-template-fn=baselines/state_flowbench.jinja
    --conversation-turn-limit=-1
    --log-utterence-time
    --log-to-db
)

if [[ " ${CLI_ARGS[*]} " == *" --api-mode=real_api "* ]]; then
    echo "Starting backend server (backend/app.py) in background..."
    rm -f backend/backend.log
    
    PYTHON_BIN="python"
    if [ -f ".venv/Scripts/python.exe" ]; then
        PYTHON_BIN=".venv/Scripts/python.exe"
    elif [ -f ".venv/bin/python" ]; then
        PYTHON_BIN=".venv/bin/python"
    fi
    
    $PYTHON_BIN backend/app.py > backend/backend.log 2>&1 &
    BACKEND_PID=$!
    trap 'if [ ! -z "$BACKEND_PID" ]; then kill $BACKEND_PID 2>/dev/null; fi' EXIT
    sleep 3
fi

python run_flowagent_cli.py "${CLI_ARGS[@]}"
