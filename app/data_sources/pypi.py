import requests
import os
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL
PYPI_API_URL = os.getenv('PYPI_API_URL', 'https://pypi.org/pypi')

def search_libraries(keyword, max_results=100):
    """
    Search for Python libraries using PyPI API
    
    Args:
        keyword (str): Search keyword
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of library data dictionaries
    """
    libraries = []
    
    try:
        # Use PyPI Search API
        search_url = f"https://pypi.org/search/?q={keyword}&c=Programming+Language+%3A%3A+Python"
        
        # Use the JSON API for each package found
        # This is a simplified approach - in production, we would parse the search results page
        # For demonstration, we'll use some predefined AI libraries
        if 'ai' in keyword.lower() or 'machine learning' in keyword.lower():
            packages = [
                'tensorflow', 'pytorch', 'transformers', 'huggingface-hub', 'scikit-learn', 
                'keras', 'nltk', 'spacy', 'gensim', 'openai', 'langchain', 
                'sentence-transformers', 'torchvision', 'opencv-python', 'fastai',
                'llama-cpp-python', 'diffusers', 'stable-diffusion', 'autogpt'
            ]
        elif 'nlp' in keyword.lower():
            packages = [
                'nltk', 'spacy', 'gensim', 'transformers', 'bert-pytorch', 
                'allennlp', 'stanza', 'flair', 'textblob', 'langchain'
            ]
        elif 'computer vision' in keyword.lower():
            packages = [
                'opencv-python', 'pillow', 'torchvision', 'detectron2', 'imageai',
                'albumentations', 'imgaug', 'kornia', 'scikit-image', 'diffusers'
            ]
        else:
            packages = [
                'tensorflow', 'pytorch', 'scikit-learn', 'keras', 'torch', 
                'pandas', 'numpy', 'matplotlib', 'scipy', 'statsmodels'
            ]
        
        # Limit the number of packages to process
        packages = packages[:max_results]
        
        for package_name in packages:
            # Avoid too many requests in short time
            time.sleep(0.5)
            
            try:
                # Get package data from PyPI
                package_url = f"{PYPI_API_URL}/{package_name}/json"
                response = requests.get(package_url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract relevant information
                    info = data.get('info', {})
                    
                    # Parse release date
                    release_date = None
                    if 'release_date' in info:
                        try:
                            release_date = datetime.strptime(info['release_date'], '%Y-%m-%dT%H:%M:%S')
                        except:
                            pass
                    
                    # Extract GitHub repository URL if available
                    repository_url = ''
                    if 'project_urls' in info and info['project_urls']:
                        for key in ['Source', 'Homepage', 'Repository']:
                            if key in info['project_urls'] and 'github.com' in info['project_urls'][key]:
                                repository_url = info['project_urls'][key]
                                break
                    
                    # Extract documentation URL if available
                    documentation_url = ''
                    if 'project_urls' in info and info['project_urls']:
                        for key in ['Documentation', 'Docs', 'Homepage']:
                            if key in info['project_urls'] and info['project_urls'][key]:
                                documentation_url = info['project_urls'][key]
                                break
                    
                    # Determine categories based on keywords
                    categories = []
                    if 'keywords' in info and info['keywords']:
                        keywords = [k.strip().lower() for k in info['keywords'].split(',')]
                        
                        # Map keywords to categories
                        keyword_to_category = {
                            'nlp': 'Natural Language Processing',
                            'natural language': 'Natural Language Processing',
                            'text': 'Natural Language Processing',
                            'machine learning': 'Machine Learning',
                            'deep learning': 'Deep Learning',
                            'neural': 'Neural Networks',
                            'ai': 'Artificial Intelligence',
                            'vision': 'Computer Vision',
                            'image': 'Computer Vision',
                            'video': 'Computer Vision',
                            'voice': 'Speech Processing',
                            'speech': 'Speech Processing',
                            'audio': 'Speech Processing',
                            'reinforcement': 'Reinforcement Learning',
                            'rl': 'Reinforcement Learning',
                            'generation': 'Generative AI',
                            'generative': 'Generative AI',
                            'llm': 'Large Language Models',
                            'language model': 'Large Language Models'
                        }
                        
                        for keyword in keywords:
                            for key, category in keyword_to_category.items():
                                if key in keyword:
                                    categories.append(category)
                    
                    # Get download statistics - this is simplified
                    # In production, we would use the PyPI Stats API or BigQuery dataset
                    monthly_downloads = 0
                    
                    # Create library data dictionary
                    library_data = {
                        'name': info.get('name', package_name),
                        'description': info.get('summary', ''),
                        'version': info.get('version', ''),
                        'last_update': release_date or datetime.now(),
                        'repository_url': repository_url,
                        'documentation_url': documentation_url,
                        'package_url': info.get('package_url', f"https://pypi.org/project/{package_name}/"),
                        'downloads': monthly_downloads,
                        'categories': list(set(categories)) if categories else ['Artificial Intelligence']
                    }
                    
                    libraries.append(library_data)
                    logger.info(f"Collected data for Python package: {package_name}")
                
                else:
                    logger.warning(f"Failed to get data for package {package_name}. Status code: {response.status_code}")
            
            except Exception as e:
                logger.error(f"Error processing package {package_name}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error searching Python libraries: {str(e)}")
    
    return libraries

def get_package_details(package_name):
    """
    Get detailed information about a specific Python package
    
    Args:
        package_name (str): Name of the package
        
    Returns:
        dict: Package details
    """
    try:
        package_url = f"{PYPI_API_URL}/{package_name}/json"
        response = requests.get(package_url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process and return the data
            info = data.get('info', {})
            releases = data.get('releases', {})
            
            # Get version history
            versions = []
            for version, release_data in releases.items():
                if release_data:
                    upload_time = release_data[0].get('upload_time')
                    versions.append({
                        'version': version,
                        'release_date': upload_time
                    })
            
            return {
                'name': info.get('name', package_name),
                'description': info.get('summary', ''),
                'author': info.get('author', ''),
                'author_email': info.get('author_email', ''),
                'version': info.get('version', ''),
                'homepage': info.get('home_page', ''),
                'license': info.get('license', ''),
                'versions': versions
            }
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting details for package {package_name}: {str(e)}")
        return None 