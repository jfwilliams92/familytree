import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly
import plotly.graph_objs as go 
import json

from treecreation import create_tree
from treeplotting import plotly_graph

tree = create_tree()
tree.update_node_positions()
selected_nodes = []

fig = plotly_graph(tree._graph)

DEFAULT_COLOR = 'blue'
DEFAULT_SIZE = 10

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    children=[
    html.H1(children='Hello Dash'),

    html.Div(
        children='''
        Dash: A web application framework for Python.
        '''
    ),

    html.Div(
        className="row",
        children = [
            dcc.Graph(
                id='example-graph',
                figure=fig
            ),

            html.Div(
                id='text-output',
                children='Click a point on the graph to change me'
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
])


def accumulate_clicks(new_click, click_list, max_click_num=2):
    
    enqueued = None
    dequeued = None


    if new_click in click_list:
        dequeued = new_click
        click_list.remove(new_click)

    else:
        if len(click_list) < max_click_num:
            click_list.append(new_click)

        else:
            dequeued = click_list[-1]
            click_list[:-1] = click_list[1:]
            click_list[-1] = new_click
    

class clickList():
    def __init__(self, max_clicks=2):
        self.clicks = list()
        self.max_clicks = max_clicks

    def accumulate(self, new_click):
        dequeued = None
        
        if new_click in self.clicks:
            dequeued = new_click
            self.clicks.remove(new_click)

        else:
            if len(self.clicks) < self.max_clicks:
                self.clicks.append(new_click)

            else:
                dequeued = self.clicks[0]
                self.clicks[:-1] = self.clicks[1:]
                self.clicks[-1] = new_click
    
        return dequeued

    def clear(self):
        self.clicks = []


def highlight_path(tree, node_list):

    edge_tuples = list(zip(node_list[:-1], node_list[1:]))
    
    edge_indices = []
    for idx, edge in enumerate(tree._graph.edges):
        if edge in edge_tuples:
            edge_indices.append(idx)

    return edge_indices


class markerUpdater():
    def __init__(
            self,
            figure,
            trace_ix,
            on_color='red',
            off_color='blue',
            on_size='12',
            off_size='10'
    ):

        self.figure = figure
        self.trace_ix = trace_ix
        self.on_color = on_color
        self.off_color = off_color
        self.on_size = on_size
        self.off_size = off_size

    def update_marker(self, marker_ix, direction='on'):
        if direction == 'on':
            self.figure['data'][self.trace_ix]['marker']['color'][marker_ix] = self.on_color
            self.figure['data'][self.trace_ix]['marker']['size'][marker_ix] = self.on_size

        else:
            self.figure['data'][self.trace_ix]['marker']['color'][marker_ix] = self.off_color
            self.figure['data'][self.trace_ix]['marker']['size'][marker_ix] = self.off_size


clicks = clickList(max_clicks=2)
updater = markerUpdater(figure=fig, trace_ix=1)

@app.callback(
    [
        Output('text-output', 'children'),
        Output('example-graph', 'figure'),
        Output('node-1', 'children'),
        Output('relationship', 'children'),
        Output('node-2', 'children')
    ],
    [Input('example-graph', 'clickData')],
    [State('example-graph', 'figure')]
    )

def display_click_data(clickData, fig):
    relationship = ""
    if clickData is not None:
        point_data = clickData['points'][0]['pointIndex']

        removed_point_idx = clicks.accumulate(new_click=point_data)
        
        fig['data'][1]['marker']['color'][point_data] = 'red'
        fig['data'][1]['marker']['size'][point_data] = 12

        if removed_point_idx:
            fig['data'][1]['marker']['color'][removed_point_idx] = 'blue'
            fig['data'][1]['marker']['size'][removed_point_idx] = 10


        if len(selected_nodes) == 0:
            selected_nodes.append(point_data)

        elif len(selected_nodes) > 0:
            if point_data in selected_nodes:
                selected_nodes.remove(point_data)
                fig['data'][1]['marker']['color'][point_data] = 'blue'
                fig['data'][1]['marker']['size'][point_data] = 10

            else:
                # point is not in selected points already
                if len(selected_nodes) < 2:
                    selected_nodes.append(point_data)

                elif len(selected_nodes) == 2:
                    removed_point_idx = selected_nodes[0]
                    fig['data'][1]['marker']['color'][removed_point_idx] = 'blue'
                    fig['data'][1]['marker']['size'][removed_point_idx] = 10

                    selected_nodes[0] = selected_nodes[1]
                    selected_nodes[1] = point_data

                relationship = tree.determine_familial_relationship(selected_nodes[0] + 1, selected_nodes[1] + 1)
                
    node_data = ["", ""]
    for idx, point_idx in enumerate(selected_nodes):
        node_data[idx] = json.dumps(
            tree._graph.nodes[point_idx + 1],
            default=lambda x: 'not working',
            indent=4
        )
        #print(tree._graph.nodes[point_idx + 1])
        fig['data'][1]['marker']['color'][point_idx] = 'red'
        fig['data'][1]['marker']['size'][point_idx] = 12

    selected_nodes_str = [str(d) for d in selected_nodes]
    selected_nodes_str = '; '.join(selected_nodes_str)

    return json.dumps(fig['data'][0]), fig, node_data[0], relationship, node_data[1]
    #return json.dumps(fig['data'][1])

if __name__ == '__main__':
    app.run_server(debug=True)