# install flask
# pip install flask


# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request
  
# creating a Flask app
app = Flask(__name__)
  
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
        info = "LNB text similarity API prototype 0.0.3"
        data = "use /search/<name1>/<name2>/<name3> to search for text fragments with the given names"
        return jsonify({'data': data,
                        'info': info})
  
  
# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/search/<t1>/<t2>/<t3>/', methods = ['GET'])
def disp(t1,t2,t3):
  
    return jsonify({
        'search_terms': f"{t1} {t2} {t3}",
        'results': [
            {"domID": "1", "title": "title1", "url": "url1", "snippet": "snippet1"},
            {"domID": "2", "title": "title2", "url": "url2", "snippet": "snippet2"}
        ]   
    })
  


# driver function
if __name__ == '__main__':
  
    app.run(debug = True)