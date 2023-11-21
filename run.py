from flasknews import create_app, db

app = create_app('default')

# Push an application context
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

