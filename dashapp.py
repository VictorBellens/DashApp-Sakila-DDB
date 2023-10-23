import dash
from dash import html,dcc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine

# Connect to the Sakila database
engine = create_engine('mysql://root:password@localhost/sakila')

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Sakila: Actors in more than 15 films."),
    
    # Dropdown to select a category
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Category 1', 'value': 1},
            {'label': 'Category 2', 'value': 2},
            # Add more options based on your data
        ],
        value=1  # Default selected option
    ),
    
    # Line chart to display data over time
    dcc.Graph(id='line-chart')
])

# Define callback to update the line chart based on the selected category
@app.callback(
    Output('line-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_line_chart(selected_category):
    query = """
        select actor.first_name , actor.last_name, count(film_actor.film_id) as film_count
        from actor
        join film_actor on actor.actor_id = film_actor.actor_id
        group by actor.actor_id
        having film_count > 15
        order by film_count desc;
        """

    data = pd.read_sql(query, engine)
    print(data.columns)

    fig = {
        'data': [
            {
                'x': data['first_name'] + ' ' + data['last_name'],
                'y': data['film_count'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Film Count for Actors with more than 15 Films',
            'xaxis': {'title': 'Actor'},
            'yaxis': {'title': 'Film Count'}
        }
    }

    return fig

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)