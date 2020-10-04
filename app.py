import dash
import dash_core_components as dcc
import dash_html_components as html


def start_app(fig):
  external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

  app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

  app.layout = html.Div(children=[
    html.H1(children='Basket Tracker'),

    dcc.Graph(
      id='example-graph',
      figure=fig
    )
  ])
  print('Go to http://localhost:8050')
  app.run_server()