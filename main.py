from app import create_app
from flask_sqlalchemy import SQLAlchemy

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)