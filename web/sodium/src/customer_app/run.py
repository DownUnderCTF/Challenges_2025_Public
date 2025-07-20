from app import create_app, db
import dotenv
dotenv.load_dotenv("./.env")

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
