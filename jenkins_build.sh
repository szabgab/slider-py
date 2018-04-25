#!/bin/bash
virtualenv venv
source venv/bin/activate
pip install pytest
pip install -r requirements.txt
pytest

