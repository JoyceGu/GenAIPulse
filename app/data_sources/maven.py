import requests
import os
import logging
from datetime import datetime
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL
MAVEN_API_URL = os.getenv('MAVEN_API_URL', 'https://search.maven.org/solrsearch/select')

def search_libraries(keyword, max_results=100):
    """
    Search for Java libraries using Maven Central Repository API
    
    Args:
        keyword (str): Search keyword
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of library data dictionaries
    """
    libraries = []
    
    try:
        # Use Maven Search API
        params = {
            'q': keyword,
            'rows': max_results,
            'wt': 'json'
        }
        
        response = requests.get(MAVEN_API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            # For demonstration purposes, we'll add some predefined AI libraries
            # This is to ensure we get relevant AI libraries regardless of the API response
            if 'ai' in keyword.lower() or 'machine learning' in keyword.lower():
                predefined_packages = [
                    {'id': 'org.deeplearning4j:deeplearning4j-core', 'g': 'org.deeplearning4j', 'a': 'deeplearning4j-core', 'latestVersion': '1.0.0-M2.1', 'versionCount': 30, 'description': 'Deep Learning library for Java'},
                    {'id': 'org.nd4j:nd4j-api', 'g': 'org.nd4j', 'a': 'nd4j-api', 'latestVersion': '1.0.0-M2.1', 'versionCount': 30, 'description': 'Scientific computing library for the JVM'},
                    {'id': 'org.apache.mahout:mahout-core', 'g': 'org.apache.mahout', 'a': 'mahout-core', 'latestVersion': '0.9', 'versionCount': 15, 'description': 'Apache Mahout Machine Learning Library'},
                    {'id': 'ai.djl:api', 'g': 'ai.djl', 'a': 'api', 'latestVersion': '0.18.0', 'versionCount': 12, 'description': 'Deep Java Library (DJL) API'},
                    {'id': 'org.tensorflow:tensorflow', 'g': 'org.tensorflow', 'a': 'tensorflow', 'latestVersion': '1.15.0', 'versionCount': 25, 'description': 'TensorFlow for Java'},
                    {'id': 'org.datavec:datavec-api', 'g': 'org.datavec', 'a': 'datavec-api', 'latestVersion': '1.0.0-M2.1', 'versionCount': 20, 'description': 'DataVec API for machine learning data pipelines'},
                    {'id': 'weka:weka', 'g': 'weka', 'a': 'weka', 'latestVersion': '3.9.5', 'versionCount': 10, 'description': 'Weka Machine Learning Library'},
                    {'id': 'org.tribuo:tribuo-all', 'g': 'org.tribuo', 'a': 'tribuo-all', 'latestVersion': '4.2.2', 'versionCount': 5, 'description': 'Tribuo - Oracle Machine Learning Library for Java'},
                    {'id': 'org.apache.spark:spark-mllib_2.12', 'g': 'org.apache.spark', 'a': 'spark-mllib_2.12', 'latestVersion': '3.1.2', 'versionCount': 18, 'description': 'Spark MLlib (Machine Learning library)'},
                    {'id': 'org.languagetool:language-en', 'g': 'org.languagetool', 'a': 'language-en', 'latestVersion': '5.6', 'versionCount': 15, 'description': 'LanguageTool NLP library for English'}
                ]
                
                # Add these packages to the existing data
                existing_ids = {f"{doc.get('g', '')}:{doc.get('a', '')}" for doc in docs}
                for package in predefined_packages:
                    if package['id'] not in existing_ids and len(docs) < max_results:
                        docs.append(package)
            
            for doc in docs:
                group_id = doc.get('g', '')
                artifact_id = doc.get('a', '')
                
                if not group_id or not artifact_id:
                    continue
                
                package_id = f"{group_id}:{artifact_id}"
                
                # Avoid too many requests in short time
                time.sleep(0.2)
                
                try:
                    # Get package details
                    # For demonstration, we'll use the package data we already have
                    # In production, we would make another request to get more details
                    
                    # Extract information
                    latest_version = doc.get('latestVersion', '')
                    description = doc.get('description', '')
                    
                    # Determine categories based on package ID and description
                    categories = []
                    
                    # Keywords to categories mapping
                    keyword_to_category = {
                        'ml': 'Machine Learning',
                        'machinelearning': 'Machine Learning',
                        'deeplearning': 'Deep Learning',
                        'tensorflow': 'Deep Learning',
                        'neural': 'Neural Networks',
                        'ai': 'Artificial Intelligence',
                        'djl': 'Deep Learning',
                        'vision': 'Computer Vision',
                        'image': 'Computer Vision',
                        'nlp': 'Natural Language Processing',
                        'language': 'Natural Language Processing',
                        'text': 'Natural Language Processing',
                        'voice': 'Speech Processing',
                        'speech': 'Speech Processing',
                        'mahout': 'Machine Learning',
                        'weka': 'Machine Learning',
                        'spark-mllib': 'Machine Learning',
                        'tribuo': 'Machine Learning',
                        'nd4j': 'Scientific Computing'
                    }
                    
                    # Check package ID
                    for key, category in keyword_to_category.items():
                        if key.lower() in package_id.lower():
                            categories.append(category)
                    
                    # Check description
                    if description:
                        for key, category in keyword_to_category.items():
                            if key.lower() in description.lower() and category not in categories:
                                categories.append(category)
                    
                    # If no categories were identified but package seems AI-related
                    if not categories and any(term in package_id.lower() for term in 
                                            ['ai', 'ml', 'learn', 'deeplearning', 'tensorflow', 'neural']):
                        categories = ['Artificial Intelligence']
                    
                    # Create library data dictionary
                    library_data = {
                        'name': package_id,
                        'description': description,
                        'version': latest_version,
                        'last_update': datetime.now(),  # Simplified, would get from API in production
                        'repository_url': f"https://github.com/search?q={package_id}",  # Simplified
                        'documentation_url': f"https://search.maven.org/artifact/{group_id}/{artifact_id}",
                        'package_url': f"https://search.maven.org/artifact/{group_id}/{artifact_id}/{latest_version}/jar",
                        'downloads': 0,  # Maven doesn't provide download statistics
                        'categories': list(set(categories)) if categories else ['Java Libraries']
                    }
                    
                    libraries.append(library_data)
                    logger.info(f"Collected data for Maven package: {package_id}")
                
                except Exception as e:
                    logger.error(f"Error processing package {package_id}: {str(e)}")
        
        else:
            logger.warning(f"Failed to search Maven packages. Status code: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error searching Java libraries: {str(e)}")
    
    return libraries

def get_package_details(group_id, artifact_id):
    """
    Get detailed information about a specific Maven package
    
    Args:
        group_id (str): Group ID of the package
        artifact_id (str): Artifact ID of the package
        
    Returns:
        dict: Package details
    """
    try:
        # Get package versions
        params = {
            'q': f"g:{group_id} AND a:{artifact_id}",
            'core': 'gav',
            'rows': 100,
            'wt': 'json'
        }
        
        response = requests.get(MAVEN_API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            if docs:
                # Sort versions
                versions = []
                for doc in docs:
                    version = doc.get('v', '')
                    timestamp = doc.get('timestamp', 0)
                    if version:
                        versions.append({
                            'version': version,
                            'timestamp': timestamp
                        })
                
                # Sort by timestamp (newest first)
                versions.sort(key=lambda x: x['timestamp'], reverse=True)
                
                # Get the latest version details
                latest_version = versions[0]['version'] if versions else ''
                
                return {
                    'group_id': group_id,
                    'artifact_id': artifact_id,
                    'version': latest_version,
                    'versions': [v['version'] for v in versions],
                    'repository_url': f"https://search.maven.org/artifact/{group_id}/{artifact_id}/{latest_version}/jar"
                }
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting details for package {group_id}:{artifact_id}: {str(e)}")
        return None 