from app import create_app
from app.scheduler import init_scheduler

app = create_app()

if __name__ == '__main__':
    # Initialize the scheduler
    init_scheduler(app)
    # Run the application
    app.run(host='0.0.0.0', port=8001, debug=True) 