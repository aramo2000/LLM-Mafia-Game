# LLM-Mafia-Game






```shell
#Setup .env file
cp .env.example .env

# Create Virtual env
virtualenv venv

# Install necessary packages
pip install -r requirements.txt

# Package for textblob emotions (required only for the analysis)
python -m textblob.download_corpora
```