CURRENT_DIR := $(shell pwd)
SCRIPT := $(CURRENT_DIR)/start.sh

all: run_bot

run_bot:
	@chmod +x $(SCRIPT)
	@nohup $(SCRIPT) > /tmp/quiz-bot.log 2>&1 &