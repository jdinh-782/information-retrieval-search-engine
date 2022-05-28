from flask import Flask, render_template, request, flash, redirect, json
from nltk.stem import PorterStemmer
import time
import ast


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs121searchengine7813'  # should be some random long string

stemmer = PorterStemmer()

print("Loading files...")

positions = open('position.txt')
offsets = json.load(positions)
ind = open('index.txt')
file = open("docIDs.txt")
data_file = json.load(file)
with open("index.txt", 'r') as index_file:
    index_data = index_file.readlines()

print("\nFiles loaded")


def search_input(user_input):
    start = time.time()
    user_input = user_input.split()

    # stem each word in user query
    for i in range(len(user_input)):
        user_input[i] = stemmer.stem(user_input[i])

    # check if index file can be loaded (problems reading TextIO)
    load_data = True
    data = {}
    try:
        ind.seek(offsets[user_input[0]])
        entry = ind.readline()
        json.loads(entry)
    except ValueError:
        load_data = False

    words = {}
    query_dict = {}

    for token in user_input:
        if token not in offsets:
            continue

        if load_data:
            ind.seek(offsets[user_input[0]])
            entry = ind.readline()
            data = json.loads(entry)
        else:
            token_string = '"' + str(token) + '"'

            for i, s in enumerate(index_data):
                if token_string in s:
                    posting = ast.literal_eval(index_data[i])
                    data.update(posting)
                    break

    for token in user_input:
        for i in data:
            query_dict.update({i: data[i]})
        words[token] = len(data[token])

    words = sorted(words.items(), key=lambda x: x[1])

    word_list = []
    for key, value in words:
        word_list.append(key)

    # find all docIDs of each stemmed token in input query
    docID_list = []

    for token in word_list:
        if token == word_list[0]:
            extract_docIDs = query_dict[token]
            count = 0
            extract_docIDs = sorted(extract_docIDs, key=lambda x: x[1], reverse=True)
            for docID in extract_docIDs:
                docID_list.append(extract_docIDs[count][0])
                count += 1
            continue
        new_docID_list = []
        docIDs = query_dict[token]
        count = 0
        docIDs = (sorted(docIDs, key=lambda x: x[1], reverse=True))
        for docID in docIDs:
            if docIDs[count][0] in docID_list:
                new_docID_list.append(docIDs[count][0])
            if len(new_docID_list) == 6:
                docID_list = new_docID_list
                break
            count += 1
        if new_docID_list:
            docID_list = new_docID_list

    dictionary = {}
    count = 0
    for docID in docID_list:
        if count >= 5:
            break
        file_path = data_file[str(docID)]
        dictionary[docID] = file_path
        count += 1

    print("\n--- %s seconds ---" % (time.time() - start))

    top_5_urls = []
    for count, value in enumerate(dictionary):
        print("\n" + str(count + 1) + ". " + dictionary[value])
        top_5_urls.append(dictionary[value])
        if count == 4:
            print('\n')
            break

    return top_5_urls


@app.route('/about.html')
def about_page():
    return render_template("about.html")

@app.route('/feedback.html')
def contact_page():
    return render_template("feedback.html")

# home page
@app.route('/', methods=["GET", "POST"])
def main():
    user_input = request.args.get("search_box")

    if user_input is None:
        user_input = "cristina lopes"  # default value
    else:
        if user_input == "":
            flash("Could not find search input in database. Please provide at least 1 character!")
            return redirect("/")

    urls = search_input(user_input)
    print(user_input)
    print(urls)

    if not urls:
        flash("Could not find any urls for search input, try again!")
        return redirect("/")


    return render_template("index.html", user_input=user_input, urls=urls)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port='8000', debug=True)