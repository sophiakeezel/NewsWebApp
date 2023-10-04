from flask import Flask, render_template
app = Flask(__name__)

posts = [
    {
        'author' : 'Sophia Keezel',
        'title' : 'News Post 1',
        'content': 'First post content',
        'date_posted': 'October 4th, 2023'
    }
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)

