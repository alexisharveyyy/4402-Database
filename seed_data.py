"""
Data generation script using Faker library.
Generates realistic synthetic data for the restaurant database.
"""

import random
from datetime import datetime, timedelta, date, time
from typing import List, Tuple
from faker import Faker

from database import get_db_cursor, init_database, check_database_exists

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible data
random.seed(42)


# ============================================
# Menu Data Constants
# ============================================

MENU_DATA = {
    "Appetizers": [
        ("Crispy Calamari", "Lightly breaded and fried, served with marinara sauce", 14.99),
        ("Bruschetta", "Grilled bread topped with tomatoes, basil, and balsamic glaze", 9.99),
        ("Spinach Artichoke Dip", "Creamy blend served with tortilla chips", 12.99),
        ("Soup of the Day", "Ask your server for today's selection", 7.99),
        ("Stuffed Mushrooms", "Filled with crab meat and cream cheese", 13.99),
        ("Shrimp Cocktail", "Six jumbo shrimp with cocktail sauce", 16.99),
        ("Chicken Wings", "Choice of buffalo, BBQ, or garlic parmesan", 14.99),
        ("Loaded Nachos", "Topped with cheese, jalapeños, sour cream, and guacamole", 15.99),
    ],
    "Salads": [
        ("Caesar Salad", "Romaine lettuce, parmesan, croutons, caesar dressing", 11.99),
        ("House Salad", "Mixed greens with cherry tomatoes and balsamic vinaigrette", 9.99),
        ("Greek Salad", "Cucumber, tomatoes, olives, feta cheese, red onion", 12.99),
        ("Cobb Salad", "Chicken, bacon, avocado, egg, blue cheese", 16.99),
        ("Wedge Salad", "Iceberg lettuce with blue cheese and bacon", 11.99),
        ("Caprese Salad", "Fresh mozzarella, tomatoes, and basil", 13.99),
    ],
    "Entrees": [
        ("Grilled Salmon", "Atlantic salmon with lemon butter sauce, seasonal vegetables", 28.99),
        ("Filet Mignon", "8oz center-cut filet with red wine reduction", 42.99),
        ("New York Strip", "12oz prime cut with herb butter", 38.99),
        ("Chicken Parmesan", "Breaded chicken breast with marinara and mozzarella", 22.99),
        ("Lobster Tail", "8oz tail with drawn butter and lemon", 48.99),
        ("Rack of Lamb", "Herb-crusted with mint jelly", 44.99),
        ("Seafood Pasta", "Shrimp, scallops, and mussels in garlic cream sauce", 32.99),
        ("Vegetable Risotto", "Arborio rice with seasonal vegetables and parmesan", 19.99),
        ("BBQ Baby Back Ribs", "Full rack with house-made BBQ sauce", 29.99),
        ("Pan-Seared Duck", "With cherry reduction and wild rice", 34.99),
        ("Catch of the Day", "Fresh fish prepared to chef's specifications", 32.99),
        ("Prime Rib", "Slow-roasted 14oz cut with au jus", 39.99),
    ],
    "Sides": [
        ("Mashed Potatoes", "Creamy garlic mashed potatoes", 6.99),
        ("Grilled Asparagus", "With lemon and olive oil", 7.99),
        ("Mac and Cheese", "Four-cheese blend with breadcrumb topping", 8.99),
        ("Sautéed Spinach", "With garlic and olive oil", 6.99),
        ("Baked Potato", "With butter, sour cream, and chives", 5.99),
        ("French Fries", "Crispy seasoned fries", 5.99),
        ("Onion Rings", "Beer-battered and fried", 7.99),
        ("Roasted Brussels Sprouts", "With bacon and balsamic", 8.99),
    ],
    "Desserts": [
        ("Chocolate Lava Cake", "Warm chocolate cake with molten center", 10.99),
        ("New York Cheesecake", "Classic style with berry compote", 9.99),
        ("Crème Brûlée", "Classic vanilla custard with caramelized sugar", 9.99),
        ("Tiramisu", "Espresso-soaked ladyfingers with mascarpone", 10.99),
        ("Apple Pie à la Mode", "Warm apple pie with vanilla ice cream", 8.99),
        ("Ice Cream Sundae", "Three scoops with chocolate sauce and whipped cream", 7.99),
        ("Key Lime Pie", "Tangy and sweet with whipped cream", 8.99),
    ],
    "Beverages": [
        ("Soft Drinks", "Coca-Cola products, refills included", 3.49),
        ("Fresh Lemonade", "House-made with fresh lemons", 4.49),
        ("Iced Tea", "Sweetened or unsweetened", 3.49),
        ("Coffee", "Regular or decaf", 3.99),
        ("Espresso", "Single or double shot", 4.49),
        ("Hot Tea", "Selection of premium teas", 3.99),
        ("Juice", "Orange, apple, or cranberry", 4.49),
        ("Sparkling Water", "San Pellegrino", 4.99),
    ],
}


def generate_customers(count: int = 50) -> List[Tuple]:
    """
    Generate synthetic customer data.
    
    Args:
        count: Number of customers to generate.
        
    Returns:
        List of customer tuples (first_name, last_name, phone, email).
    """
    customers = []
    used_emails = set()
    
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()[:20]
        
        # Generate unique email
        base_email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
        email = base_email
        counter = 1
        while email in used_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@{fake.free_email_domain()}"
            counter += 1
        used_emails.add(email)
        
        customers.append((first_name, last_name, phone, email))
    
    return customers


def generate_employees(count: int = 20) -> List[Tuple]:
    """
    Generate synthetic employee data with appropriate role distribution.
    
    Args:
        count: Number of employees to generate.
        
    Returns:
        List of employee tuples.
    """
    # Role distribution: 2 Managers, 2 Hosts, 8 Servers, 3 Bartenders, 5 Cooks
    roles = ['Manager'] * 2 + ['Host'] * 2 + ['Server'] * 8 + ['Bartender'] * 3 + ['Cook'] * 5
    random.shuffle(roles)
    roles = roles[:count]
    
    # Wage ranges by role
    wage_ranges = {
        'Manager': (25.00, 35.00),
        'Host': (12.00, 15.00),
        'Server': (2.13, 5.00),  # Server minimum wage (tips expected)
        'Bartender': (7.50, 12.00),
        'Cook': (14.00, 22.00),
    }
    
    employees = []
    used_emails = set()
    
    for i, role in enumerate(roles):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()[:20]
        
        # Generate unique email
        base_email = f"{first_name.lower()}.{last_name.lower()}@restaurant.com"
        email = base_email
        counter = 1
        while email in used_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@restaurant.com"
            counter += 1
        used_emails.add(email)
        
        # Generate hire date within the past 5 years
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        
        # Generate hourly wage based on role
        min_wage, max_wage = wage_ranges[role]
        hourly_wage = round(random.uniform(min_wage, max_wage), 2)
        
        employees.append((first_name, last_name, role, phone, email, hire_date, hourly_wage))
    
    return employees


def generate_tables(count: int = 18) -> List[Tuple]:
    """
    Generate restaurant table data.
    
    Args:
        count: Number of tables to generate.
        
    Returns:
        List of table tuples.
    """
    tables = []
    locations = ['Main Dining', 'Main Dining', 'Main Dining', 'Patio', 'Bar Area', 'Private Room']
    
    # Table configurations by location
    table_configs = {
        'Main Dining': [(2, 4), (4, 6), (4, 4), (6, 2)],  # (capacity, count)
        'Patio': [(2, 2), (4, 2)],
        'Bar Area': [(2, 2), (4, 1)],
        'Private Room': [(8, 1), (12, 1)],
    }
    
    table_num = 1
    for location, configs in table_configs.items():
        for capacity, num_tables in configs:
            for _ in range(num_tables):
                if len(tables) >= count:
                    break
                tables.append((f"T{table_num:02d}", capacity, location))
                table_num += 1
    
    return tables[:count]


def generate_shifts(employee_ids: List[int], days: int = 30) -> List[Tuple]:
    """
    Generate employee shift schedules.
    
    Args:
        employee_ids: List of employee IDs.
        days: Number of days to generate shifts for.
        
    Returns:
        List of shift tuples.
    """
    shifts = []
    today = date.today()
    
    # Shift templates
    shift_templates = [
        (time(10, 0), time(16, 0)),   # Morning shift
        (time(16, 0), time(22, 0)),   # Evening shift
        (time(11, 0), time(19, 0)),   # Mid shift
        (time(17, 0), time(23, 0)),   # Late shift
    ]
    
    for day_offset in range(-days, 14):  # Past month plus next 2 weeks
        shift_date = today + timedelta(days=day_offset)
        
        # Skip some random days for each employee
        working_employees = random.sample(employee_ids, k=int(len(employee_ids) * 0.7))
        
        for emp_id in working_employees:
            shift = random.choice(shift_templates)
            shifts.append((emp_id, shift_date, shift[0].strftime('%H:%M'), shift[1].strftime('%H:%M')))
    
    return shifts


def generate_reservations(customer_ids: List[int], table_ids: List[int], 
                          table_capacities: dict, days: int = 14) -> List[Tuple]:
    """
    Generate reservations for upcoming weeks.
    
    Args:
        customer_ids: List of customer IDs.
        table_ids: List of table IDs.
        table_capacities: Dictionary mapping table_id to capacity.
        days: Number of days ahead to generate reservations.
        
    Returns:
        List of reservation tuples.
    """
    reservations = []
    today = date.today()
    
    reservation_times = ['17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']
    statuses = ['Confirmed'] * 8 + ['Cancelled'] + ['No-Show']
    special_requests = [
        None, None, None, None,  # Most have no special requests
        "Birthday celebration - please bring cake",
        "Anniversary dinner",
        "Allergic to shellfish",
        "Gluten-free options needed",
        "High chair needed",
        "Window seat preferred",
        "Quiet table please",
    ]
    
    for day_offset in range(1, days + 1):
        res_date = today + timedelta(days=day_offset)
        
        # Skip some days (restaurant might be less busy)
        if random.random() < 0.1:
            continue
        
        # 3-8 reservations per day
        num_reservations = random.randint(3, 8)
        day_tables_used = {}  # Track tables used at each time
        
        for _ in range(num_reservations):
            customer_id = random.choice(customer_ids)
            table_id = random.choice(table_ids)
            res_time = random.choice(reservation_times)
            
            # Avoid double-booking same table at same time
            time_key = (table_id, res_time)
            if time_key in day_tables_used:
                continue
            day_tables_used[time_key] = True
            
            capacity = table_capacities.get(table_id, 4)
            party_size = random.randint(1, capacity)
            status = random.choice(statuses)
            special_request = random.choice(special_requests)
            
            reservations.append((
                customer_id, table_id, res_date, res_time,
                party_size, status, special_request
            ))
    
    return reservations


def generate_orders_and_items(customer_ids: List[int], server_ids: List[int],
                               table_ids: List[int], menu_items: List[dict],
                               count: int = 150) -> Tuple[List[Tuple], List[Tuple]]:
    """
    Generate orders and order items for the past few months.
    
    Args:
        customer_ids: List of customer IDs.
        server_ids: List of server employee IDs.
        table_ids: List of table IDs.
        menu_items: List of menu item dictionaries.
        count: Number of orders to generate.
        
    Returns:
        Tuple of (orders list, order_items list).
    """
    orders = []
    order_items = []
    
    today = date.today()
    order_types = ['Dine-In'] * 7 + ['Takeout'] * 2 + ['Bar']
    order_times = [
        '11:30', '12:00', '12:30', '13:00',  # Lunch
        '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'  # Dinner
    ]
    
    for order_idx in range(count):
        # Order date within past 90 days
        days_ago = random.randint(0, 90)
        order_date = today - timedelta(days=days_ago)
        order_time = random.choice(order_times)
        
        order_type = random.choice(order_types)
        customer_id = random.choice(customer_ids) if random.random() > 0.3 else None
        server_id = random.choice(server_ids)
        table_id = random.choice(table_ids) if order_type == 'Dine-In' else None
        
        # Status: older orders are completed
        if days_ago > 1:
            status = 'Completed'
        else:
            status = random.choice(['Open', 'In Progress', 'Completed'])
        
        # Tip percentage (15-25% typically)
        tip_percentage = random.uniform(0.15, 0.25) if status == 'Completed' else 0
        
        orders.append((
            customer_id, server_id, table_id, order_type,
            status, order_date, order_time
        ))
        
        # Generate 2-6 items per order
        num_items = random.randint(2, 6)
        selected_items = random.sample(menu_items, min(num_items, len(menu_items)))
        
        for item in selected_items:
            quantity = random.randint(1, 3) if item['category'] != 'Beverages' else random.randint(1, 4)
            order_items.append((
                order_idx + 1,  # Placeholder for order_id (will be actual ID after insert)
                item['id'],
                quantity,
                item['price'],
                random.choice([None, None, None, "No onions", "Extra sauce", "Well done"]),
            ))
    
    return orders, order_items


def seed_database() -> dict:
    """
    Main function to seed the database with all generated data.
    
    Returns:
        Dictionary with counts of inserted records.
    """
    # Initialize database if needed
    if not check_database_exists():
        init_database()
    
    counts = {}
    
    with get_db_cursor() as (conn, cursor):
        # 1. Insert Categories
        print("Seeding categories...")
        categories = list(MENU_DATA.keys())
        for cat_name in categories:
            cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (cat_name, f"Our selection of {cat_name.lower()}")
            )
        counts['categories'] = len(categories)
        
        # Get category IDs
        cursor.execute("SELECT category_id, name FROM categories")
        category_map = {row['name']: row['category_id'] for row in cursor.fetchall()}
        
        # 2. Insert Menu Items
        print("Seeding menu items...")
        menu_items = []
        for category_name, items in MENU_DATA.items():
            category_id = category_map[category_name]
            for name, description, price in items:
                cursor.execute(
                    "INSERT INTO menu_items (name, description, price, category_id) VALUES (?, ?, ?, ?)",
                    (name, description, price, category_id)
                )
                menu_items.append({
                    'id': cursor.lastrowid,
                    'name': name,
                    'price': price,
                    'category': category_name
                })
        counts['menu_items'] = len(menu_items)
        
        # 3. Insert Customers
        print("Seeding customers...")
        customers = generate_customers(50)
        cursor.executemany(
            "INSERT INTO customers (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)",
            customers
        )
        counts['customers'] = len(customers)
        
        # Get customer IDs
        cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row['customer_id'] for row in cursor.fetchall()]
        
        # 4. Insert Employees
        print("Seeding employees...")
        employees = generate_employees(20)
        for emp in employees:
            cursor.execute(
                """INSERT INTO employees 
                   (first_name, last_name, role, phone, email, hire_date, hourly_wage) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                emp
            )
        counts['employees'] = len(employees)
        
        # Set manager relationships
        cursor.execute("SELECT employee_id FROM employees WHERE role = 'Manager'")
        manager_ids = [row['employee_id'] for row in cursor.fetchall()]
        
        if manager_ids:
            cursor.execute("SELECT employee_id FROM employees WHERE role != 'Manager'")
            non_managers = [row['employee_id'] for row in cursor.fetchall()]
            for emp_id in non_managers:
                manager_id = random.choice(manager_ids)
                cursor.execute(
                    "UPDATE employees SET manager_id = ? WHERE employee_id = ?",
                    (manager_id, emp_id)
                )
        
        # Get server IDs
        cursor.execute("SELECT employee_id FROM employees WHERE role IN ('Server', 'Bartender')")
        server_ids = [row['employee_id'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT employee_id FROM employees")
        all_employee_ids = [row['employee_id'] for row in cursor.fetchall()]
        
        # 5. Insert Tables
        print("Seeding tables...")
        tables = generate_tables(18)
        cursor.executemany(
            "INSERT INTO tables (table_number, capacity, location) VALUES (?, ?, ?)",
            tables
        )
        counts['tables'] = len(tables)
        
        # Get table IDs and capacities
        cursor.execute("SELECT table_id, capacity FROM tables")
        table_data = cursor.fetchall()
        table_ids = [row['table_id'] for row in table_data]
        table_capacities = {row['table_id']: row['capacity'] for row in table_data}
        
        # 6. Insert Shifts
        print("Seeding shifts...")
        shifts = generate_shifts(all_employee_ids, 30)
        cursor.executemany(
            "INSERT INTO shifts (employee_id, shift_date, start_time, end_time) VALUES (?, ?, ?, ?)",
            shifts
        )
        counts['shifts'] = len(shifts)
        
        # 7. Insert Reservations
        print("Seeding reservations...")
        reservations = generate_reservations(customer_ids, table_ids, table_capacities, 14)
        cursor.executemany(
            """INSERT INTO reservations 
               (customer_id, table_id, reservation_date, reservation_time, 
                party_size, status, special_requests) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            reservations
        )
        counts['reservations'] = len(reservations)
        
        # 8. Insert Orders and Order Items
        print("Seeding orders...")
        orders, order_items_template = generate_orders_and_items(
            customer_ids, server_ids, table_ids, menu_items, 150
        )
        
        # Insert orders and track their IDs
        order_id_map = {}
        for idx, order in enumerate(orders):
            cursor.execute(
                """INSERT INTO orders 
                   (customer_id, employee_id, table_id, order_type, status, order_date, order_time)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                order
            )
            order_id_map[idx + 1] = cursor.lastrowid
        counts['orders'] = len(orders)
        
        print("Seeding order items...")
        # Update order items with actual order IDs and insert
        for item in order_items_template:
            actual_order_id = order_id_map[item[0]]
            cursor.execute(
                """INSERT INTO order_items 
                   (order_id, item_id, quantity, unit_price, special_instructions)
                   VALUES (?, ?, ?, ?, ?)""",
                (actual_order_id, item[1], item[2], item[3], item[4])
            )
        counts['order_items'] = len(order_items_template)
        
        # Update order tips for completed orders
        print("Updating order totals...")
        cursor.execute("""
            UPDATE orders 
            SET tip = ROUND(subtotal * (0.15 + (RANDOM() % 11) / 100.0), 2),
                total = total + ROUND(subtotal * (0.15 + (RANDOM() % 11) / 100.0), 2)
            WHERE status = 'Completed'
        """)
    
    print("\n✓ Database seeding completed successfully!")
    print("\nRecord counts:")
    for table, count in counts.items():
        print(f"  {table}: {count}")
    
    return counts


if __name__ == "__main__":
    seed_database()

