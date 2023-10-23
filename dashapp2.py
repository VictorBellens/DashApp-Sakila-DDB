import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

# Connect to the Sakila database
engine = create_engine('mysql://root:password@localhost/sakila')

# Define SQL queries
query1 = """
select actor.first_name , actor.last_name, count(film_actor.film_id) as film_count
from actor
join film_actor on actor.actor_id = film_actor.actor_id
group by actor.actor_id
having film_count > 15
order by film_count desc;
"""

query2 = """
select customer_id, count(*) as num_rentals
from rental
group by customer_id
order by num_rentals desc
limit 5;
"""

query3 = """
select f.film_id, f.title, sum(p.amount) as total_revenue
from film f
join inventory i on f.film_id = i.film_id
join rental r on i.inventory_id = r.inventory_id
join payment p on r.rental_id = p.rental_id
group by f.title, f.film_id;
"""

query4 = """
select actor.actor_id, count(film_actor.film_id) as film_count
from actor
join film_actor on actor.actor_id = film_actor.actor_id
group by actor.actor_id
having film_count >= 20
order by film_count desc;
"""

query5 = """
SELECT DATE(rental_date) AS rental_day, COUNT(rental_id) AS rental_count
FROM rental, inventory, film, film_category
WHERE rental.inventory_id = inventory.inventory_id AND
      inventory.film_id = film.film_id AND
      film.film_id = film_category.film_id AND
      category_id = 1
GROUP BY DATE(rental_date);

"""

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1('Sakila: SQL Tables'),
    dcc.Graph(id='actor-chart'),
    dcc.Graph(id='customer-chart'),
    dcc.Graph(id='payment-chart'),
    dcc.Graph(id='film-chart'),
    dcc.Graph(id='top-chart')
])


# Create callback to update graphs
@app.callback(
    [Output('actor-chart', 'figure'), Output('customer-chart', 'figure'), Output('payment-chart', 'figure'),
     Output('film-chart', 'figure'), Output('top-chart', 'figure')],
    Input('actor-chart', 'relayoutData')  # Dummy input for initial load
)
def update_graphs(_):
    # Fetch data and create graph for the first query
    df1 = pd.read_sql(query1, engine)
    fig1 = px.bar(df1, x=df1['first_name'] + ' ' + df1['last_name'], y='film_count',
                  title='Actors with More than 15 Films')

    # Fetch data and create graph for the second query
    df2 = pd.read_sql(query2, engine)
    fig2 = px.bar(df2, x='customer_id', y='num_rentals', title='Top 5 Customers by Number of Rentals')

    # Fetch data and create graph for the third query
    df3 = pd.read_sql(query3, engine)
    fig3 = px.bar(df3, x='title', y='total_revenue', title='Total Revenue by Film')

    df4 = pd.read_sql(query4, engine)
    fig4 = px.bar(df4, x='actor_id', y='film_count', title='Actors with 20 or More Films')

    df5 = pd.read_sql(query5, engine)
    fig5 = px.bar(df5, x='rental_day', y='rental_count', title='Rentals Count by Day for Category 1')

    return fig1, fig2, fig3, fig4, fig5


if __name__ == '__main__':
    app.run_server(debug=True)
