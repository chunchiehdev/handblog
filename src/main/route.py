from flask import render_template, request, Blueprint
from ..models import Posts, Users, Visit
from sqlalchemy import or_, and_
from ..posts.form import SearchForm
from .. import db

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    if 'keyword' in request.args:
        keyword = request.args['keyword']
        page = request.args.get('page', 1 , type=int)
        # search the posts using the keyword
        posts = Posts.query.join(Users).filter(
            or_(
                Posts.title.like(f'%{keyword}%'),
                Posts.content.like(f'%{keyword}%'),
                and_(Users.name == keyword, Posts.poster_id == Users.id)
            )
        ).order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5)
        
    # 從資料庫獲取文章
    else:
        page = request.args.get('page', 1 , type=int)
        posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=5)
    
    visit_page = get_normalized_page_path(request.path)  # 獲取造訪的頁面
    visit_record = Visit.query.filter_by(page=visit_page).first()
    if visit_record:
        visit_record.count += 1
    else:
        visit_record = Visit(page=visit_page, count=1)
        db.session.add(visit_record)
    db.session.commit()

    return render_template("posts.html", posts=posts)

def get_normalized_page_path(path):
    normalized_path = path.strip().lower()
    if normalized_path in ['', '/', '/home', 'home']:
        return '/'
    return normalized_path

@main.context_processor
def base():
    form = SearchForm()
    
    # 定義取得用戶造訪次數的函式
    def get_visit_count(page):
        visit_record = Visit.query.filter_by(page=page).first()
        return visit_record.count if visit_record else 0

    return dict(form=form, get_visit_count=get_visit_count)


    
