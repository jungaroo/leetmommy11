# Leet Mommy 11

Leet Mommy 11 is a search tool for Rithm's lecture notes. 

Dependencies:
```
python3
```
## To access the hosted version:

leetmommy.herokuapp.com

## To use the command-line tool:
Make a virtual env
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To get the help message:
```
python3 notes_search.py -h
```

How to run a search query on the word `flask-wtf`

```
python3 notes_search.py flask-wtf

```


# API Documentation

## Resource URL (base URL)
```
https://leetmommy.herokuapp.com/
```

| HTTP VERB | URL | Description |
| --- | ---| --- |
| GET | /api/ping/ | Wakes up the heroku servers
| GET | /api/index-search/ | Does an indexed search
| GET | /api/scrape-search/ | Does a search with scraping (deprecated)
| GET | /api/interviewq-search/ | Searches interview questions (deprecated)
---

## GET api/ping/
This route takes no paramters, it just wakes up the heroku server from sleeping.
Once finished, it will return a JSON object :
```
{ status : success }
```

## GET /api/index-search?search={searchwords}&cohort={cohort}
#### URI Parameters
| Name | Input | Required | Type | Description |
| --- | --- | --- | --- | --- |
| search | query | True | string | Space seperated string of search
| cohort | query | False | string | A cohort string. Either 'r11', 'r10', 'r13' etc. Defaults to 'r11'

### Response
If successful parameters are passed: 

Returns a JSON, with property `links`
Which is an array of rithm school links to the documents.

```
{
  links :  [
    'https://somelink.com/asdf',
    'https://anotherlink.com/asdf2',
  ]   
}

```

If there is an Error:
{
  "error": "A key of 'search' is required in the args'"
}

Means you didn't READ THE DOCS

# Deprecated API calls
These search very slowly (does not use an index), but makes asynchronous calls.

## GET /api/scrape-search?search={searchwords}&type={cohort}

#### URI Parameters
| Name | Input | Required | Type | Description |
| --- | --- | --- | --- | --- |
| search | query | True | string | Space seperated string of search
| type | query | True | string | One of ["code_snips", "lecture_pages", "links"]

### Response
If successful parameters are passed: 

Returns a JSON, with property `data`
Which is an JSON object with keys of rithm cohort to of rithm school links to the documents, or strings of the html snippet.

```
{
  data :  {
    "r11": [ "link1", "link2", ],
    "r10": [ "link3", "link4", ]
  } 

}

```

If there is an Error:
{
  "error": "A key of 'search' is required in the args'"
}

Means you didn't READ THE DOCS





