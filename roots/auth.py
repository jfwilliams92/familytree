from flask import Blueprint, render_template
from . import db
import json, plotly

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/tree')
def tree():
    from .models import create_tree
    from .treeplot import tree_plot
    tree = create_tree()
    tree.update_node_positions()
    fig = tree_plot(tree.graph_)

    figureJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('tree.html', figureJSON=figureJSON)


@auth.route('/logout')
def logout():
    return 'Logout'