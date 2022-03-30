# wiki_dump
A library that assists in traversing and downloading from Wikimedia Data Dumps 
and its mirrors.

## Installation
`pip install wiki_dump`

## Usage
This library is designed to provide readability and stability to the process 
of traversing the site map of and downloading from Wikimedia Data Dumps.

One could easily get all available job names for any given wiki with 
short script:

```python
from wiki_dump import WikiDump, Wiki

wiki = WikiDump()
en_wiki: Wiki = wiki.get_wiki('enwiki')

print(en_wiki.jobs.keys())
```

