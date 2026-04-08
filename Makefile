PYTHON := python3
BUILD_SCRIPT := scripts/build.py

DATA_FILES := $(filter-out data/songs.json,$(wildcard data/*.json))
SLUGS := $(patsubst data/%.json,%,$(DATA_FILES))
SONG_PAGES := $(patsubst %, %/index.html, $(SLUGS))

.PHONY: all build check clean one force

all: build

build: index.html

index.html: $(SONG_PAGES) templates/index.html scripts/build.py
	$(PYTHON) $(BUILD_SCRIPT)

%/index.html: data/%.json templates/song.html scripts/build.py
	$(PYTHON) $(BUILD_SCRIPT) $*

check:
	@for f in $(DATA_FILES); do \
		echo "Checking $$f"; \
		$(PYTHON) -m json.tool "$$f" > /dev/null; \
	done
	@echo "All JSON files look good."

one:
	@echo 'Usage: make one SONG=and-then'
	@test -n "$(SONG)"
	$(PYTHON) $(BUILD_SCRIPT) $(SONG)

clean:
	rm -f index.html data/songs.json
	rm -rf $(SLUGS)

force:
	$(PYTHON) $(BUILD_SCRIPT)
