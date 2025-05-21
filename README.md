# GenAIPulse

GenAIPulse is a real-time monitoring and visualization platform for GenAI-related libraries and packages across multiple programming languages. It helps developers stay updated with the latest trends, releases, and updates in the GenAI ecosystem.

## Features

- **Comprehensive Monitoring**: Tracks AI-related packages across Python, JavaScript, .NET, and Java
- **Intelligent Categorization**: Classifies libraries by language, functionality, and application scenario
- **Trend Analysis**: Visualizes popularity trends and growth patterns
- **New Releases Alert**: Highlights the latest packages and updates
- **User Customization**: Allows subscribing to specific categories for personalized updates

## Architecture

### Backend

- **Data Collection System**: Scheduled crawlers for package repositories and GitHub
- **Data Processing**: Categorization and trend analysis algorithms
- **API Layer**: RESTful endpoints for frontend consumption

### Frontend

- **Dashboard**: Interactive visualizations of library trends
- **Discovery Page**: Exploring libraries by categories
- **Notification System**: Customizable alerts for new releases

## Data Sources

- **Python**: PyPI, Libraries.io, GitHub
- **JavaScript**: npm Registry, npms.io
- **.NET**: NuGet API
- **Java**: Maven Central Repository
- **General**: HuggingFace, Papers With Code

## Setup & Installation

1. Clone the repository
2. Create and activate virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` file
5. Run the application:
   ```
   python run.py
   ```

## API Documentation

The platform provides several API endpoints for programmatic access to the data:

- `GET /api/libraries` - List all libraries
- `GET /api/libraries/category/{category}` - Filter libraries by category
- `GET /api/trends` - Get popularity trends
- `GET /api/latest` - Get latest releases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 