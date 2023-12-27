from flask import Flask, render_template, request

app = Flask(__name__)

# Route for the 'read' page
@app.route('/read', methods=['GET', 'POST'])
def read():
    if request.method == 'POST':
        text = request.form['text']
        option = request.form.get('search_option', 'direct-hit')

        # Implement your logic to send a request to AWS with the provided text and option
        # The result of the request should be stored in the 'result' variable

        # For now, let's assume the result is a placeholder string
        result = f"Request sent to AWS with text: {text}, option: {option}"

        return render_template('result.html', result=result)

    return render_template('read.html')

# Route for the 'write' page
@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        text = request.form['text']

        # Implement your logic to send a request to AWS with the provided text
        # The result of the request should be stored in the 'result' variable

        # For now, let's assume the result is a placeholder string
        result = f"Request sent to AWS with text: {text}"

        return render_template('result.html', result=result)
    return render_template('write.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)