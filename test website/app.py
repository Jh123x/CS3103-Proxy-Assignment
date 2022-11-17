from flask import Flask, request, send_from_directory
import time

app = Flask(__name__)


@app.route('/')
def index():
    return '''<div>
    Hello World!
    <form action='/' method='post'>
        <input type="text" name="input" placeholder="input">
        <button type="submit" >Submit</button>
    </form>
    <ol>
        <li>main page also supports delete, put and patch methods</li>
        <li><a href='/img'>Load Image from b64</a></li>
        <li><a href='/img_src'>Load Image from source</a></li>
        <li><a href='/iframe'>Loads an iframe with an image</a></li>
        <li><a href='/time?seconds=1'>Loads the page after 1 second</a></li>
        <li><a href='/time?seconds=5'>Loads the page after 5 seconds</a></li>
        <li><a href='/time?seconds=10'>Loads the page after 10 seconds</a></li>
        <li><a href='/time?seconds=20'>Loads the page after 20 seconds</a></li>
    </ol>
    </div>'''


@app.route('/', methods=['POST'])
def form():
    f = request.form
    return f


@app.route('/', methods=['DELETE'])
def delete():
    return 'delete'


@app.route('/', methods=['PUT'])
def put():
    return 'put'


@app.route('/', methods=['PATCH'])
def patch():
    return 'patch'


@app.route('/img', methods=['GET'])
def img():
    return '''<div>
  <p>Taken from wikpedia</p>
  <img src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUA
    AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
        9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot" />
</div>'''


@app.route('/img_src', methods=["GET"])
def img_src():
    return '''<div>
  <p>Taken from wikpedia</p>
  <img src="/static/img1.jpg" alt="Red dot" />'''


@app.route('/iframe', methods=["GET"])
def frame():
    return '''Iframe<div><iframe src="/img_src" width="100%" height="98%"></iframe></div>'''


@app.route('/time', methods=['GET'])
def timeout_url():
    seconds = 0
    try:
        seconds = int(request.args['seconds'])
    except Exception:
        pass
    time.sleep(seconds)
    return "Done after {} seconds".format(seconds)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
