from flask import Flask

app = Flask(__name__)

@app.route('/hello')
def helloWorldHandler():
    return 'Hello World from Flask running on the PI!'
 
app.run(host='127.0.0.1', port= 8090)
