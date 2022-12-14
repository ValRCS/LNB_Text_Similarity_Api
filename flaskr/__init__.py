# import os

from flask import Flask, jsonify, request, render_template, url_for, escape
import pandas as pd
import numpy as np  
from pathlib import Path
from datetime import datetime
from LatvianStemmer import stem
# http://valoda.ailab.lv/latval/vidusskolai/morfol/lietv-mija.htm
ending_replace_dict = {
    "v": "vj",
    "t": "[tš]",
    "d": "[dž]",
    "c": "[cč]",
    "s": "[sš]",
    "z": "[zž]",
    "n": "[nņ]",
    "l": "[lļ]",
    "sn": "[sn|šņ]",
    "zn": "[zn|žņ]",
    "sl": "[sl|šļ]",
    "zl": "[zl|žļ]",
    "ln": "[ln|ļņ]",
    "kst": "[kst|kš]",
  


}

def load_all_chunks_as_df(pattern='data/tuve*.parquet'):
    df = pd.concat([pd.read_parquet(f) for f in Path().glob(pattern)])
    return df


def find_merge_index(df, term_list=()):
    index_list = []
    for term in term_list:
        iarr = np.where(df.index==term)[0]
        index_list.append(iarr)
    c = np.concatenate(index_list)
    c.sort(kind='mergesort')
    return c

def find_close_indexes(iarr, terms=3, window=5):
    close_list = [(iarr[n],iarr[n+1],iarr[n+2]) for n in range(len(iarr)-terms+1) if (iarr[n+2]-iarr[n]) <= window]
    return close_list

def return_fragment(df, close_index, padding=10):
    beg = close_index[0]
    end = close_index[-1]
    d = {
        "title": df.iloc[beg].fname,
        "text": " ".join(df.iloc[beg-padding:end+padding].form.values),
        "lemma": " ".join(df.iloc[beg-padding:end+padding].lemma.values),
        "upos": " ".join(df.iloc[beg-padding:end+padding].upos.values)
    }
    return d

def return_top_fragments(df, clist, num_frags=5, padding=10, offset=2):
    frag_list = [return_fragment(df, close_index, padding) for close_index in clist[offset:num_frags+offset]]
    return frag_list

def create_pattern(word_tuple, window=100, ending_replace_dict=ending_replace_dict, is_stemmed=False):
    """Create regex pattern from word_tuple and ending_replace_dict"""
    # create pattern from word_tuple
    word_list = list(word_tuple)
    if is_stemmed:
        word_list = [stem(word) for word in word_list]
        word_list = [word[:-1]+ending_replace_dict.get(word[-1], word[-1]) for word in word_list]

    pattern = (".{1," + str(window) + "}").join(word_list)
    return pattern



def find_pattern(df, pattern, verbose=True):
    if verbose:
        print("Will look for Pattern:", pattern)
        start_datetime = datetime.now()
        print("Starting search at:", start_datetime)
        
    found_df = df[df["text"].str.contains(pat=pattern, case=False)]
    if verbose:
        end_datetime = datetime.now()
        print("Found", found_df.shape[0], "rows at:", end_datetime)
        print("Search took:", end_datetime - start_datetime)
    return found_df.index.to_list()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    df = pd.read_parquet('data/lima_lemma_index_20222610.parquet') # FIXME to configurable path
    plaintext_df = load_all_chunks_as_df()

    # app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev', # FIXME: change this to a random value when deploying
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    @app.route('/', methods = ['GET', 'POST'])
    def home():
        if(request.method == 'GET'):
            info = "LNB text similarity API prototype 0.0.3"
            data = "use /search/<name1>/<name2>/<name3> to search for text fragments with the given names"
            return jsonify({'data': data,
                            'info': info})

    @app.route('/search/<t1>/<t2>/<t3>/', methods = ['GET'])
    def disp(t1,t2,t3):
        term_list = [t1,t2,t3]
        iarr = find_merge_index(df, term_list)
        clist = find_close_indexes(iarr)
        frag_list = return_top_fragments(df, clist)
        return jsonify({'search_terms': f"{t1} {t2} {t3}",
        'fragments': frag_list})

    # serve plaintext files
    @app.route('/plaintext/<fname>', methods = ['GET'])
    def plaintext(fname):
        text = plaintext_df.loc[fname,"text"]
        return jsonify({'fname':fname, 'text': text})

    # server plaintext as text/plain
    @app.route('/plaintext/raw/<fname>', methods = ['GET'])
    def plaintext_raw(fname):
        text = plaintext_df.loc[fname,"text"]
        return text


    # highlight all terms in term_list using <mark> tags 
    def highlight_terms(text, term_list,stems=True):
        for term in term_list:
            if stems:
                term = stem(term)
            text = text.replace(term, f"<mark>{term}</mark>")
        return text


    html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}
    def html_escape(text):
        return "".join(html_escape_table.get(c,c) for c in text)

    # serve plaintext as html
    @app.route('/plaintext/html/<fname>', methods = ['GET'])
    def plaintext_html(fname):
        text = plaintext_df.loc[fname,"text"]
        terms = request.args.get('terms')
        term_list = terms.split("_")
        # escape html 
        # text = escape(text) # returns markup 
        text = html_escape(text) # had to use my own function because escape() returns markup

        text = highlight_terms(text, term_list)

        # pass text to jinja template
        return render_template('plaintext.html', text=text, fname=fname)

    # serve search page
    @app.route('/search', methods = ['GET'])
    def search():
        return render_template('search.html')

    # process search results
    @app.route('/search', methods = ['POST'])
    def search_post():
        # get form data
        terms = request.form['terms']
        window = int(request.form['window_size'])
        beg_year = int(request.form['beg_year'])
        end_year = int(request.form['end_year'])
        is_stemmed = bool(request.form.get('is_stemmed'))
        # split terms into list
        term_list = terms.split()

        # create GET arguments from term_list - used for highlighting terms in plaintext
        get_args = "?terms="+ "_".join(term_list)

        # find indexes
        # todo make window adjustable
        search_pattern = create_pattern(term_list, 
            window=window,
            ending_replace_dict=ending_replace_dict,
            is_stemmed=is_stemmed)

        df = plaintext_df
        df_year = df[(df["year"] >= beg_year) & (df["year"] <= end_year)]
        pattern_results = find_pattern(df_year, 
                                        search_pattern,
            verbose=True)
        url_list = [f"/plaintext/html/{fname}" for fname in pattern_results]
        dict_list = [{"url": url, "fname": fname} for url, fname in zip(url_list, pattern_results)]
        return render_template('search.html', 
                dict_list=dict_list, 
                search_pattern=search_pattern, 
                get_args=get_args,
                beg_year=beg_year,
                end_year=end_year)
        
    
    @app.errorhandler(404)
    def page_not_found(e):
    # note that we set the 404 status explicitly
        return jsonify({'info':'valid paths are search/term1/term2/term3'}), 404

    return app