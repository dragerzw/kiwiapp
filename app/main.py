from app import create_app
from app.config import get_config


def main():
    app_config = get_config("development")
    app = create_app(app_config)
    app.run(debug=True)

if __name__ == "__main__":
    main()
