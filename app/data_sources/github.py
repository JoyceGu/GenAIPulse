import requests
import os
import logging
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub API Token
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Headers for GitHub API
headers = {
    'Accept': 'application/vnd.github.v3+json'
}

# If token is provided, use it for authentication
if GITHUB_TOKEN:
    headers['Authorization'] = f'token {GITHUB_TOKEN}'

def get_repository_data(owner, repo):
    """
    Get data about a GitHub repository
    
    Args:
        owner (str): Repository owner (username or organization)
        repo (str): Repository name
        
    Returns:
        dict: Repository data including stars, forks, etc.
    """
    try:
        # Get repository data
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get release data
            releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            releases_response = requests.get(releases_url, headers=headers, params={'per_page': 5})
            releases = releases_response.json() if releases_response.status_code == 200 else []
            
            # Get latest release date
            latest_release_date = None
            if releases and isinstance(releases, list) and len(releases) > 0:
                try:
                    latest_release_date = datetime.strptime(releases[0]['published_at'], '%Y-%m-%dT%H:%M:%SZ')
                except:
                    pass
            
            # Get commit data for activity
            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            since_date = (datetime.now() - timedelta(days=30)).isoformat()
            commits_response = requests.get(
                commits_url, 
                headers=headers, 
                params={'per_page': 1, 'since': since_date}
            )
            
            # Check if rate limited
            if commits_response.status_code == 403 and 'rate limit exceeded' in commits_response.text.lower():
                logger.warning(f"GitHub API rate limit exceeded for {owner}/{repo}")
                # Use the data we already have
                return {
                    'name': data['name'],
                    'full_name': data['full_name'],
                    'description': data['description'],
                    'stars': data['stargazers_count'],
                    'forks': data['forks_count'],
                    'open_issues': data['open_issues_count'],
                    'watchers': data['watchers_count'],
                    'latest_release_date': latest_release_date.isoformat() if latest_release_date else None,
                    'last_commit_date': None,
                    'activity_level': 'unknown'
                }
            
            # Process commit data to determine activity level
            activity_level = 'low'
            last_commit_date = None
            
            if commits_response.status_code == 200:
                commits = commits_response.json()
                if commits and isinstance(commits, list) and len(commits) > 0:
                    try:
                        last_commit_date = datetime.strptime(commits[0]['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ')
                        
                        # Check activity level based on commits
                        if (datetime.now() - last_commit_date).days < 7:
                            activity_level = 'high'
                        elif (datetime.now() - last_commit_date).days < 30:
                            activity_level = 'medium'
                    except:
                        pass
            
            return {
                'name': data['name'],
                'full_name': data['full_name'],
                'description': data['description'],
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'open_issues': data['open_issues_count'],
                'watchers': data['watchers_count'],
                'latest_release_date': latest_release_date.isoformat() if latest_release_date else None,
                'last_commit_date': last_commit_date.isoformat() if last_commit_date else None,
                'activity_level': activity_level
            }
        
        elif response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            logger.warning(f"GitHub API rate limit exceeded for {owner}/{repo}")
            # Return minimal data
            return {
                'name': repo,
                'full_name': f"{owner}/{repo}",
                'description': '',
                'stars': 0,
                'forks': 0,
                'open_issues': 0,
                'watchers': 0,
                'latest_release_date': None,
                'last_commit_date': None,
                'activity_level': 'unknown'
            }
        
        else:
            logger.warning(f"Failed to get repository data for {owner}/{repo}. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error getting repository data for {owner}/{repo}: {str(e)}")
        return None

def search_ai_repos(query, max_results=20):
    """
    Search for AI/ML repositories on GitHub
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of repository data
    """
    try:
        search_url = "https://api.github.com/search/repositories"
        search_query = f"{query} topic:ai OR topic:machine-learning OR topic:deep-learning"
        
        # Parameters for search
        params = {
            'q': search_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': max_results
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            repos = data.get('items', [])
            
            results = []
            for repo in repos:
                repo_data = {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'url': repo['html_url'],
                    'language': repo['language']
                }
                results.append(repo_data)
            
            return results
        
        elif response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            logger.warning(f"GitHub API rate limit exceeded for search: {query}")
            return []
        
        else:
            logger.warning(f"Failed to search repositories. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        logger.error(f"Error searching repositories: {str(e)}")
        return []

def get_trending_ai_repos():
    """
    Get trending AI/ML repositories on GitHub
    
    Returns:
        list: List of trending repositories
    """
    # We'll search for repositories created within the last month
    date_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        search_url = "https://api.github.com/search/repositories"
        search_query = f"topic:ai OR topic:machine-learning OR topic:deep-learning created:>{date_month_ago}"
        
        # Parameters for search
        params = {
            'q': search_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            repos = data.get('items', [])
            
            results = []
            for repo in repos:
                repo_data = {
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'url': repo['html_url'],
                    'language': repo['language'],
                    'created_at': repo['created_at']
                }
                results.append(repo_data)
            
            return results
        
        elif response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            logger.warning("GitHub API rate limit exceeded for trending repositories")
            return []
        
        else:
            logger.warning(f"Failed to get trending repositories. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        logger.error(f"Error getting trending repositories: {str(e)}")
        return [] 