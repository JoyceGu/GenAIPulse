import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    """
    Application factory function to create and configure the Flask app
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///genai_pulse.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables and add sample data
    with app.app_context():
        from app.models import Library, Category, Version, library_categories
        
        db.create_all()
        
        # Add sample data if database is empty
        if Category.query.count() == 0:
            create_sample_data()
    
    # Add Jinja template filters
    @app.template_filter('now')
    def _jinja2_filter_now(format_str):
        """Return formatted datetime string for current time"""
        from datetime import datetime
        return datetime.now().strftime(format_str)
    
    @app.template_filter('tojson')
    def _tojson_filter(obj):
        """Convert object to JSON string"""
        return json.dumps(obj)
    
    return app

def create_sample_data():
    """Create sample data for the application"""
    from app.models import Library, Category, Version, library_categories
    from datetime import datetime, timedelta
    import random
    
    # Create categories
    categories = {
        'ai': Category(name='Artificial Intelligence', category_type='domain'),
        'ml': Category(name='Machine Learning', category_type='functionality'),
        'dl': Category(name='Deep Learning', category_type='functionality'),
        'nlp': Category(name='Natural Language Processing', category_type='functionality'),
        'cv': Category(name='Computer Vision', category_type='functionality'),
        'sp': Category(name='Speech Processing', category_type='functionality'),
        'rl': Category(name='Reinforcement Learning', category_type='functionality'),
        'gen': Category(name='Generative AI', category_type='functionality'),
        'llm': Category(name='Large Language Models', category_type='application'),
        'nn': Category(name='Neural Networks', category_type='functionality')
    }
    
    for category in categories.values():
        db.session.add(category)
    
    # Commit categories to get IDs
    db.session.commit()
    
    # Sample libraries for each language
    libraries = [
        # Python libraries
        {
            'name': 'TensorFlow',
            'description': 'An open-source machine learning framework for everyone',
            'language': 'Python',
            'current_version': '2.10.0',
            'last_update': datetime.now() - timedelta(days=30),
            'repository_url': 'https://github.com/tensorflow/tensorflow',
            'documentation_url': 'https://www.tensorflow.org/api_docs',
            'package_url': 'https://pypi.org/project/tensorflow/',
            'popularity_score': 95.0,
            'github_stars': 170000,
            'monthly_downloads': 5000000,
            'categories': ['ai', 'ml', 'dl', 'nn']
        },
        {
            'name': 'PyTorch',
            'description': 'Tensors and Dynamic neural networks in Python with strong GPU acceleration',
            'language': 'Python',
            'current_version': '1.13.0',
            'last_update': datetime.now() - timedelta(days=15),
            'repository_url': 'https://github.com/pytorch/pytorch',
            'documentation_url': 'https://pytorch.org/docs/stable/index.html',
            'package_url': 'https://pypi.org/project/torch/',
            'popularity_score': 92.0,
            'github_stars': 62000,
            'monthly_downloads': 3000000,
            'categories': ['ai', 'ml', 'dl', 'nn']
        },
        {
            'name': 'Transformers',
            'description': 'State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX',
            'language': 'Python',
            'current_version': '4.24.0',
            'last_update': datetime.now() - timedelta(days=5),
            'repository_url': 'https://github.com/huggingface/transformers',
            'documentation_url': 'https://huggingface.co/docs/transformers/index',
            'package_url': 'https://pypi.org/project/transformers/',
            'popularity_score': 90.0,
            'github_stars': 75000,
            'monthly_downloads': 2500000,
            'categories': ['ai', 'ml', 'nlp', 'llm']
        },
        {
            'name': 'LangChain',
            'description': 'Building applications with LLMs through composability',
            'language': 'Python',
            'current_version': '0.0.150',
            'last_update': datetime.now() - timedelta(days=2),
            'repository_url': 'https://github.com/langchain-ai/langchain',
            'documentation_url': 'https://python.langchain.com/docs/get_started/introduction',
            'package_url': 'https://pypi.org/project/langchain/',
            'popularity_score': 88.0,
            'github_stars': 45000,
            'monthly_downloads': 1500000,
            'categories': ['ai', 'nlp', 'llm', 'gen']
        },
        
        # JavaScript libraries
        {
            'name': 'TensorFlow.js',
            'description': 'A JavaScript library for training and deploying ML models in the browser and on Node.js',
            'language': 'JavaScript',
            'current_version': '4.0.0',
            'last_update': datetime.now() - timedelta(days=45),
            'repository_url': 'https://github.com/tensorflow/tfjs',
            'documentation_url': 'https://www.tensorflow.org/js/guide',
            'package_url': 'https://www.npmjs.com/package/@tensorflow/tfjs',
            'popularity_score': 85.0,
            'github_stars': 17000,
            'monthly_downloads': 500000,
            'categories': ['ai', 'ml', 'dl', 'nn']
        },
        {
            'name': 'Brain.js',
            'description': 'Neural networks in JavaScript',
            'language': 'JavaScript',
            'current_version': '2.0.0',
            'last_update': datetime.now() - timedelta(days=120),
            'repository_url': 'https://github.com/BrainJS/brain.js',
            'documentation_url': 'https://brain.js.org/',
            'package_url': 'https://www.npmjs.com/package/brain.js',
            'popularity_score': 75.0,
            'github_stars': 13000,
            'monthly_downloads': 200000,
            'categories': ['ai', 'ml', 'nn']
        },
        {
            'name': 'LangChain.js',
            'description': 'JavaScript version of LangChain framework for LLM applications',
            'language': 'JavaScript',
            'current_version': '0.0.52',
            'last_update': datetime.now() - timedelta(days=3),
            'repository_url': 'https://github.com/langchain-ai/langchainjs',
            'documentation_url': 'https://js.langchain.com/docs/',
            'package_url': 'https://www.npmjs.com/package/langchain',
            'popularity_score': 82.0,
            'github_stars': 5000,
            'monthly_downloads': 300000,
            'categories': ['ai', 'nlp', 'llm', 'gen']
        },
        
        # .NET libraries
        {
            'name': 'ML.NET',
            'description': 'Cross-platform machine learning framework for .NET',
            'language': '.NET',
            'current_version': '1.7.1',
            'last_update': datetime.now() - timedelta(days=90),
            'repository_url': 'https://github.com/dotnet/machinelearning',
            'documentation_url': 'https://learn.microsoft.com/en-us/dotnet/machine-learning/',
            'package_url': 'https://www.nuget.org/packages/Microsoft.ML/',
            'popularity_score': 78.0,
            'github_stars': 8000,
            'monthly_downloads': 100000,
            'categories': ['ai', 'ml']
        },
        {
            'name': 'TensorFlow.NET',
            'description': 'TensorFlow binding for .NET',
            'language': '.NET',
            'current_version': '0.70.1',
            'last_update': datetime.now() - timedelta(days=60),
            'repository_url': 'https://github.com/SciSharp/TensorFlow.NET',
            'documentation_url': 'https://scisharp.github.io/TensorFlow.NET/',
            'package_url': 'https://www.nuget.org/packages/TensorFlow.NET/',
            'popularity_score': 70.0,
            'github_stars': 3000,
            'monthly_downloads': 50000,
            'categories': ['ai', 'ml', 'dl', 'nn']
        },
        
        # Java libraries
        {
            'name': 'DL4J',
            'description': 'Deep Learning for Java, scientific computing and neural networks',
            'language': 'Java',
            'current_version': '1.0.0-M2.1',
            'last_update': datetime.now() - timedelta(days=180),
            'repository_url': 'https://github.com/deeplearning4j/deeplearning4j',
            'documentation_url': 'https://deeplearning4j.konduit.ai/',
            'package_url': 'https://search.maven.org/artifact/org.deeplearning4j/deeplearning4j-core',
            'popularity_score': 72.0,
            'github_stars': 12000,
            'monthly_downloads': 80000,
            'categories': ['ai', 'ml', 'dl', 'nn']
        },
        {
            'name': 'DJL',
            'description': 'Deep Java Library - An Engine-Agnostic Deep Learning Framework',
            'language': 'Java',
            'current_version': '0.18.0',
            'last_update': datetime.now() - timedelta(days=45),
            'repository_url': 'https://github.com/deepjavalibrary/djl',
            'documentation_url': 'https://djl.ai/docs/jupyter/index.html',
            'package_url': 'https://search.maven.org/artifact/ai.djl/api',
            'popularity_score': 68.0,
            'github_stars': 3000,
            'monthly_downloads': 40000,
            'categories': ['ai', 'ml', 'dl']
        }
    ]
    
    # Add libraries and associate with categories
    for lib_data in libraries:
        lib = Library(
            name=lib_data['name'],
            description=lib_data['description'],
            language=lib_data['language'],
            current_version=lib_data['current_version'],
            last_update=lib_data['last_update'],
            repository_url=lib_data['repository_url'],
            documentation_url=lib_data['documentation_url'],
            package_url=lib_data['package_url'],
            popularity_score=lib_data['popularity_score'],
            github_stars=lib_data['github_stars'],
            monthly_downloads=lib_data['monthly_downloads']
        )
        
        # Add library to database to get ID
        db.session.add(lib)
        db.session.flush()
        
        # Associate with categories
        for cat_key in lib_data['categories']:
            if cat_key in categories:
                lib.categories.append(categories[cat_key])
        
        # Add version history
        for i in range(3):
            version_num = '.'.join(lib_data['current_version'].split('.')[:2]) + '.' + str(i)
            release_date = lib_data['last_update'] - timedelta(days=30 * (3-i))
            
            version = Version(
                library_id=lib.id,
                version_number=version_num,
                release_date=release_date,
                release_notes=f"Version {version_num} release with improvements and bug fixes."
            )
            db.session.add(version)
    
    # Commit all changes
    db.session.commit() 