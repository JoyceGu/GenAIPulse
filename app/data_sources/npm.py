import requests
import os
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL
NPM_API_URL = os.getenv('NPM_API_URL', 'https://registry.npmjs.org')

def search_libraries(keyword, max_results=100):
    """
    Search for JavaScript libraries using npm Registry API
    
    Args:
        keyword (str): Search keyword
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of library data dictionaries
    """
    libraries = []
    
    try:
        # Use npm Registry Search API
        search_url = f"https://registry.npmjs.org/-/v1/search?text={keyword}&size={max_results}"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            data = response.json()
            packages = data.get('objects', [])
            
            # Alternatively, for demonstration purposes, we'll use some predefined AI libraries
            # This is to ensure we get relevant AI libraries regardless of the API response
            if 'ai' in keyword.lower() or 'machine-learning' in keyword.lower():
                predefined_packages = [
                    'tensorflow.js', '@tensorflow/tfjs', 'ml5.js', 'brain.js', 'mind.js',
                    'synaptic', 'compromise', 'natural', 'nlp.js', 'sentiment',
                    'face-api.js', '@teachablemachine/image', '@tensorflow-models/face-landmarks-detection',
                    'langchain', 'langchainjs', 'openai', 'gpt-3-encoder', 'transformers.js',
                    'ml.js', 'webdnn', 'convnetjs', 'deeplearnjs', 'deeplearn'
                ]
                
                # Add these packages to the existing list
                existing_names = [p['package']['name'] for p in packages]
                for package_name in predefined_packages:
                    if package_name not in existing_names and len(packages) < max_results:
                        packages.append({
                            'package': {
                                'name': package_name,
                                'description': f"AI/ML library for JavaScript: {package_name}",
                                'version': 'latest',
                                'links': {
                                    'npm': f"https://www.npmjs.com/package/{package_name}",
                                    'homepage': f"https://www.npmjs.com/package/{package_name}"
                                }
                            },
                            'score': {
                                'final': 0.8
                            }
                        })
            
            for package_data in packages:
                package = package_data.get('package', {})
                name = package.get('name', '')
                
                if not name:
                    continue
                
                # Avoid too many requests in short time
                time.sleep(0.2)
                
                try:
                    # Get detailed package data
                    package_url = f"{NPM_API_URL}/{name}"
                    detailed_response = requests.get(package_url)
                    
                    if detailed_response.status_code == 200:
                        detailed_data = detailed_response.json()
                        
                        # Extract information
                        latest_version = detailed_data.get('dist-tags', {}).get('latest', '')
                        
                        # Get the latest version data
                        version_data = {}
                        if latest_version and 'versions' in detailed_data and latest_version in detailed_data['versions']:
                            version_data = detailed_data['versions'][latest_version]
                        
                        # Parse time data
                        modified_time = None
                        if 'time' in detailed_data and latest_version in detailed_data['time']:
                            try:
                                time_str = detailed_data['time'][latest_version]
                                modified_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                            except:
                                try:
                                    # Try alternative format
                                    modified_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                                except:
                                    pass
                        
                        # Extract repository URL
                        repository_url = ''
                        if 'repository' in version_data:
                            if isinstance(version_data['repository'], dict):
                                repository_url = version_data['repository'].get('url', '')
                            elif isinstance(version_data['repository'], str):
                                repository_url = version_data['repository']
                        
                        # Clean up repository URL
                        if repository_url.startswith('git+'):
                            repository_url = repository_url[4:]
                        if repository_url.startswith('git:'):
                            repository_url = 'https:' + repository_url[4:]
                        if repository_url.endswith('.git'):
                            repository_url = repository_url[:-4]
                        
                        # Extract homepage/documentation URL
                        homepage_url = version_data.get('homepage', '')
                        
                        # Determine categories based on keywords
                        categories = []
                        keywords = version_data.get('keywords', [])
                        
                        if keywords:
                            # Map keywords to categories
                            keyword_to_category = {
                                'nlp': 'Natural Language Processing',
                                'natural-language': 'Natural Language Processing',
                                'text': 'Natural Language Processing',
                                'machine-learning': 'Machine Learning',
                                'deep-learning': 'Deep Learning',
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
                                'language-model': 'Large Language Models',
                                'tensorflow': 'Machine Learning',
                                'face': 'Computer Vision',
                                'gpt': 'Large Language Models'
                            }
                            
                            for kw in keywords:
                                kw = kw.lower()
                                for key, category in keyword_to_category.items():
                                    if key in kw:
                                        categories.append(category)
                        
                        # If no categories were identified but package seems AI-related
                        if not categories and any(term in name.lower() for term in 
                                              ['ai', 'ml', 'tensorflow', 'neural', 'brain', 'mind', 
                                              'nlp', 'language', 'gpt', 'openai']):
                            categories = ['Artificial Intelligence']
                        
                        # Get download statistics - this is simplified
                        # In production, we would use the npm download counts API
                        monthly_downloads = 0
                        
                        # Create library data dictionary
                        library_data = {
                            'name': name,
                            'description': package.get('description', ''),
                            'version': latest_version,
                            'last_update': modified_time or datetime.now(),
                            'repository_url': repository_url,
                            'documentation_url': homepage_url,
                            'package_url': package.get('links', {}).get('npm', f"https://www.npmjs.com/package/{name}"),
                            'downloads': monthly_downloads,
                            'categories': list(set(categories)) if categories else ['JavaScript Libraries']
                        }
                        
                        libraries.append(library_data)
                        logger.info(f"Collected data for npm package: {name}")
                    
                    else:
                        logger.warning(f"Failed to get data for package {name}. Status code: {detailed_response.status_code}")
                
                except Exception as e:
                    logger.error(f"Error processing package {name}: {str(e)}")
        
        else:
            logger.warning(f"Failed to search npm packages. Status code: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error searching JavaScript libraries: {str(e)}")
    
    return libraries

def get_package_details(package_name):
    """
    Get detailed information about a specific npm package
    
    Args:
        package_name (str): Name of the package
        
    Returns:
        dict: Package details
    """
    try:
        package_url = f"{NPM_API_URL}/{package_name}"
        response = requests.get(package_url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get the latest version
            latest_version = data.get('dist-tags', {}).get('latest', '')
            
            # Get version data
            version_data = {}
            if latest_version and 'versions' in data and latest_version in data['versions']:
                version_data = data['versions'][latest_version]
            
            # Get version history
            versions = []
            if 'time' in data:
                for version, time_str in data['time'].items():
                    if version != 'created' and version != 'modified':
                        try:
                            release_date = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                            versions.append({
                                'version': version,
                                'release_date': release_date.isoformat()
                            })
                        except:
                            pass
            
            return {
                'name': package_name,
                'description': version_data.get('description', ''),
                'author': version_data.get('author', ''),
                'version': latest_version,
                'homepage': version_data.get('homepage', ''),
                'license': version_data.get('license', ''),
                'versions': versions
            }
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting details for package {package_name}: {str(e)}")
        return None 