from service.app import create_app


uxtracking_app = create_app(environment="development")

if __name__ == "__main__":
    uxtracking_app.run()
