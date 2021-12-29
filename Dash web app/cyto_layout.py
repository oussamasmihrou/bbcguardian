import json
from app import app

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
import dash_reusable_components as drc
import dash_bootstrap_components as dbc


# ###################### DATA PREPROCESSING ######################
# Load data
with open('sample_network.txt', 'r') as f:
    network_data = f.read().split('\n')

# We select the first 750 edges and associated nodes for an easier visualization
edges = network_data[:750]
nodes = set()

cy_edges = []
cy_nodes = []

for network_edge in edges:
    source, target = network_edge.split(" ")

    if source not in nodes:
        nodes.add(source)
        cy_nodes.append({"data": {"id": source, "label": "User #" + source[-5:]}})
    if target not in nodes:
        nodes.add(target)
        cy_nodes.append({"data": {"id": target, "label": "User #" + target[-5:]}})

    cy_edges.append({
        'data': {
            'source': source,
            'target': target
        }
    })

default_stylesheet = [
    {
        "selector": 'node',
        'style': {
            "opacity": 0.65,
        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.65
        }
    },
]

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 50px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {
        'height': 'calc(98vh - 105px)'
    }
}
layout_items = [
    {"label": "random", "value": "random"},
    {"label": "grid", "value": "grid"},
    {"label": "circle", "value": "circle"},
    {"label": "concentric", "value": "concentric"},
    {"label": "breadthfirst", "value": "breadthfirst"},
    {"label": "cose", "value": "cose"},
]
Node_shape_items = [
    {"label": "ellipse", "value": "ellipse"},
    {"label": "triangle", "value": "triangle"},
    {"label": "rectangle", "value": "rectangle"},
    {"label": "diamond", "value": "diamond"},
]

cyto_layout_main = dbc.Card([
    dbc.CardBody(
    dbc.Row([
        dbc.Col(
        cyto.Cytoscape(
            id='cytoscape',
            elements=cy_edges + cy_nodes,
            style={
                'height': '95vh',
                'width': '100%'
            }
        ),
        width={"size": 9})
    ,
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                dbc.Tabs(id='graph-control-tabs', children=[
                        dbc.Tab(label='Control Panel', children=[
                            dbc.Row(dbc.Col(
                                dbc.Select(
                                id='dropdown-layout',
                                value = "random",
                                options = layout_items,
                                className= "form-select"
                                
                                
                            ), width = 12)),
                        dbc.Row(dbc.Col(
                                dbc.Select(
                                id='dropdown-node-shape',
                                value = "ellipse",
                                options=Node_shape_items,
                                className= "form-select"
                            ), width = 12)),
                        html.Hr(),
                        dbc.Label(["Followers Color"]),
                        dbc.Input(
                            type="color",
                            id="input-follower-color",
                            value="#941D14",
                            style={"width": 100, "height": 70,"border-radius": 5, "margin-top": 5},
                        ),
                        html.Hr(),
                        dbc.Label(["following color"]),
                        dbc.Input(
                            type="color",
                            id="input-following-color",
                            value="#32A946",
                            style={"width": 100, "height": 70,"border-radius": 5, "margin-top": 5},
                        ),
                    ]),

                    dcc.Tab(label='JSON', children=[
                        html.Div(style=styles['tab'], children=[
                            html.P('Node Object JSON:'),
                            html.Pre(
                                id='tap-node-json-output',
                                style=styles['json-output']
                            ),
                            html.P('Edge Object JSON:'),
                            html.Pre(
                                id='tap-edge-json-output',
                                style=styles['json-output']
                            )
                        ])
                    ])
                ]))]),width={"size": 3})
        ])
)],
    #className="card"
    )


@app.callback(Output('tap-node-json-output', 'children'),
              [Input('cytoscape', 'tapNode')])
def display_tap_node(data):
    return json.dumps(data, indent=2)


@app.callback(Output('tap-edge-json-output', 'children'),
              [Input('cytoscape', 'tapEdge')])
def display_tap_edge(data):
    return json.dumps(data, indent=2)


@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    layout.capitalize()
    return {'name': layout}


@app.callback(Output('cytoscape', 'stylesheet'), 
              [Input('cytoscape', 'tapNode'),
               Input('input-follower-color', 'value'),
               Input('input-following-color', 'value'),
               Input('dropdown-node-shape', 'value')])
def generate_stylesheet(node, follower_color, following_color, node_shape):
    node_shape.capitalize()
    if not node:
        return default_stylesheet

    stylesheet = [{
        "selector": 'node',
        'style': {
            'opacity': 0.3,
            'shape': node_shape
        }
    }, {
        'selector': 'edge',
        'style': {
            'opacity': 0.2,
            "curve-style": "bezier",
        }
    }, {
        "selector": 'node[id = "{}"]'.format(node['data']['id']),
        "style": {
            'background-color': '#C2F50A',
            "border-color": "#C2F50A",
            "border-width": 2,
            "border-opacity": 1,
            "opacity": 1,

            "label": "data(label)",
            "color": "#C2F50A",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    }]

    for edge in node['edgesData']:
        if edge['source'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['target']),
                "style": {
                    'background-color': following_color,
                    'opacity': 0.9
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": following_color,
                    "mid-target-arrow-shape": "vee",
                    "line-color": following_color,
                    'opacity': 0.9,
                    'z-index': 5000
                }
            })

        if edge['target'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['source']),
                "style": {
                    'background-color': follower_color,
                    'opacity': 0.9,
                    'z-index': 9999
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": follower_color,
                    "mid-target-arrow-shape": "vee",
                    "line-color": follower_color,
                    'opacity': 1,
                    'z-index': 5000
                }
            })

    return stylesheet
