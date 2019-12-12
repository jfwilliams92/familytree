import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go 

from treecreation import create_tree
from treeplotting import plotly_graph

tree = create_tree()
tree.update_node_positions()

fig = plotly_graph(tree._graph)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)