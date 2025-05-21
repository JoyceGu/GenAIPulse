from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
import logging
from datetime import datetime
from app import db
from app.models import Library, Category, Version
from app.data_sources import pypi, npm, nuget, maven, github

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_scheduler(app):
    """Initialize the scheduler with all data collection jobs"""
    with app.app_context():
        scheduler = BackgroundScheduler()
        
        # Add jobs
        scheduler.add_job(
            func=collect_python_libraries,
            trigger=IntervalTrigger(hours=24),
            id='python_libraries_job',
            name='Collect Python Libraries',
            replace_existing=True
        )
        
        scheduler.add_job(
            func=collect_javascript_libraries,
            trigger=IntervalTrigger(hours=24),
            id='javascript_libraries_job',
            name='Collect JavaScript Libraries',
            replace_existing=True
        )
        
        scheduler.add_job(
            func=collect_dotnet_libraries,
            trigger=IntervalTrigger(hours=24),
            id='dotnet_libraries_job',
            name='Collect .NET Libraries',
            replace_existing=True
        )
        
        scheduler.add_job(
            func=collect_java_libraries,
            trigger=IntervalTrigger(hours=24),
            id='java_libraries_job',
            name='Collect Java Libraries',
            replace_existing=True
        )
        
        scheduler.add_job(
            func=update_github_data,
            trigger=IntervalTrigger(hours=12),
            id='github_data_job',
            name='Update GitHub Data',
            replace_existing=True
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Scheduler started!")
        
        return scheduler

def collect_python_libraries():
    """Collect AI-related Python libraries from PyPI"""
    logger.info("Collecting Python libraries...")
    
    try:
        # Keywords to search for AI-related packages
        keywords = ['ai', 'machine learning', 'deep learning', 'neural network', 
                   'nlp', 'computer vision', 'generative ai', 'llm']
        
        libraries = []
        for keyword in keywords:
            libraries.extend(pypi.search_libraries(keyword))
        
        # Process and store the libraries
        save_libraries(libraries, 'Python')
        
        logger.info(f"Successfully collected {len(libraries)} Python libraries")
    
    except Exception as e:
        logger.error(f"Error collecting Python libraries: {str(e)}")

def collect_javascript_libraries():
    """Collect AI-related JavaScript libraries from npm"""
    logger.info("Collecting JavaScript libraries...")
    
    try:
        # Keywords to search for AI-related packages
        keywords = ['ai', 'machine-learning', 'deep-learning', 'neural-network', 
                   'nlp', 'computer-vision', 'generative-ai', 'llm']
        
        libraries = []
        for keyword in keywords:
            libraries.extend(npm.search_libraries(keyword))
        
        # Process and store the libraries
        save_libraries(libraries, 'JavaScript')
        
        logger.info(f"Successfully collected {len(libraries)} JavaScript libraries")
    
    except Exception as e:
        logger.error(f"Error collecting JavaScript libraries: {str(e)}")

def collect_dotnet_libraries():
    """Collect AI-related .NET libraries from NuGet"""
    logger.info("Collecting .NET libraries...")
    
    try:
        # Keywords to search for AI-related packages
        keywords = ['ai', 'machine learning', 'deep learning', 'neural network', 
                   'nlp', 'computer vision', 'generative ai', 'llm']
        
        libraries = []
        for keyword in keywords:
            libraries.extend(nuget.search_libraries(keyword))
        
        # Process and store the libraries
        save_libraries(libraries, '.NET')
        
        logger.info(f"Successfully collected {len(libraries)} .NET libraries")
    
    except Exception as e:
        logger.error(f"Error collecting .NET libraries: {str(e)}")

def collect_java_libraries():
    """Collect AI-related Java libraries from Maven"""
    logger.info("Collecting Java libraries...")
    
    try:
        # Keywords to search for AI-related packages
        keywords = ['ai', 'machine learning', 'deep learning', 'neural network', 
                   'nlp', 'computer vision', 'generative ai', 'llm']
        
        libraries = []
        for keyword in keywords:
            libraries.extend(maven.search_libraries(keyword))
        
        # Process and store the libraries
        save_libraries(libraries, 'Java')
        
        logger.info(f"Successfully collected {len(libraries)} Java libraries")
    
    except Exception as e:
        logger.error(f"Error collecting Java libraries: {str(e)}")

def update_github_data():
    """Update GitHub data (stars, commits, etc.) for all libraries"""
    logger.info("Updating GitHub data...")
    
    try:
        # Get all libraries with a repository URL containing 'github.com'
        libraries = Library.query.filter(Library.repository_url.ilike('%github.com%')).all()
        
        for library in libraries:
            # Extract owner and repo from the repository URL
            if 'github.com' in library.repository_url:
                parts = library.repository_url.split('github.com/')
                if len(parts) > 1:
                    owner_repo = parts[1].strip('/')
                    owner, repo = owner_repo.split('/') if '/' in owner_repo else (None, None)
                    
                    if owner and repo:
                        # Get GitHub data
                        github_data = github.get_repository_data(owner, repo)
                        
                        if github_data:
                            # Update library data
                            library.github_stars = github_data.get('stars', library.github_stars)
                            
                            # Recalculate popularity score based on downloads and stars
                            library.popularity_score = calculate_popularity_score(
                                library.monthly_downloads, 
                                library.github_stars
                            )
                            
                            db.session.add(library)
        
        db.session.commit()
        logger.info(f"Successfully updated GitHub data for {len(libraries)} libraries")
    
    except Exception as e:
        logger.error(f"Error updating GitHub data: {str(e)}")
        db.session.rollback()

def save_libraries(libraries_data, language):
    """Save or update libraries in the database"""
    try:
        for lib_data in libraries_data:
            # Check if library already exists
            existing_lib = Library.query.filter_by(name=lib_data['name'], language=language).first()
            
            if existing_lib:
                # Update existing library
                existing_lib.description = lib_data.get('description', existing_lib.description)
                existing_lib.current_version = lib_data.get('version', existing_lib.current_version)
                existing_lib.last_update = lib_data.get('last_update', existing_lib.last_update)
                existing_lib.repository_url = lib_data.get('repository_url', existing_lib.repository_url)
                existing_lib.documentation_url = lib_data.get('documentation_url', existing_lib.documentation_url)
                existing_lib.package_url = lib_data.get('package_url', existing_lib.package_url)
                existing_lib.monthly_downloads = lib_data.get('downloads', existing_lib.monthly_downloads)
                
                # Update popularity score
                existing_lib.popularity_score = calculate_popularity_score(
                    existing_lib.monthly_downloads,
                    existing_lib.github_stars
                )
                
                # Add new version if it's different
                if existing_lib.current_version != lib_data.get('version') and lib_data.get('version'):
                    new_version = Version(
                        library_id=existing_lib.id,
                        version_number=lib_data.get('version'),
                        release_date=lib_data.get('last_update', datetime.utcnow()),
                        release_notes=lib_data.get('release_notes', '')
                    )
                    db.session.add(new_version)
                
                db.session.add(existing_lib)
            
            else:
                # Create new library
                new_lib = Library(
                    name=lib_data['name'],
                    description=lib_data.get('description', ''),
                    language=language,
                    current_version=lib_data.get('version', ''),
                    last_update=lib_data.get('last_update', datetime.utcnow()),
                    repository_url=lib_data.get('repository_url', ''),
                    documentation_url=lib_data.get('documentation_url', ''),
                    package_url=lib_data.get('package_url', ''),
                    monthly_downloads=lib_data.get('downloads', 0),
                    github_stars=0,
                    popularity_score=0.0
                )
                
                db.session.add(new_lib)
                db.session.flush()  # Get the ID
                
                # Add initial version
                if lib_data.get('version'):
                    version = Version(
                        library_id=new_lib.id,
                        version_number=lib_data.get('version'),
                        release_date=lib_data.get('last_update', datetime.utcnow()),
                        release_notes=lib_data.get('release_notes', '')
                    )
                    db.session.add(version)
                
                # Add categories
                if lib_data.get('categories'):
                    for cat_name in lib_data['categories']:
                        # Check if category exists
                        cat = Category.query.filter_by(name=cat_name).first()
                        if not cat:
                            cat = Category(name=cat_name, category_type='functionality')
                            db.session.add(cat)
                            db.session.flush()
                        
                        new_lib.categories.append(cat)
        
        db.session.commit()
    
    except Exception as e:
        logger.error(f"Error saving libraries: {str(e)}")
        db.session.rollback()

def calculate_popularity_score(downloads, stars):
    """Calculate a popularity score based on downloads and GitHub stars"""
    # Normalize and weight the factors
    download_weight = 0.7
    star_weight = 0.3
    
    # Avoid division by zero or negative values
    downloads = max(0, downloads or 0)
    stars = max(0, stars or 0)
    
    # Simple scoring algorithm - can be refined
    # Assuming most popular packages have around 1M downloads and 10K stars
    normalized_downloads = min(1.0, downloads / 1000000)
    normalized_stars = min(1.0, stars / 10000)
    
    score = (normalized_downloads * download_weight) + (normalized_stars * star_weight)
    return score 