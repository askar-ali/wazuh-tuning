.PHONY: test lint check
check lint:
	python3 -I scripts/check-xml.py rules/local_rules.xml decoders/local_decoder.xml config/*.conf config/agent-groups/*/agent.conf
	python3 -I scripts/lint-rules.py
	shellcheck scripts/*.sh active-response/*.sh tests/*.sh

test:
	python3 -I -m unittest discover -s scripts/tests
	tests/test-safe-block.sh
