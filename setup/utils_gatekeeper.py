def get_extern_flask_app(info):
    """
    Dynamically creates the script for the flask application used on the web facing instance (entry point to our system)

    Parameters:
    - info: Dictionnary containing all the information about our instances (see data.json).
    """
    flask_file = f'''from flask import Flask, render_template, request
import requests


app = Flask(__name__)

dest_url = 'http://{info['proxy']['public_dns']}:5000/query'

# Route for the 'read' page
@app.route('/read', methods=['GET', 'POST'])
def read():
    if request.method == 'POST':
        text = request.form['text']
        option = request.form.get('search_option', 'direct-hit')

        payload = dict()
        payload['query'] = text
        payload['mode'] = option

        response = requests.post(dest_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if 'result' in result: result=result['result']
        else:
            result= 'Error:' + response.text

        return render_template('result.html', result=result)

    return render_template('read.html')

# Route for the 'write' page
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        text = request.form['text']

        payload = dict()
        payload['query'] = text
        payload['mode'] = 'write'

        response = requests.post(dest_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if 'result' in result: result=result['result']
        else:
            result= 'Error:' + response.text

        return render_template('result.html', result=result)
    return render_template('write.html')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)'''
    return flask_file