PROJECT_PATH="$(git rev-parse --show-toplevel)"
cd "${PROJECT_PATH}"

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
fi

cd src
# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#     --workflow-type=pdl --workflow-id=000 \
#     --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#     --bot-mode=pdl_bot --bot-llm-name=openai/gpt-oss-20b \
#     --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#     --bot-template-fn=flowagent/bot_pdl.jinja \
#     --conversation-turn-limit=20 --log-utterence-time --log-to-db

# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#     --workflow-dataset=STAR \
#     --workflow-type=pdl --workflow-id=004 \
#     --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#     --bot-mode=pdl_bot --bot-llm-name=openai/gpt-oss-20b \
#     --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#     --bot-template-fn=flowagent/bot_pdl.jinja \
#     --conversation-turn-limit=20 --log-utterence-time --log-to-db

# python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
#     --workflow-dataset=STAR \
#     --workflow-type=flowchart --workflow-id=022 \
#     --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
#     --bot-mode=react_bot --bot-llm-name=openai/gpt-oss-20b \
#     --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
#     --bot-template-fn=baselines/flowbench.jinja \
#     --conversation-turn-limit=20 --log-utterence-time --log-to-db

python run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
    --workflow-dataset=STAR \
    --workflow-type=flowchart --workflow-id=005 \
    --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
    --bot-mode=state_react_bot --bot-llm-name=openai/gpt-oss-20b \
    --api-mode=llm --api-llm-name=openai/gpt-oss-20b \
    --bot-template-fn=baselines/state_flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db
