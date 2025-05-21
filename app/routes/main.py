from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import Library, Category, Version
from app import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page showing dashboard with library trends"""
    # Get trending libraries sorted by popularity score
    trending_libraries = Library.query.order_by(Library.popularity_score.desc()).limit(10).all()
    
    # Get newest libraries sorted by last update
    newest_libraries = Library.query.order_by(Library.last_update.desc()).limit(10).all()
    
    # Get languages statistics
    languages = db.session.query(Library.language, func.count(Library.id)).\
                group_by(Library.language).all()
    
    return render_template('index.html', 
                           trending_libraries=trending_libraries,
                           newest_libraries=newest_libraries,
                           languages=languages)

@main_bp.route('/libraries')
def libraries():
    """Page listing all libraries with filtering options"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get query parameters
    q = request.args.get('q', '')
    sort = request.args.get('sort', 'popularity')
    view = request.args.get('view', 'grid')
    selected_languages = request.args.getlist('language')
    selected_categories = request.args.getlist('category')
    
    # Base query
    query = Library.query
    
    # Apply search filter
    if q:
        query = query.filter(Library.name.ilike(f'%{q}%') | Library.description.ilike(f'%{q}%'))
    
    # Apply language filter
    if selected_languages:
        query = query.filter(Library.language.in_(selected_languages))
    
    # Apply category filter
    if selected_categories:
        query = query.join(Library.categories).filter(Category.id.in_([int(cat_id) for cat_id in selected_categories]))
    
    # Apply sorting
    if sort == 'popularity':
        query = query.order_by(Library.popularity_score.desc())
    elif sort == 'newest':
        query = query.order_by(Library.last_update.desc())
    elif sort == 'name':
        query = query.order_by(Library.name)
    
    # Paginate results
    libraries = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all categories for filter sidebar
    categories = Category.query.order_by(Category.name).all()
    
    # Get total count and last updated time
    total_libraries = Library.query.count()
    last_updated = db.session.query(func.max(Library.last_update)).scalar()
    
    # Calculate pagination info
    next_page = page + 1 if libraries.has_next else None
    prev_page = page - 1 if libraries.has_prev else None
    total_pages = libraries.pages or 1
    
    return render_template('libraries.html',
                           libraries=libraries.items,
                           page=page,
                           total_pages=total_pages,
                           next_page=next_page,
                           prev_page=prev_page,
                           total_libraries=total_libraries,
                           categories=categories,
                           selected_languages=selected_languages,
                           selected_categories=selected_categories,
                           sort=sort,
                           view=view,
                           languages=db.session.query(Library.language, func.count(Library.id)).group_by(Library.language).all(),
                           last_updated=last_updated)

@main_bp.route('/libraries/<int:library_id>')
def library_detail(library_id):
    """Detail page for a specific library"""
    library = Library.query.get_or_404(library_id)
    
    # Get version history
    versions = Version.query.filter_by(library_id=library_id).order_by(Version.release_date.desc()).all()
    
    # Get similar libraries (same categories or language)
    similar_libraries = []
    if library.categories:
        category_ids = [c.id for c in library.categories]
        similar_by_category = Library.query.join(Library.categories).\
                              filter(Category.id.in_(category_ids)).\
                              filter(Library.id != library_id).\
                              order_by(Library.popularity_score.desc()).\
                              limit(3).all()
        similar_libraries.extend(similar_by_category)
    
    # Add some by language if needed
    if len(similar_libraries) < 5:
        similar_by_language = Library.query.\
                             filter(Library.language == library.language).\
                             filter(Library.id != library_id).\
                             filter(~Library.id.in_([l.id for l in similar_libraries])).\
                             order_by(Library.popularity_score.desc()).\
                             limit(5 - len(similar_libraries)).all()
        similar_libraries.extend(similar_by_language)
    
    return render_template('library_detail.html', 
                           library=library,
                           versions=versions,
                           similar_libraries=similar_libraries)

@main_bp.route('/categories')
def categories():
    """Page listing all categories"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    q = request.args.get('q', '')
    selected_types = request.args.getlist('type')
    
    # Base query
    query = Category.query
    
    # Apply search filter
    if q:
        query = query.filter(Category.name.ilike(f'%{q}%'))
    
    # Apply type filter
    if selected_types:
        query = query.filter(Category.category_type.in_(selected_types))
    
    # Add library count to each category
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
    
    # Paginate results
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Process results to include library count
    categories_with_count = []
    for category, count in paginated.items:
        category.library_count = count
        
        # Assign an appropriate icon based on category name
        if 'machine learning' in category.name.lower():
            category.icon = 'fas fa-brain'
        elif 'vision' in category.name.lower():
            category.icon = 'fas fa-eye'
        elif 'nlp' in category.name.lower() or 'language' in category.name.lower():
            category.icon = 'fas fa-comment-alt'
        elif 'speech' in category.name.lower() or 'voice' in category.name.lower():
            category.icon = 'fas fa-microphone'
        elif 'reinforcement' in category.name.lower():
            category.icon = 'fas fa-cogs'
        elif 'generative' in category.name.lower():
            category.icon = 'fas fa-lightbulb'
        elif 'neural' in category.name.lower():
            category.icon = 'fas fa-network-wired'
        else:
            category.icon = 'fas fa-robot'
            
        categories_with_count.append(category)
    
    # Get top categories for chart
    top_categories = db.session.query(
        Category.id,
        Category.name,
        func.count(Library.id).label('library_count')
    ).join(
        Category.libraries
    ).group_by(
        Category.id,
        Category.name
    ).order_by(
        func.count(Library.id).desc()
    ).limit(10).all()
    
    # Calculate pagination info
    next_page = page + 1 if paginated.has_next else None
    prev_page = page - 1 if paginated.has_prev else None
    total_pages = paginated.pages or 1
    
    # Get last updated time
    last_updated = db.session.query(func.max(Library.last_update)).scalar()
    
    return render_template('categories.html',
                           categories=categories_with_count,
                           top_categories=top_categories,
                           page=page,
                           total_pages=total_pages,
                           next_page=next_page,
                           prev_page=prev_page,
                           selected_types=selected_types,
                           category_stats=top_categories,
                           last_updated=last_updated)

@main_bp.route('/about')
def about():
    """About page with project information"""
    # Get basic stats
    total_libraries = Library.query.count()
    categories = Category.query.all()
    last_updated = db.session.query(func.max(Library.last_update)).scalar()
    
    # Get language statistics
    language_stats = db.session.query(
        Library.language,
        func.count(Library.id)
    ).group_by(
        Library.language
    ).all()
    
    return render_template('about.html',
                           total_libraries=total_libraries,
                           categories=categories,
                           last_updated=last_updated,
                           language_stats=language_stats) 