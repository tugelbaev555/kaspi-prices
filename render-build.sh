#!/usr/bin/env bash
# Қажетті кітапханаларды орнату
pip install -r requirements.txt

# Playwright браузерін жүктеп алу (бұл ең маңызды бөлік)
playwright install
playwright install-deps
