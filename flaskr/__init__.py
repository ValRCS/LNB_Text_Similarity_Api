import os

from flask import Flask, jsonify, request


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
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
    
        return jsonify({
            'search_terms': f"{t1} {t2} {t3}",
            'results': [
                {"domID": "1", "title": "title1", "url": "url1", "snippet": "snippet1"},
                {"domID": "2", "title": "title2", "url": "url2", "snippet": "snippet2"}
            ]   
        })

    @app.errorhandler(404)
    def page_not_found(e):
    # note that we set the 404 status explicitly
        return jsonify({'info':'valid paths are search/term1/term2/term3'}), 404

    return app