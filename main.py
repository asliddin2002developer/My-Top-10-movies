from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired
import requests

API_KEY = '0d6bfd3cd78beb33a2131157bf002936'
MOVIE_END_POINT = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
db = SQLAlchemy(app)

class MovieForm(FlaskForm):
    new_rating = FloatField('Your rating out of 10. eg.7.5', validators=[DataRequired()])
    new_review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Done', validators=[DataRequired()])

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add movie', validators=[DataRequired()])

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(250))
    year = db.Column(db.Integer)
    description = db.Column(db.String(1000))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)
db.create_all()



@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_END_POINT, params={'api_key': API_KEY, 'query': movie_title})
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)


@app.route('/find_movie')
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f'{MOVIE_DB_INFO_URL}/{movie_api_id}'

        response = requests.get(movie_api_url, params={'api_key': API_KEY, 'language': 'en-US'})
        data = response.json()
        new_movie = Movie(
            title=data['title'],
            year=data['release_date'].split('-')[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data['overview']

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))



@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = MovieForm()
    all_movies = db.session.query(Movie).all()
    id = request.args.get('id')
    movie_id = Movie.query.get(id)
    if form.validate_on_submit() and request.method == 'POST':
        movie_id.rating = form.new_rating.data
        movie_id.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movies=all_movies, form=form)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    query_to_delete = Movie.query.get(movie_id)
    db.session.delete(query_to_delete)
    db.session.commit()

    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)
