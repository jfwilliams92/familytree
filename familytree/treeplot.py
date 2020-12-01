import plotly
import plotly.graph_objs as go
import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from .models import create_tree
tree = create_tree()
tree.update_node_positions()

def tree_plot(G):
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        # line=dict(width=[0.5] * len(edge_x), color=['#888'] * len(edge_x)),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        node_data = G.nodes[node]
        x, y = node_data['pos']
        node_x.append(x)
        node_y.append(y)

        name = str(node_data['first_name']) + ' ' + str(node_data['middle_name']) + ' ' + str(node_data['last_name']) + ' ' + str(node_data['suffix'])
        node_text.append(name)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        hovertext=node_text,
        marker=dict(
            #showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            #colorscale='YlGnBu',
            #reversescale=True,
            color=['blue'] * len(node_x),
            size=[10] * len(node_x),
            line_width=2))

    layout = go.Layout(
        title='Family Tree',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=15,r=15,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=750
    )

    fig = dict(data=[edge_trace, node_trace], layout=layout)

    return fig

fig = tree_plot(tree.graph_)

def create_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            'https://codepen.io/chriddyp/pen/bWLwgP.css',
        ]
    )

    dash_app.layout = html.Div(
        children=[
            html.A(html.Button('Go back', className='three-columns'), href='/index'),
            html.H2(children='Your family tree!'),

            html.Div(
                className="row",
                children = [
                    dcc.Graph(
                        id='family-tree',
                        figure=fig
                    ),

                    html.Div(
                        id='text-output',
                        children='Click a point on the tree!'
                    )   
                ]
            ),

            html.Div(
                className="row",
                children=[
                    html.Div(
                        id="node-1", children="", className="five columns"
                    ),
                    html.Div(
                        id="relationship", children="", className="two columns"
                    ),
                    html.Div(
                        id="node-2", children="", className="five columns"
                    )
                ]
            )   
        ]
    )
    return dash_app.server