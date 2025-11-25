"""
Command-Line Interface for Restaurant Database Management.
Built with Typer for a modern CLI experience.

Usage:
    python cli.py --help                    # Show all commands
    python cli.py init                      # Initialize database
    python cli.py host reservation create   # Create reservation
    python cli.py server order create       # Create order
    python cli.py manager report            # View reports
"""

import typer
from typing import Optional
from datetime import date, datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from database import (
    init_database, check_database_exists, reset_database,
    get_db_cursor, get_table_counts
)
from seed_data import seed_database
from queries import (
    get_revenue_by_server, get_popular_menu_items,
    get_above_average_customers, get_daily_revenue,
    get_revenue_by_category, get_upcoming_reservations
)

# Initialize Typer app and Rich console
app = typer.Typer(
    name="restaurant",
    help="Restaurant Database Management CLI",
    add_completion=False
)
host_app = typer.Typer(help="Host commands for reservations and tables")
server_app = typer.Typer(help="Server commands for orders")
manager_app = typer.Typer(help="Manager commands for reports and menu")

app.add_typer(host_app, name="host")
app.add_typer(server_app, name="server")
app.add_typer(manager_app, name="manager")

console = Console()


# ============================================
# Database Initialization Commands
# ============================================

@app.command()
def init(seed: bool = typer.Option(False, "--seed", "-s", help="Seed database with sample data")):
    """Initialize the database schema."""
    if check_database_exists():
        if not typer.confirm("Database already exists. Reinitialize?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()
        reset_database()
    else:
        init_database()
    
    if seed:
        seed_database()
    
    console.print("[green]✓ Database initialized successfully![/green]")


@app.command()
def seed():
    """Seed the database with sample data."""
    if not check_database_exists():
        console.print("[yellow]Database not found. Initializing first...[/yellow]")
        init_database()
    
    seed_database()
    console.print("[green]✓ Database seeded successfully![/green]")


@app.command()
def status():
    """Show database status and record counts."""
    if not check_database_exists():
        console.print("[red]✗ Database not initialized. Run 'python cli.py init' first.[/red]")
        raise typer.Exit(1)
    
    counts = get_table_counts()
    
    table = Table(title="Database Status", box=box.ROUNDED)
    table.add_column("Table", style="cyan")
    table.add_column("Record Count", justify="right", style="green")
    
    for table_name, count in counts.items():
        table.add_row(table_name, str(count))
    
    console.print(table)


# ============================================
# Host Commands
# ============================================

@host_app.command("tables")
def view_available_tables(
    date_str: str = typer.Argument(..., help="Date to check (YYYY-MM-DD)"),
    time_str: str = typer.Argument(..., help="Time to check (HH:MM)")
):
    """View available tables for a given date and time."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    try:
        # Validate date and time format
        datetime.strptime(date_str, "%Y-%m-%d")
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        console.print("[red]Invalid date/time format. Use YYYY-MM-DD and HH:MM.[/red]")
        raise typer.Exit(1)
    
    query = """
        SELECT t.table_id, t.table_number, t.capacity, t.location
        FROM tables t
        WHERE t.is_active = 1
          AND t.table_id NOT IN (
              SELECT r.table_id
              FROM reservations r
              WHERE r.reservation_date = ?
                AND r.reservation_time BETWEEN time(?, '-1 hour') AND time(?, '+1 hour')
                AND r.status IN ('Confirmed', 'Seated')
          )
        ORDER BY t.location, t.capacity
    """
    
    with get_db_cursor() as (conn, cursor):
        cursor.execute(query, (date_str, time_str, time_str))
        results = cursor.fetchall()
    
    if not results:
        console.print(f"[yellow]No tables available for {date_str} at {time_str}.[/yellow]")
        return
    
    table = Table(title=f"Available Tables - {date_str} at {time_str}", box=box.ROUNDED)
    table.add_column("Table #", style="cyan")
    table.add_column("Capacity", justify="center")
    table.add_column("Location", style="green")
    
    for row in results:
        table.add_row(row['table_number'], str(row['capacity']), row['location'])
    
    console.print(table)


@host_app.command("reservation")
def create_reservation(
    customer_id: int = typer.Option(..., "--customer", "-c", help="Customer ID"),
    table_id: int = typer.Option(..., "--table", "-t", help="Table ID"),
    date_str: str = typer.Option(..., "--date", "-d", help="Reservation date (YYYY-MM-DD)"),
    time_str: str = typer.Option(..., "--time", help="Reservation time (HH:MM)"),
    party_size: int = typer.Option(..., "--party", "-p", help="Number of guests"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Special requests")
):
    """Create a new reservation."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    try:
        res_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        console.print("[red]Invalid date/time format. Use YYYY-MM-DD and HH:MM.[/red]")
        raise typer.Exit(1)
    
    if res_date < date.today():
        console.print("[red]Cannot create reservation for past date.[/red]")
        raise typer.Exit(1)
    
    if party_size < 1:
        console.print("[red]Party size must be at least 1.[/red]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        # Verify customer exists
        cursor.execute("SELECT customer_id, first_name, last_name FROM customers WHERE customer_id = ?", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            console.print(f"[red]Customer ID {customer_id} not found.[/red]")
            raise typer.Exit(1)
        
        # Verify table exists and check capacity
        cursor.execute("SELECT table_id, table_number, capacity FROM tables WHERE table_id = ?", (table_id,))
        table_info = cursor.fetchone()
        if not table_info:
            console.print(f"[red]Table ID {table_id} not found.[/red]")
            raise typer.Exit(1)
        
        if party_size > table_info['capacity']:
            console.print(f"[yellow]Warning: Party size ({party_size}) exceeds table capacity ({table_info['capacity']}).[/yellow]")
            if not typer.confirm("Continue anyway?"):
                raise typer.Exit()
        
        # Check for conflicts
        cursor.execute("""
            SELECT reservation_id FROM reservations
            WHERE table_id = ? AND reservation_date = ?
              AND reservation_time BETWEEN time(?, '-1 hour') AND time(?, '+1 hour')
              AND status IN ('Confirmed', 'Seated')
        """, (table_id, date_str, time_str, time_str))
        
        if cursor.fetchone():
            console.print("[red]Table already reserved at this time.[/red]")
            raise typer.Exit(1)
        
        # Create reservation
        cursor.execute("""
            INSERT INTO reservations 
            (customer_id, table_id, reservation_date, reservation_time, party_size, special_requests)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_id, table_id, date_str, time_str, party_size, notes))
        
        reservation_id = cursor.lastrowid
    
    console.print(Panel(
        f"[green]Reservation created successfully![/green]\n\n"
        f"Reservation ID: {reservation_id}\n"
        f"Customer: {customer['first_name']} {customer['last_name']}\n"
        f"Table: {table_info['table_number']}\n"
        f"Date: {date_str} at {time_str}\n"
        f"Party Size: {party_size}",
        title="✓ New Reservation"
    ))


@host_app.command("reservations")
def list_reservations(
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Filter by date (YYYY-MM-DD)")
):
    """List upcoming reservations."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    results = get_upcoming_reservations()
    
    if date_str:
        results = [r for r in results if str(r['reservation_date']) == date_str]
    
    if not results:
        console.print("[yellow]No upcoming reservations found.[/yellow]")
        return
    
    table = Table(title="Upcoming Reservations", box=box.ROUNDED)
    table.add_column("ID", style="dim")
    table.add_column("Date")
    table.add_column("Time")
    table.add_column("Customer", style="cyan")
    table.add_column("Table")
    table.add_column("Party", justify="center")
    table.add_column("Notes", style="dim")
    
    for row in results[:20]:
        table.add_row(
            str(row['reservation_id']),
            str(row['reservation_date']),
            str(row['reservation_time']),
            row['customer_name'],
            row['table_number'],
            str(row['party_size']),
            (row['special_requests'] or "")[:30]
        )
    
    console.print(table)


# ============================================
# Server Commands
# ============================================

@server_app.command("order")
def create_order(
    employee_id: int = typer.Option(..., "--server", "-s", help="Server employee ID"),
    table_id: Optional[int] = typer.Option(None, "--table", "-t", help="Table ID (for dine-in)"),
    customer_id: Optional[int] = typer.Option(None, "--customer", "-c", help="Customer ID"),
    order_type: str = typer.Option("Dine-In", "--type", help="Order type: Dine-In, Takeout, Bar")
):
    """Create a new order."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    if order_type not in ['Dine-In', 'Takeout', 'Bar']:
        console.print("[red]Invalid order type. Use: Dine-In, Takeout, or Bar[/red]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        # Verify server exists
        cursor.execute("""
            SELECT employee_id, first_name, last_name, role 
            FROM employees WHERE employee_id = ?
        """, (employee_id,))
        server = cursor.fetchone()
        if not server:
            console.print(f"[red]Employee ID {employee_id} not found.[/red]")
            raise typer.Exit(1)
        
        if server['role'] not in ['Server', 'Bartender', 'Manager']:
            console.print(f"[yellow]Warning: {server['first_name']} is a {server['role']}, not a Server.[/yellow]")
        
        # Create order
        today = date.today()
        now = datetime.now().strftime("%H:%M")
        
        cursor.execute("""
            INSERT INTO orders 
            (customer_id, employee_id, table_id, order_type, status, order_date, order_time)
            VALUES (?, ?, ?, ?, 'Open', ?, ?)
        """, (customer_id, employee_id, table_id, order_type, today, now))
        
        order_id = cursor.lastrowid
    
    console.print(Panel(
        f"[green]Order created successfully![/green]\n\n"
        f"Order ID: {order_id}\n"
        f"Server: {server['first_name']} {server['last_name']}\n"
        f"Type: {order_type}\n"
        f"Status: Open\n\n"
        f"[dim]Use 'python cli.py server add-item --order {order_id} --item <ID> --qty <N>' to add items.[/dim]",
        title="✓ New Order"
    ))


@server_app.command("add-item")
def add_order_item(
    order_id: int = typer.Option(..., "--order", "-o", help="Order ID"),
    item_id: int = typer.Option(..., "--item", "-i", help="Menu item ID"),
    quantity: int = typer.Option(1, "--qty", "-q", help="Quantity"),
    notes: Optional[str] = typer.Option(None, "--notes", "-n", help="Special instructions")
):
    """Add an item to an existing order."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    if quantity < 1:
        console.print("[red]Quantity must be at least 1.[/red]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        # Verify order exists and is open
        cursor.execute("SELECT order_id, status FROM orders WHERE order_id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            console.print(f"[red]Order ID {order_id} not found.[/red]")
            raise typer.Exit(1)
        
        if order['status'] in ['Completed', 'Cancelled']:
            console.print(f"[red]Cannot modify {order['status'].lower()} order.[/red]")
            raise typer.Exit(1)
        
        # Verify menu item exists
        cursor.execute("""
            SELECT item_id, name, price, is_available 
            FROM menu_items WHERE item_id = ?
        """, (item_id,))
        item = cursor.fetchone()
        if not item:
            console.print(f"[red]Menu item ID {item_id} not found.[/red]")
            raise typer.Exit(1)
        
        if not item['is_available']:
            console.print(f"[yellow]{item['name']} is currently unavailable.[/yellow]")
            if not typer.confirm("Add anyway?"):
                raise typer.Exit()
        
        # Add item to order
        cursor.execute("""
            INSERT INTO order_items (order_id, item_id, quantity, unit_price, special_instructions)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, item_id, quantity, item['price'], notes))
        
        # Get updated order total
        cursor.execute("SELECT total FROM orders WHERE order_id = ?", (order_id,))
        new_total = cursor.fetchone()['total']
    
    console.print(Panel(
        f"[green]Item added to order![/green]\n\n"
        f"Item: {item['name']}\n"
        f"Quantity: {quantity}\n"
        f"Unit Price: ${item['price']:.2f}\n"
        f"Item Total: ${item['price'] * quantity:.2f}\n\n"
        f"[bold]New Order Total: ${new_total:.2f}[/bold]",
        title="✓ Item Added"
    ))


@server_app.command("menu")
def view_menu(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category")
):
    """View the menu."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    query = """
        SELECT mi.item_id, mi.name, mi.description, mi.price, 
               c.name AS category, mi.is_available
        FROM menu_items mi
        JOIN categories c ON mi.category_id = c.category_id
    """
    params = []
    
    if category:
        query += " WHERE c.name LIKE ?"
        params.append(f"%{category}%")
    
    query += " ORDER BY c.name, mi.name"
    
    with get_db_cursor() as (conn, cursor):
        cursor.execute(query, params)
        results = cursor.fetchall()
    
    if not results:
        console.print("[yellow]No menu items found.[/yellow]")
        return
    
    # Group by category
    current_category = None
    table = None
    
    for row in results:
        if row['category'] != current_category:
            if table:
                console.print(table)
                console.print()
            current_category = row['category']
            table = Table(title=current_category, box=box.ROUNDED)
            table.add_column("ID", style="dim", width=4)
            table.add_column("Item", style="cyan", width=30)
            table.add_column("Price", justify="right", width=10)
            table.add_column("Available", justify="center", width=10)
        
        status = "✓" if row['is_available'] else "✗"
        status_style = "green" if row['is_available'] else "red"
        table.add_row(
            str(row['item_id']),
            row['name'],
            f"${row['price']:.2f}",
            f"[{status_style}]{status}[/{status_style}]"
        )
    
    if table:
        console.print(table)


# ============================================
# Manager Commands
# ============================================

@manager_app.command("report")
def sales_report(
    report_type: str = typer.Option("daily", "--type", "-t", help="Report type: daily, category, server"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days for daily report")
):
    """View sales reports."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    if report_type == "daily":
        results = get_daily_revenue(days)
        if not results:
            console.print("[yellow]No sales data found.[/yellow]")
            return
        
        table = Table(title=f"Daily Revenue Report (Last {days} Days)", box=box.ROUNDED)
        table.add_column("Date")
        table.add_column("Orders", justify="right")
        table.add_column("Subtotal", justify="right")
        table.add_column("Tax", justify="right")
        table.add_column("Tips", justify="right")
        table.add_column("Total", justify="right", style="green")
        
        total_revenue = 0
        for row in results:
            table.add_row(
                str(row['order_date']),
                str(row['order_count']),
                f"${row['subtotal']:.2f}",
                f"${row['tax']:.2f}",
                f"${row['tips']:.2f}",
                f"${row['daily_total']:.2f}"
            )
            total_revenue += row['daily_total']
        
        console.print(table)
        console.print(f"\n[bold green]Total Revenue: ${total_revenue:.2f}[/bold green]")
    
    elif report_type == "category":
        results = get_revenue_by_category()
        if not results:
            console.print("[yellow]No sales data found.[/yellow]")
            return
        
        table = Table(title="Revenue by Category", box=box.ROUNDED)
        table.add_column("Category")
        table.add_column("Orders", justify="right")
        table.add_column("Items Sold", justify="right")
        table.add_column("Revenue", justify="right", style="green")
        
        for row in results:
            table.add_row(
                row['category'],
                str(row['order_count']),
                str(row['items_sold']),
                f"${row['category_revenue']:.2f}"
            )
        
        console.print(table)
    
    elif report_type == "server":
        results = get_revenue_by_server()
        if not results:
            console.print("[yellow]No sales data found.[/yellow]")
            return
        
        table = Table(title="Revenue by Server", box=box.ROUNDED)
        table.add_column("Server")
        table.add_column("Role")
        table.add_column("Orders", justify="right")
        table.add_column("Sales", justify="right")
        table.add_column("Tips", justify="right")
        table.add_column("Total", justify="right", style="green")
        
        for row in results:
            table.add_row(
                row['server_name'],
                row['role'],
                str(row['total_orders']),
                f"${row['gross_sales']:.2f}",
                f"${row['total_tips']:.2f}",
                f"${row['total_revenue']:.2f}"
            )
        
        console.print(table)
    
    else:
        console.print(f"[red]Unknown report type: {report_type}[/red]")
        console.print("[dim]Available: daily, category, server[/dim]")


@manager_app.command("menu-add")
def add_menu_item(
    name: str = typer.Option(..., "--name", "-n", help="Item name"),
    price: float = typer.Option(..., "--price", "-p", help="Item price"),
    category_id: int = typer.Option(..., "--category", "-c", help="Category ID"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Item description")
):
    """Add a new menu item."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    if price <= 0:
        console.print("[red]Price must be greater than 0.[/red]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        # Verify category exists
        cursor.execute("SELECT category_id, name FROM categories WHERE category_id = ?", (category_id,))
        category = cursor.fetchone()
        if not category:
            console.print(f"[red]Category ID {category_id} not found.[/red]")
            # Show available categories
            cursor.execute("SELECT category_id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
            console.print("\nAvailable categories:")
            for cat in categories:
                console.print(f"  {cat['category_id']}: {cat['name']}")
            raise typer.Exit(1)
        
        # Insert menu item
        cursor.execute("""
            INSERT INTO menu_items (name, description, price, category_id)
            VALUES (?, ?, ?, ?)
        """, (name, description, price, category_id))
        
        item_id = cursor.lastrowid
    
    console.print(Panel(
        f"[green]Menu item added successfully![/green]\n\n"
        f"ID: {item_id}\n"
        f"Name: {name}\n"
        f"Category: {category['name']}\n"
        f"Price: ${price:.2f}",
        title="✓ New Menu Item"
    ))


@manager_app.command("menu-update")
def update_menu_item(
    item_id: int = typer.Option(..., "--id", "-i", help="Menu item ID to update"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="New price"),
    available: Optional[bool] = typer.Option(None, "--available", "-a", help="Set availability"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="New description")
):
    """Update an existing menu item."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    if price is None and available is None and description is None:
        console.print("[yellow]No updates specified. Use --price, --available, or --desc.[/yellow]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        # Verify item exists
        cursor.execute("SELECT * FROM menu_items WHERE item_id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            console.print(f"[red]Menu item ID {item_id} not found.[/red]")
            raise typer.Exit(1)
        
        # Build update query
        updates = []
        params = []
        
        if price is not None:
            if price <= 0:
                console.print("[red]Price must be greater than 0.[/red]")
                raise typer.Exit(1)
            updates.append("price = ?")
            params.append(price)
        
        if available is not None:
            updates.append("is_available = ?")
            params.append(1 if available else 0)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        params.append(item_id)
        query = f"UPDATE menu_items SET {', '.join(updates)} WHERE item_id = ?"
        cursor.execute(query, params)
        
        # Get updated item
        cursor.execute("""
            SELECT mi.*, c.name AS category_name 
            FROM menu_items mi
            JOIN categories c ON mi.category_id = c.category_id
            WHERE mi.item_id = ?
        """, (item_id,))
        updated = cursor.fetchone()
    
    console.print(Panel(
        f"[green]Menu item updated![/green]\n\n"
        f"ID: {updated['item_id']}\n"
        f"Name: {updated['name']}\n"
        f"Category: {updated['category_name']}\n"
        f"Price: ${updated['price']:.2f}\n"
        f"Available: {'Yes' if updated['is_available'] else 'No'}",
        title="✓ Updated Menu Item"
    ))


@manager_app.command("employees")
def list_employees():
    """List all employees."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    with get_db_cursor() as (conn, cursor):
        cursor.execute("""
            SELECT e.employee_id, e.first_name || ' ' || e.last_name AS name,
                   e.role, e.email, e.hire_date, e.hourly_wage,
                   m.first_name || ' ' || m.last_name AS manager_name
            FROM employees e
            LEFT JOIN employees m ON e.manager_id = m.employee_id
            ORDER BY e.role, e.last_name
        """)
        results = cursor.fetchall()
    
    table = Table(title="Employees", box=box.ROUNDED)
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Role")
    table.add_column("Wage", justify="right")
    table.add_column("Manager")
    
    for row in results:
        table.add_row(
            str(row['employee_id']),
            row['name'],
            row['role'],
            f"${row['hourly_wage']:.2f}/hr",
            row['manager_name'] or "-"
        )
    
    console.print(table)


@manager_app.command("popular")
def popular_items(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show")
):
    """Show most popular menu items."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    results = get_popular_menu_items(limit)
    
    if not results:
        console.print("[yellow]No order data found.[/yellow]")
        return
    
    table = Table(title=f"Top {limit} Popular Items", box=box.ROUNDED)
    table.add_column("Rank", style="dim", width=5)
    table.add_column("Item", style="cyan")
    table.add_column("Category")
    table.add_column("Times Ordered", justify="right")
    table.add_column("Revenue", justify="right", style="green")
    
    for i, row in enumerate(results, 1):
        table.add_row(
            str(i),
            row['item_name'],
            row['category'],
            str(row['times_ordered']),
            f"${row['total_revenue']:.2f}"
        )
    
    console.print(table)


@manager_app.command("customers")
def top_customers(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of customers to show")
):
    """Show top customers by spending."""
    if not check_database_exists():
        console.print("[red]Database not initialized.[/red]")
        raise typer.Exit(1)
    
    results = get_above_average_customers()
    
    if not results:
        console.print("[yellow]No customer data found.[/yellow]")
        return
    
    avg_spending = results[0]['avg_customer_spending'] if results else 0
    
    table = Table(
        title=f"Top Customers (Avg Spending: ${avg_spending:.2f})", 
        box=box.ROUNDED
    )
    table.add_column("Rank", style="dim", width=5)
    table.add_column("Customer", style="cyan")
    table.add_column("Email")
    table.add_column("Orders", justify="right")
    table.add_column("Total Spent", justify="right", style="green")
    
    for i, row in enumerate(results[:limit], 1):
        table.add_row(
            str(i),
            row['customer_name'],
            row['email'][:30],
            str(row['order_count']),
            f"${row['total_spent']:.2f}"
        )
    
    console.print(table)


if __name__ == "__main__":
    app()

