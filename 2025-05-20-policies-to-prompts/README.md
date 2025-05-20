# 🦄 policy to prompt: evaluating the enron email dataset against SEC regulations

one of the most common problems in AI engineering is looking at a set of policies / rules and evaluating evidence to determine if the rules were followed. In this session we'll explore turning policies into prompts and pipelines to evaluate which emails in the massive [enron email dataset](https://www.cs.cmu.edu/~enron/) violated SEC and Sarbanes-Oxley regulations.

Video • [RSVP](https://lu.ma/iw1d9l3j)

## Overview

## Running this code

### installing dependencies

```bash
# Install dependencies
uv sync
```

### Download the enron email dataset

```bash
wget 'https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz'
```

unzip the file

```bash
tar -xzvf enron_mail_20150507.tar.gz
```

### Download sarbanes-oxley rules (plaintext)

```bash
wget 'https://www.govinfo.gov/content/pkg/PLAW-107publ204/html/PLAW-107publ204.htm'
```


### Download the JPMC 2024 code of conduct (pdf)

```
wget 'https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/documents/code-of-conduct.pdf'
```


### run the code

```
# Run the code:
python enron.py
```

## Key Topics


## Session Notes

