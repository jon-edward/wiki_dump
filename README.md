# wiki_data_dump
A library that assists in traversing and downloading from 
[Wikimedia Data Dumps](https://dumps.wikimedia.org) and its mirrors.

## Purpose
To make the maintenance of large wiki datasets easier and more stable. 

In addition, the purpose is to lighten the load on Wikimedia and its mirrors by 
accessing only the index of the site, and doing the inevitable searching and 
navigation of its contents offline. 

A web crawler might make multiple requests to find its file (in addition to 
navigating with the notorious fragility of a web crawler), while `wiki_data_dump` 
caches the site's contents - which not only provides a speed boost for multiple 
uses of the library but protects against accidentally flooding
Wikimedia with requests by not relying on requests for site navigation.

## Installation
`pip install wiki_data_dump`

## Usage
One could easily get all available job names for any given wiki with this 
short script:

```python
from wiki_data_dump import WikiDump, Wiki

wiki = WikiDump()
en_wiki: Wiki = wiki.get_wiki('enwiki')

print(en_wiki.jobs.keys())
```

Or, you could see the available files from the `categorytables` sql job.

```python
from wiki_data_dump import WikiDump, Job

wiki = WikiDump()
categories: Job = wiki.get_job("enwiki", "categorytables")

print(categories.files.keys())
```

A slightly more nontrivial example - querying for specific file types when a job 
may contain more files than we need.

For example, it's not uncommon to find a job that has partial data dumps - making
it necessary to know the file paths of all parts. If you're hard-coding all the 
file names, it becomes increasingly difficult to find the relevant files.

This is a solution that `wiki_data_dump` provides:
```python
from wiki_data_dump import WikiDump, File
import re
from typing import List

wiki = WikiDump()

xml_stubs_dump_job = wiki["enwiki", "xmlstubsdump"]

stub_history_files: List[File] = xml_stubs_dump_job.get_files(
    re.compile(r"stub-meta-history[0-9]+\.xml\.gz$")
)

for file in stub_history_files:
    wiki.download(file).join()
```

Download processes are threaded by default, and the call to `WikiDump.download`
returns a reference to the thread it's running in.

The process is simple and readable: 
1. Get the job that contains the files desired.
2. Filter the files to only contain those that you need.
3. Download the files concurrently (or in parallel).

## Next steps

* Bars showing appropriate progress over multiple threads.
* Automatic detection of which mirror has the fastest download speed at any 
given time.
* Caching that updates only when a resource is out of date, instead of just when
the current date has passed the cache's creation date.
* The ability to access Wikimedia downloads available in 
[`/other/`](https://dumps.wikimedia.org/other/).

## Disclaimer
The author of this software is not affiliated, associated, authorized, endorsed by, 
or in any way officially connected with Wikimedia or any of its affiliates and is 
independently owned and created.