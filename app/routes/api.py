from flask import Blueprint, jsonify, request
from app.models import Library, Category, Version
from app import db
from sqlalchemy import func
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/libraries')
def get_libraries():
    """API endpoint to get all libraries with optional filtering"""
    # Get query parameters
    language = request.args.get('language')
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    sort = request.args.get('sort', 'popularity')
    
    # Base query
    query = Library.query
    
    # Apply filters
    if language:
        query = query.filter(Library.language == language)
    
    if category_id:
        query = query.join(Library.categories).filter(Category.id == category_id)
    
    if search:
        query = query.filter(Library.name.ilike(f'%{search}%') | 
                           Library.description.ilike(f'%{search}%'))
    
    # Apply sorting
    if sort == 'popularity':
        query = query.order_by(Library.popularity_score.desc())
    elif sort == 'newest':
        query = query.order_by(Library.last_update.desc())
    elif sort == 'name':
        query = query.order_by(Library.name)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    # Execute query
    libraries = query.all()
    
    # Format results
    result = {
        'total': total_count,
        'limit': limit,
        'offset': offset,
        'libraries': [format_library(lib) for lib in libraries]
    }
    
    return jsonify(result)

@api_bp.route('/libraries/<int:library_id>')
def get_library(library_id):
    """API endpoint to get details of a specific library"""
    library = Library.query.get_or_404(library_id)
    
    # Get versions
    versions = Version.query.filter_by(library_id=library_id).order_by(Version.release_date.desc()).all()
    
    # Format library with versions
    result = format_library(library)
    result['versions'] = [format_version(v) for v in versions]
    
    return jsonify(result)

@api_bp.route('/categories')
def get_categories():
    """API endpoint to get all categories"""
    # Get query parameters
    type_filter = request.args.get('type')
    
    # Base query
    query = Category.query
    
    # Apply filter
    if type_filter:
        query = query.filter(Category.category_type == type_filter)
    
    # Add library count
    subquery = db.session.query(
        Category.id.label('category_id'),
        func.count(Library.id).label('library_count')
    ).join(
        Category.libraries
    ).group_by(
        Category.id
    ).subquery()
    
    query = query.outerjoin(
        subquery, 
        Category.id == subquery.c.category_id
    ).add_columns(
        func.coalesce(subquery.c.library_count, 0).label('library_count')
    ).order_by(
        func.coalesce(subquery.c.library_count, 0).desc()
    )
    
    # Execute query
    categories = query.all()
    
    # Format results
    result = {
        'categories': [
            {
                'id': category.id,
                'name': category.name,
                'type': category.category_type,
                'library_count': count
            }
            for category, count in categories
        ]
    }
    
    return jsonify(result)

@api_bp.route('/trends')
def get_trends():
    """API endpoint to get trending libraries and statistics"""
    # Get trending libraries
    trending_libraries = Library.query.order_by(Library.popularity_score.desc()).limit(10).all()
    
    # Get language distribution
    language_stats = db.session.query(
        Library.language,
        func.count(Library.id).label('count')
    ).group_by(
        Library.language
    ).all()
    
    # Get category distribution
    category_stats = db.session.query(
        Category.name,
        func.count(Library.id).label('count')
    ).join(
        Category.libraries
    ).group_by(
        Category.name
    ).order_by(
        func.count(Library.id).desc()
    ).limit(10).all()
    
    # Format results
    result = {
        'trending_libraries': [format_library(lib) for lib in trending_libraries],
        'language_distribution': [
            {'language': lang, 'count': count}
            for lang, count in language_stats
        ],
        'category_distribution': [
            {'category': cat, 'count': count}
            for cat, count in category_stats
        ]
    }
    
    return jsonify(result)

@api_bp.route('/latest')
def get_latest():
    """API endpoint to get latest library updates"""
    # Get days parameter (default to 30 days)
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Calculate cutoff date
    cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
    
    # Get latest libraries
    latest_libraries = Library.query.filter(Library.last_update >= cutoff_date).\
                      order_by(Library.last_update.desc()).\
                      limit(limit).all()
    
    # Format results
    result = {
        'latest_libraries': [format_library(lib) for lib in latest_libraries],
        'cutoff_date': cutoff_date.isoformat(),
        'days': days
    }
    
    return jsonify(result)

@api_bp.route('/stats')
def get_stats():
    """API endpoint to get general statistics"""
    # Get total counts
    total_libraries = Library.query.count()
    total_categories = Category.query.count()
    
    # Get language counts
    language_counts = db.session.query(
        Library.language,
        func.count(Library.id).label('count')
    ).group_by(
        Library.language
    ).all()
    
    # Get last update time
    last_update = db.session.query(func.max(Library.last_update)).scalar()
    
    # Format results
    result = {
        'total_libraries': total_libraries,
        'total_categories': total_categories,
        'languages': [
            {'language': lang, 'count': count}
            for lang, count in language_counts
        ],
        'last_update': last_update.isoformat() if last_update else None
    }
    
    return jsonify(result)

# Helper functions
def format_library(library):
    """Format a library object for API response"""
    return {
        'id': library.id,
        'name': library.name,
        'description': library.description,
        'language': library.language,
        'current_version': library.current_version,
        'last_update': library.last_update.isoformat() if library.last_update else None,
        'repository_url': library.repository_url,
        'documentation_url': library.documentation_url,
        'package_url': library.package_url,
        'popularity_score': library.popularity_score,
        'github_stars': library.github_stars,
        'monthly_downloads': library.monthly_downloads,
        'categories': [
            {
                'id': category.id,
                'name': category.name,
                'type': category.category_type
            }
            for category in library.categories
        ]
    }

def format_version(version):
    """Format a version object for API response"""
    return {
        'id': version.id,
        'version_number': version.version_number,
        'release_date': version.release_date.isoformat() if version.release_date else None,
        'release_notes': version.release_notes
    } 