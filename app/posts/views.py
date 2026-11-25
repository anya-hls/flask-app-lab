from datetime import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request
)
from sqlalchemy import select

from app import db
from app.posts import posts_bp
from app.posts.models import Post, Tag
from app.posts.forms import PostForm


def get_tags_by_ids(ids):
    return list(db.session.scalars(
        select(Tag).where(Tag.id.in_(ids))
    ).all())


@posts_bp.route('/post')
def post_list():
    posts = Post.query.filter_by(is_active=True).order_by(
        Post.posted.desc()
    ).all()

    return render_template(
        'posts/posts.html',
        posts=posts,
        title='Допис'
    )


@posts_bp.route('/post/create', methods=['GET', 'POST'])
def post_create():
    form = PostForm()

    if request.method == 'GET':
        form.publish_date.data = datetime.now().replace(second=0, microsecond=0)

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            posted=form.publish_date.data,
            category=form.category.data,
            is_active=form.is_active.data,
            user_id=form.author_id.data
        )
        post.tags = get_tags_by_ids(form.tags.data)

        db.session.add(post)
        db.session.commit()

        flash('Допис успішно створено!', 'success')

        return redirect(url_for('posts.post_list'))

    return render_template(
        'posts/post_form.html',
        form=form,
        title='Створення допису',
        heading='Створити допис'
    )


@posts_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    post = db.session.get(Post, post_id)

    if post is None:
        abort(404)

    return render_template(
        'posts/post_detail.html',
        post=post,
        title=post.title
    )


@posts_bp.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
def post_update(post_id):
    post = db.session.get(Post, post_id)

    if post is None:
        abort(404)

    form = PostForm(obj=post)

    if request.method == 'GET':
        form.publish_date.data = post.posted
        form.author_id.data = post.user_id
        form.tags.data = [t.id for t in post.tags]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.posted = form.publish_date.data
        post.category = form.category.data
        post.is_active = form.is_active.data
        post.user_id = form.author_id.data
        post.tags = get_tags_by_ids(form.tags.data)

        db.session.commit()

        flash('Допис успішно оновлено!', 'success')

        return redirect(
            url_for('posts.post_detail', post_id=post.id)
        )

    return render_template(
        'posts/post_form.html',
        form=form,
        post=post,
        title='Редагування допису',
        heading='Редагувати допис'
    )


@posts_bp.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
def post_delete(post_id):
    post = db.session.get(Post, post_id)

    if post is None:
        abort(404)

    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()

        flash('Допис успішно видалено!', 'success')

        return redirect(url_for('posts.post_list'))

    return render_template(
        'posts/post_delete.html',
        post=post,
        title='Видалення допису'
    )
    