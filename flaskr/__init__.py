# import os

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np

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

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False

    df = pd.read_parquet('data/lima_lemma_index_20222610.parquet') # FIXME to configurable path


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
    
    @app.errorhandler(404)
    def page_not_found(e):
    # note that we set the 404 status explicitly
        return jsonify({'info':'valid paths are search/term1/term2/term3'}), 404

    return app