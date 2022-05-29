import json
import os
import time
import nltk
import math
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.stem import PorterStemmer


# check if documents are valid html/json files
# open/read documents
# get text from files
# tokenize text
# merge index (word -> (list of documents containing words))
# ie. ambitious : 1 -> 4 -> 5
# docID will identify the specific document along with keeping track of number of documents
docID = 0
# keep track of token frequency within document
dictionary = defaultdict(list)
# keep track of docID and their urls
file_key = defaultdict(str)

# rootdir will be the root directory path for extracting the json files
rootdir = "developer\DEV"

# initialize Porter Stemmer
stemmer = PorterStemmer()


def index():
    # open files / get text
    global docID
    global dictionary

    file_url = ""

    # list of partial indexes
    partials = []
    count = 0
    doc_count = 0
    n = 0
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            doc_count += 1

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            file_url = os.path.join(subdir, file)

            f = open(file_url)

            # check if file is valid json file
            try:
                data = json.load(f)
            except ValueError as e:
                print(e)
                break

            text = data['content']
            soup = BeautifulSoup(text, features='lxml')

            word_freq = defaultdict(int)
            tokens = tokenize(soup.text)

            # defrag url
            url = data['url'].split('#')
            # add url to docID dict
            file_key[docID] = url[0]

            # stem tokens
            tokens = [stemmer.stem(token) for token in tokens]

            for token in tokens:
                word_freq[token.lower()] += 1

            for word in word_freq:
                # adds (word: (docID, tf-idf)) to dictionary
                dictionary[word].append((docID, word_freq[word]))

            docID += 1
            count += 1

            if count == 5000:  # write to partial index every 10000 documents
                n = len(partials) + 1
                partial_name = writeToDisk(dictionary, n)
                partials.append(partial_name)
                dictionary.clear()
                count = 0

            f.close()

    if len(dictionary) != 0:
        partial_name = writeToDisk(dictionary, n)
        partials.append(partial_name)
        dictionary.clear()
    final_index = MergeIndices(partials)

    with open('index.txt', 'w') as f:
        merged = open(final_index, 'r')
        entry = merged.readline()
        dic = defaultdict(list)
        while entry != "":
            object = json.loads(entry)
            for item in object:
                # calculate tf-idf scores
                doc_freq = len(object[item])
                idf_score = math.log((docID / doc_freq), 10)
                for doc_id, tf_idf in object[item]:
                    tf_idf = tf_idf * idf_score
                    dic[item].append((doc_id, tf_idf))
                # dic[item].sort(key=lambda item: item[1], reverse=True)
            # write each term and its postings to file
            f.write(json.dumps(dic))
            f.write('\n')
            entry = merged.readline()
            dic.clear()
        merged.close()

    # read through final index and create index of index
    index_positions = open('position.txt', 'w')
    positions = dict()
    ind = open('index.txt', 'r')
    line = ind.readline()
    next_position = 0
    while line != "":
        term = json.loads(line)
        for item in term:
            positions[item] = next_position
        next_position += len(line)
        line = ind.readline()
    ind.close()
    index_positions.write(json.dumps(positions))
    index_positions.close()

    # with open('index.txt', 'w', encoding="utf-8") as f:
    # for item in dic:
    # f.write(json.dumps(("{" + "'" + item + "': " + str(dic[item]) + "}")))
    # f.write('\n')

    # write docIDs and urls to a txt file
    with open('docIDs.txt', 'w') as f:
        f.write(json.dumps(file_key))


# tokenize words with apostrophes as 2 tokens (ie. "isn" and "t")
def tokenize(text):
    #   result = re.split("[^a-zA-Z0-9]", text)
    #   result = list(filter(None, result))
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    result = tokenizer.tokenize(text)
    return result


def writeToDisk(freq: dict, num: int) -> str:
    index_name = 'partial' + str(num) + '.txt'
    with open(index_name, 'w', encoding="utf-8") as i:
        for key in sorted(freq.keys()):
            new_dic = {key: freq[key]}
            i.write(json.dumps(new_dic))
            i.write('\n')
    i.close()
    return index_name


def MergeIndices(indexes: list) -> str:
    # given list of partial indexes, merge them
    start = 1
    while len(indexes) > 1:
        index_1 = indexes.pop(0)
        index_2 = indexes.pop(0)
        merged = MergeTwo(index_1, index_2, start)
        indexes.append(merged)
        start += 1
    return indexes[0]


def MergeTwo(index1, index2, mergenum):
    # binary merge
    # create merge file
    merged_name = 'merged' + str(mergenum) + '.txt'
    merge_file = open(merged_name, 'w')
    # write
    i1 = open(index1, 'r')
    i2 = open(index2, 'r')
    line1 = i1.readline()
    line2 = i2.readline()
    line1 = json.loads(line1)
    line2 = json.loads(line2)

    while line1 != "" and line2 != "":
        term1 = [str(key) for key in line1.keys()][0]
        term2 = [str(key) for key in line2.keys()][0]
        # get terms to compare
        if term1 == term2:
            line1[term1].extend(line2[term2])
            merge_file.write(json.dumps(line1))
            merge_file.write('\n')
            line1 = i1.readline()
            line2 = i2.readline()
            if line1 != "":
                line1 = json.loads(line1)
            if line2 != "":
                line2 = json.loads(line2)
        elif term1 < term2:
            merge_file.write(json.dumps(line1))
            merge_file.write('\n')
            line1 = i1.readline()
            if line1 != "":
                line1 = json.loads(line1)
        else:
            merge_file.write(json.dumps(line2))
            merge_file.write('\n')
            line2 = i2.readline()
            if line2 != "":
                line2 = json.loads(line2)

    if line1 == "":
        i1.close()
        while line2 != "":
            term2 = [str(key) for key in line2.keys()][0]
            merge_file.write(json.dumps(line2))
            merge_file.write('\n')
            line2 = i2.readline()
            if line2 != "":
                line2 = json.loads(line2)
        i2.close()
    elif line2 == "":
        i2.close()
        while line1 != "":
            term1 = [str(key) for key in line1.keys()][0]
            merge_file.write(json.dumps(line1))
            merge_file.write('\n')
            line1 = i1.readline()
            if line1 != "":
                line1 = json.loads(line1)
        i1.close()
    merge_file.close()

    return merged_name


# REPORT:
# number of documents
# number of unique tokens
# size of index in kb on disk
def create_report():
    file_size = float(os.path.getsize("index.txt") / 1000)

    with open("M1_Report.txt", mode="w") as f:
        f.write("\nNumber of indexed documents: " + str(docID))
        f.write("\nNumber of unique tokens: " + str(len(dictionary)))
        f.write("\nSize of index(in KB): " + str(file_size))


def main():
    start = time.time()
    index()
    print("--- %s seconds ---" % (time.time() - start))
    create_report()


if __name__ == "__main__":
    main()
