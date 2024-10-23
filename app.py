from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from fractions import Fraction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recetas.db'
app.config['SECRET_KEY'] = '19150909'  # Required for flashing messages
db = SQLAlchemy(app)

# Model for Recipes
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    recipe = db.Column(db.Text, nullable=False)
    ingre = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Recipe {self.name}>'

# # Model for Weekly Meal Plan
# class MealPlan(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     day = db.Column(db.String(50), nullable=False)
#     recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
#     recipe = db.relationship('Recipe', backref='meal_plans')

#     def __repr__(self):
#         return f'<PlanSemanal {self.day}: {self.recipe}>'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        recipe_name = request.form['name']
        recipe_details = request.form['recipe']
        recipe_ing = request.form['ingre']
        new_recipe = Recipe(name=recipe_name, recipe=recipe_details, ingre=recipe_ing)

        try:
            db.session.add(new_recipe)
            db.session.commit()
            flash('Receta añadida!', 'success')
        except Exception as e:
            flash(f'Error al añadir receta: {str(e)}', 'danger')

    recipes = Recipe.query.all()
    for recipe in recipes:
        recipe.recipe = recipe.recipe.replace('\n', '<br>')
        recipe.ingre = recipe.ingre.replace('\n', '<br>')
    return render_template('index.html', recipes=recipes)

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    recipe_to_delete = Recipe.query.get_or_404(id)

    try:
        db.session.delete(recipe_to_delete)
        db.session.commit()
        return '', 204  # No content response on success
    except Exception as e:
        db.session.rollback()
        return str(e), 400  # Return error message


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    recipe = Recipe.query.get_or_404(id)

    if request.method == 'POST':
        recipe.name = request.form['name']
        recipe.recipe = request.form['recipe']

        try:
            db.session.commit()
            flash('Recipe updated successfully!', 'success')
            return redirect('/')
        except Exception as e:
            flash(f'There was an issue updating your recipe: {str(e)}', 'danger')

    return render_template('update.html', recipe=recipe)

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    weekly_plan = {}
    if request.method == 'POST':
        for day in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']:
            recipe_id = request.form.get(day.lower())
            if recipe_id:
                recipe = Recipe.query.get(recipe_id)
                ingredients = recipe.ingre.split('\r\n')
                for ingredient in ingredients:
                    quant = ingredient.split()[0]
                    name = ' '.join(ingredient.split()[1:])
                    if name in weekly_plan:
                        weekly_plan[name] = weekly_plan[name] +  Fraction(quant)
                    else:
                        weekly_plan[name] = Fraction(quant)
        print(weekly_plan)
        for name, quant in weekly_plan.items():
            weekly_plan[name] = str(quant)
        print(weekly_plan)
        session['weekly_plan'] = weekly_plan

    recipes = Recipe.query.all()
    return render_template('calendar.html', recipes=recipes)

@app.route('/print')
def print_meal_plan():
    weekly_plan = session.get('weekly_plan', {})
    return render_template('print.html', weekly_plan=weekly_plan)


def create_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
