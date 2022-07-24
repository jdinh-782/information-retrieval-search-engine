# Information Retrieval Search Engine
Web-based search engine capable of indexing 10,000+ documents and providing search results based on queries.

## Description
This search engine was created using Python, alongside numerous libraries, to access a plethora of documents and their content. Large amounts of text is scraped and analyzed to pair keywords with documents. Term/Document scoring techniques are utilized for optimizing and narrying down search results. An index is created to store a json dictionary of words and documents for later use with the search engine. The rest of the application is displayed in a [localhost](http://localhost:8000) page. 

## Getting Started
### Dependencies
* Ensure intended browser of use is updated to most recent version. Google Chrome or Mozilla Firefox is preferred.
* Python version is the latest installed.
* pip version is the latest installed.
```
python -m pip install --upgrade pip
```

### Installation
Create a new folder and run the following commands in terminal. <br>
*Please be aware of the file sizes in the ```developer.zip``` file. There are roughly 10,000+ documents with each document having its own unique html content.*
``` 
git clone https://github.com/jdinh-782/information-retrieval-search-engine.git

cd information-retrieval-search-engine 
```

Now that you are inside the main directory, please install the included packages:
```
pip install -r requirements.txt
```

### Execution
Assuming all packages and dependencies are installed correctly, first create the index file by running the ```index.py``` file. <br>
* Please advise that because there are many documents, the index will need to take at least 30 minutes for completion.
* There will be smaller index files downloaded during this process as they are crucial for the search. <br>

```python3 index.py```

<br> Once the index files have been created, you may run the search engine in a local shell for preview of how the search engine works along with its performance. This can be done with the following command: 

```python3 search.py```

<br> Otherwise, you are able to run the application on the web with the following command:

```python3 main.py```

## Help
For any concerns, feel free to reach out by [email](mailto:dinhjd@uci.edu?subject=[GitHub]%20Source%20Han%20Sans).

## Authors and Contributors
[Johnson Dinh](https://www.linkedin.com/in/johnson-dinh/) <br>
Joey Siu <br>
Jocelyn Lam <br>
Sarah Khuu

## Acknowledgements
[Mondego Group, UC Irvine](https://github.com/Mondego)
