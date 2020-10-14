from flask import Blueprint, render_template

bp = Blueprint('blackboard', __name__, url_prefix='/blackboard')


@bp.route('/', methods=['GET', 'POST'])
def home():
    return render_template('blackboard/home.html')
