from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import db
from flaskblog.models import PostModel
from flaskblog.posts.forms import (
    PostFormModel,
    UpdatePostModel
)
from flask_login import current_user, login_required

posts = Blueprint('posts', __name__)


@posts.route("/post/new/", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostFormModel()
    if form.validate_on_submit():
        post = PostModel(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@posts.route("/post/<int:post_id>/", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = PostModel.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = PostModel.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = UpdatePostModel()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated", "success")
        return redirect(url_for("posts.post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = PostModel.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted", "success")
    return redirect(url_for('main.home'))
