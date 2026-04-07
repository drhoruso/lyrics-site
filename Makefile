PYTHON := python3
BUILD_SCRIPT := scripts/build.py

.PHONY: all build check clean one

all: build

build:
	$(PYTHON) $(BUILD_SCRIPT)

check:
	$(PYTHON) -m json.tool data/and-then.json > /dev/null
	@echo "JSON looks good."

one:
	@echo 'Usage: make one SONG=and-then'
	@test -n "$(SONG)"
	$(PYTHON) $(BUILD_SCRIPT) $(SONG)

clean:
	rm -f index.html
	rm -f data/songs.json
	rm -f and-then/index.html
	rm -f the-dancing-girl/index.html
	rm -f glass-ties/index.html
