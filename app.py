from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Here you could save to a database, send an email, etc.
        return render_template('contact.html', success=True, name=name)
    return render_template('contact.html', success=False)

if __name__ == '__main__':
    app.run(debug=True)