[![Build](https://github.com/suryaavala/zen_search/workflows/Test%20Build%20and%20Publish/badge.svg)](https://github.com/suryaavala/zen_search/workflows/Test%20Build%20and%20Publish/badge.svg) [![Python 3.7.6](https://img.shields.io/badge/python-v3.7-blue.svg)](https://www.python.org/downloads/release/python-376/) [![Total alerts](https://img.shields.io/lgtm/alerts/g/suryaavala/zen_search.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/suryaavala/zen_search/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/suryaavala/zen_search.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/suryaavala/zen_search/context:python) 

## zensearch

A python implementation of a basic user ticketing system search - 🔎🕵️‍♂️🕵️‍♀️🔬🚀<sub><sup>random emoji insertion to add colours to this rather dull looking readme</sup></sub>

### Quick Start

#### 1. Using Docker

1.  docker
2.  log into dockerhub `docker login`
3.  `docker pull suryaavala/zensearch:latest`
4.  `docker run -it suryaavala/zensearch:latest`
    1.  Advanced usage
        ```
        docker run -it --mount type=bind,source="$(pwd)/<rel/path/to/data/dir>",target="/zensearch/<path/inside/dockercontainer/to/mount>" zensearch:prod -d ./<<path/inside/dockercontainer/to/mount>>
        ```
    2.  Example
        ```
        •••• docker run -it --mount type=bind,source="$(pwd)/data/gen",target="/zensearch/data/new" zensearch:prod -h
        usage: zensearch [-h] [-d DATADIR] [-n NUMBER]

        Searches through ticketing data (user, organization and ticket data) to find
        relevant matches as per the search selection

        optional arguments:
        -h, --help            show this help message and exit
        -d DATADIR, --datadir DATADIR
                                Relative Path to data directory containing data files
                                (*user*.json, *ticket*.json, *organization*.json)
        -n NUMBER, --number NUMBER
                                Number of interations to run the program/search for,
                                deafult is forever(-1) - (invalid selection is also
                                counted as an interation)
        ```

#### 2. Running Locally

1. Uses [Python 3.7.6](https://www.python.org/downloads/release/python-376/)
2. `git clone git@github.com:suryaavala/zen_search.git`
3. `cd zen_search`
4. `pip3 install -r requirements.txt`
5. `python3 main.py`
   1. Advanced usage
        ```
        •••• python3 main.py -h
            usage: zensearch [-h] [-d DATADIR] [-n NUMBER]

            Searches through ticketing data (user, organization and ticket data) to find
            relevant matches as per the search selection

            optional arguments:
            -h, --help            show this help message and exit
            -d DATADIR, --datadir DATADIR
                                    Relative Path to data directory containing data files
                                    (*user*.json, *ticket*.json, *organization*.json), default './data/import/'
            -n NUMBER, --number NUMBER
                                    Number of interations to run the program/search for,
                                    deafult is forever(-1) - (invalid selection is also
                                    counted as an interation)
        ```

--------------------------------------
### Approach

I have attempted to explain the basic approach I took. However, there's a good chance that I might have missed something (as I am writing this "quickly" after writing the code). Code is always (especially in this instance since I am only spending a limited amount of time on documentation) the best documentation/reference to see what's actually going on.

My focus in the approach is titled towards quick/efficient lookups/searches rather than resource management.

1.  Every `Entity` (user, ticket, organisation) is represented by their own `Entity()` object where json data from their respective file is loaded into `self._data` as list of dicts().
    1. example each `"user"` is a dictionary like `{ "_id": "", "url": "", "external_id": "", ...}` within `user._data` 
2.  All the data is kept in memory all the time (since the data fits in memory according to the specs)
3.  These entity objects contain multiple searchable indexes(`self._indices`), an index is built for each searchable field (for example, "_id", "url", etc.. for "users")
    ```users._indices = {"_id": {"1": <dict containing data for _id 1>,....}, "url": {"https://example.com": [1 #if id 1 has the url example.com#,...]},.....}```
    1. Indices are hashtables/dictionaries with value of the field as the dict key in the hash table and 
       1. the data point dict representing the item as index's dict value if it's a primary key index ("_id")
       2. the "_id" value of the data point is appended to the index's dict value list
   
    2. example `users` has indexes on `_id, url, external_id, created_at, etc`; example `_id` index could look like `{1: <entry pointing to user dict with id 1>}`, whereas `url` index looks like `{"example.com": [<id values of the entries whose url is example.com>]}`
4.  Searching an entity (user) triggers works as follows:
    1.  If we are searching for a primary key (example "_id" == 1 in users), all we have to do is return the corresponding entry in the primary key index. Therefore this operation is generally constant time `O(1)`
    2.  If we are searching for a non primary key, then looking at the relevant entry in that index gives a list of primary keys and we'd have to return their entries from primary key index. So this is an `O(m)` time operation where `m` is the number of matches, worst case scenario where we get every data point matched leads to `O(n)` time complexity (where n is the number of data points)
5. When it comes to related entries, it's just an abstraction on top of single `Entity()`
   1. example, search on `user._id` triggers a search on `ticket.submitter_id == user._id && ticket.assignee_id == user._id` && `organization.id == user.organization_id`

<i>The solution for search implementation at it's core is doing a hash table lookup for the search value in the index for the search term</i>

#### Improvements / Things to think about / Notes

    1. Data points are assigned to the primary key index using the assignment `=` operator, they are not copied but only referenced (in python)
    2. primary keys `1, True, 1.0` would have lead to collisions and undesirable behavior in python - casting all primary keys to string just does the trick here. P.S. `1.0, 1.00` are equal in python, so as soon as a key is `1.00`, python makes it `1.0` so if we really want `1.00` it has to be string in the data.
    3. Refactor tests to make them more streamlined, modular
    4. Refactor exceptions to make them more streamlined and cover more cases
    5. Functionality to do Insertions / deletions can be easily added and updates would require updating/rebuilding partial indices as well - Assumption 1
    6. How does search work with multiple constrains? example: search for users who have a tag "Springville", in locale "en-AU", in timezone "Italy"? - Assumption 2

#### Assumptions

    0. "_id" field in each of Users, Organizations and Tickets is unique, each of these entities have an id and id is treated as primary key
    1. All the data is loaded at the beginning
    2. We can only search using one search term at a time
    3. Structure of users, organisation and tickets remain the same as the ones given in spec data files and  remain uniform through out in a file - unseen structures that are even further nested are not dealt with - but missing keys is dealt with
    4. The only mandatory field we need in these entities is just the "_id". Missing id's result in `PrimaryKeyNotFoundError`
    5. Data files should be a list of data points - list of dictionaries. Throws an error otherwise
    6. Values of fields in users, organisations and tickets are hashable

#### Trade offs

    1. Must need to traverse the entire data while building indices
    2. More memory required as multiple indices are kept in memory
    3. Fields with Unhashable values can't be indexed
    4. collisions in `dict()` (indices)
    5. Still might result in O(n) complexity when a search query matches the entire dataset

#### Alternative / Off the shelf Approaches

- Load everything into a pandas dataframe and use pandas [internals](https://stackoverflow.com/a/49937318/6318316) to query/search
- Maybe SQL Lite given it's [performance benchmark](https://blog.thedataincubator.com/2018/05/sqlite-vs-pandas-performance-benchmarks/)
- Lucene index based datastore like elastic search

-------------------------------------

### More Info

#### Modules / Classes
 - [`zensearch.entity_engine.Entity`](./zensearch/entity_engine.py) - base class for entities (users/tickets/organziations) that holds data, manages indices and handles Entity level search
 - [`zesearch.ZendeskSearch.py`](./zensearch/zensearch.py) - class that handles/orchestrates multiple (all) entities `Entity()` that handles search for related matches among entities, searchable fields etc..
 - [`zendesk.cli.py`](./zensearch/cli.py) - class that handles command line interfaces for the application, that takes/processes user input, asks `ZendeskSearch` for results, formats and outputs them
 - [`main.py`](./main.py) - entrypoint for the command line interface
 - [`zensearch.exceptions`](./zensearch/exceptions.py) - custom exceptions for the application
 - [`zensearch.config`](./zensearch/config.py) - configuration for the application, that hardcodes prompt messages, relationships between entities etc..

#### Test Coverage

[About 100% coverage](./docs/test_coverage/index.html)

#### Performance

[Not so scientific analysis](./Performance.ipynb)
1. `CLI.run()` - with user selection (patched in the analysis) and output to stdout
    <sub>(print statements in CLI have overwhelmed jupyter)</sub>
    | Description                |     10000 users     | Spec Data (75 users) |
    | -------------------------- | :-----------------: | -------------------: |
    | Instantiation/Data Load    |        324ms        |               9.55ms |
    | Number of Matches == 10000 | jupyter overwhelmed |                277ms |
    | Number of Matches == 1     |       3.08ms        |               3.48ms |
    
   
2. `ZendeskSearch().get_all_matches()` - that's used by `CLI.run()` under the hood - it returns a generator so I have added a `list()` on top of it to execute it and get accurate times
    <sub>(doesn't print results - print statements are a huge bottleneck!)</sub>
    | Description             | 10000 (10000 users) | Spec Data (75 users) |
    | ----------------------- | :-----------------: | -------------------: |
    | Instantiation/Data Load |        326ms        |                9.5ms |
    | Matches == 10000        |        229ms        |               5.05ms |
    | Matches == 1            |       47.2 µs       |              49.2 µs |

For a more fine grained analysis I have run the [`cProfiler`](./profiler_scripty.py) (and optimized some parts of the code - like using `usjon` instead of `deepcopy` etc.). Links to pstats objects are below:
1. [Pstats for `CLI.run()` with 10000 users and a search query that matches all of them ](./docs/performance/pstats_cli_run_10000)  
2. [Pstats for `CLI.run()` with 75 users and a search query that matches all of them](./docs/performance/pstats_cli_run_75)
3. [Pstats for `list(ZendeskSearch.get_all_matches())` with 10000 users and a search query that matches all of them](./docs/performance/pstats_zendesksearch_10000)
4. [Pstats for `list(ZendeskSearch.get_all_matches())` with 75 users and a search query that matches all of them](./docs/performance/pstats_zendesksearch_75)
--------------------------------------------------------------

### Repo

Repo structure

```
•••• tree -L 2
.
├── Dockerfile                          <--- Dockerfile with various target for prod, testing, security etc...
├── Performance.ipynb                   <---  not so scientific perfomance analysis in a jupyter notebook for easy readability
├── Pipfile                             <--- Pipfile that packages requirements - used in docker
├── Pipfile.lock                        <--- Pipfile locked
├── README.md                           <--- This file
├── cp_data_test_data.py                <--- util script that copies data from ./data to ./tests/test_data
├── data                                <--- base data dir
│   ├── gen                             <--- dir to host generated/random files that were used in performance anaylsis
│   ├── import                          <--- data import from specs, this is loaded by default in main when no other arg is given
│   └── out                             <--- data dir to host stuff that's generated
├── dev                                 <--- utility scripts used during dev
│   ├── test.sh                         <--- runs pytest with opinionated options
│   └── watch_dir.sh                    <--- watches ../zensearch dir for file updates and automaticall triggers ./tesh.sh
├── docs                                <--- documentation, performance reports, coverage reports etc
│   ├── performance                     <--- performance pstats recorded by running ../../profiler_scripty.py
│   ├── test_coverage                   <--- test coverage reports
│   
├── main.py                             <--- main file to start/run the app
├── profiler_scripty.py                 <--- hacky script used in performance analysis 
├── requirements-dev.txt                <--- requirements for developing in this repo
├── requirements.txt                    <--- requirments for running stuff in this repo
├── specs                               <--- specifications given
│   ├── Zendesk_Coding_Challenge.pdf
│   ├── organizations.json
│   ├── tickets.json
│   └── users.json
├── tests                               <--- tests for zensearch
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_data
│   ├── test_entity_engine.py
│   ├── test_entity_exceptions.py
│   ├── test_main.py
│   ├── test_utils.py
│   └── test_zensearch.py
└── zensearch                           <--- source code for zendesk
    ├── __init__.py                     <--- empty init for proper imports
    ├── cli.py                          <--- module for cli abstraction that runs/process stuff related to the cli app
    ├── config.py                       <--- hacky config that hardcodes stuff and can be changed for changing output prompts, entity relationships etc
    ├── entity_engine.py                <--- core class that represents an entity (users, organizations and tickets)
    ├── exceptions.py                   <--- custom exceptions in this module
    ├── utils.py                        <--- orpham utility functions that are used
    └── zensearch.py                    <--- module that's an abstraction on top of entities and orchestrates, manages them and search
```
