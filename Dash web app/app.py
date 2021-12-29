import dash

# meta_tags are required for the app layout to be mobile responsive
                
app = dash.Dash(__name__,suppress_callback_exceptions=True)
server = app.server
app.title = "DeepSearch Lab"