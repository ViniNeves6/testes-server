from app import create_app, app

if __name__ == "__main__": 
    app = create_app('dev')
    app.run(debug=True)