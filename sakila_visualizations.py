from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

# Replace 'username' and 'password' with your MySQL username and password
engine = create_engine('mysql://root:password@localhost/sakila')

# query = """
# SELECT c.name AS category, COUNT(r.rental_id) AS rental_count
# FROM category c
# JOIN film_category fc ON c.category_id = fc.category_id
# JOIN film f ON fc.film_id = f.film_id
# JOIN inventory i ON f.film_id = i.film_id
# JOIN rental r ON i.inventory_id = r.inventory_id
# GROUP BY category;
# """


queries = [
"""
SELECT c.name AS category, COUNT(r.rental_id) AS rental_count
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY category;
""",
"""
SELECT actor.first_name, actor.last_name, COUNT(*) as film_count
FROM actor
JOIN film_actor ON actor.actor_id = film_actor.actor_id
JOIN film ON film_actor.film_id = film.film_id
JOIN film_category ON film.film_id = film_category.film_id
JOIN category ON film_category.category_id = category.category_id
WHERE category.name = 'Horror'
GROUP BY actor.actor_id
ORDER BY film_count DESC
LIMIT 3;
""",
"""
SELECT category, film_id, title, rating
FROM (SELECT c.name as category, f.film_id, f.title, f.rating, RANK() OVER (PARTITION BY c.name ORDER BY f.rating DESC) AS rating_rank
FROM film AS f
JOIN film_category AS fc ON f.film_id = fc.film_id
JOIN category AS c ON fc.category_id = c.category_id
) AS film_ratings
WHERE rating_rank = 1;

""",
"""
select c.customer_id, c.first_name, p.amount
from customer as c
join payment as p on c.customer_id = p.customer_id
order by p.amount desc;
""",
"""
select actor.first_name , actor.last_name, count(film_actor.film_id) as film_count
from actor
join film_actor on actor.actor_id = film_actor.actor_id
group by actor.actor_id
having film_count > 15
order by film_count desc;

""",
"""
select f.film_id, f.title, sum(p.amount), count(*)
from film f
join inventory i on f.film_id = i.film_id
join rental r on i.inventory_id = r.inventory_id
join payment p on r.rental_id = p.rental_id
group by f.title, f.film_id
limit 5;
""",
"""
SELECT c.first_name, c.last_name, c.customer_id
FROM customer AS c
JOIN rental AS r ON c.customer_id = r.customer_id
JOIN inventory AS i ON r.inventory_id = i.inventory_id
JOIN film AS f ON i.film_id = f.film_id
JOIN film_category AS fc ON f.film_id = fc.film_id
JOIN category AS cat ON fc.category_id = cat.category_id
WHERE cat.name = 'Family';

"""
]


def buildGraph(query, title):
    data = pd.read_sql(query, engine)

    if data.empty:
        print(f"Query '{title}' returned no data, skipping plot.")
        return

    plt.figure(figsize=(10, 6))

    if 'category' in data.columns and 'rental_count' in data.columns:
        plt.bar(data['category'], data['rental_count'])
    elif 'first_name' in data.columns and 'last_name' in data.columns:
        plt.bar(data['first_name'] + ' ' + data['last_name'], data['film_count'])
    elif 'customer_id' in data.columns and 'amount' in data.columns:
        plt.scatter(data['customer_id'], data['amount'])
    else:
        plt.scatter(range(len(data)), data.iloc[:, -1])  # Last column as Y-axis

    plt.title(title)
    plt.xlabel(data.columns[0])
    plt.ylabel(data.columns[1])
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


titles = [
    "Number of Rentals by Category",
    "Top 3 Horror Movie Actors",
    "Top Rated Film in Each Category",
    "Payments by Customer",
    "Actors in More Than 15 Films",
    "Earnings by Film",
    "Family Movie Renters"
]

for query, title in zip(queries, titles):
    buildGraph(query, title)



# # Execute the SQL query and load the results into a pandas DataFrame
# rental_data = pd.read_sql(query, engine)
#
#
# # Set the figure size
# plt.figure(figsize=(10, 6))
#
# # Create a bar chart
# plt.bar(rental_data['category'], rental_data['rental_count'])
#
# # Customize the chart
# plt.title('Number of Rentals by Category')
# plt.xlabel('Category')
# plt.ylabel('Rental Count')
# plt.xticks(rotation=45)  # Rotate category labels for readability
#
# # Display the chart
# plt.tight_layout()
# plt.show()
