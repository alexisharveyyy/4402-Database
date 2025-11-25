# Entity-Relationship Diagram

## Restaurant Database E-R Model

### Conceptual E-R Diagram

```
                                    ┌─────────────────┐
                                    │    CATEGORIES   │
                                    ├─────────────────┤
                                    │ • category_id   │◄──────────────────────┐
                                    │ • name          │                       │
                                    │ • description   │                       │
                                    └─────────────────┘                       │
                                                                              │ belongs_to
                                                                              │ (M:1)
                                    ┌─────────────────┐                       │
                                    │   MENU_ITEMS    │───────────────────────┘
                                    ├─────────────────┤
                                    │ • item_id       │◄─────────────────────────────┐
                                    │ • name          │                              │
                                    │ • description   │                              │
                                    │ • price         │                              │
                                    │ • category_id   │                              │
                                    │ • is_available  │                              │
                                    └─────────────────┘                              │
                                                                                     │
                                                                                     │ references
                                                                                     │ (M:1)
                                                                                     │
┌─────────────────┐             ┌─────────────────┐             ┌─────────────────┐  │
│    CUSTOMERS    │             │   RESERVATIONS  │             │  ORDER_ITEMS    │──┘
├─────────────────┤             ├─────────────────┤             ├─────────────────┤
│ • customer_id   │◄────────────│ • reservation_id│             │ • order_item_id │
│ • first_name    │   makes     │ • customer_id   │             │ • order_id      │───┐
│ • last_name     │   (1:M)     │ • table_id      │             │ • item_id       │   │
│ • phone         │             │ • reservation_  │             │ • quantity      │   │
│ • email         │             │   date          │             │ • unit_price    │   │
│ • created_at    │             │ • reservation_  │             │ • special_      │   │
└─────────────────┘             │   time          │             │   instructions  │   │
        │                       │ • party_size    │             └─────────────────┘   │
        │                       │ • status        │                   ▲               │
        │ places                │ • special_      │                   │ contains      │
        │ (1:M)                 │   requests      │                   │ (1:M)         │
        │                       └─────────────────┘                   │               │
        │                               │                             │               │
        │                               │ for                         │               │
        │                               │ (M:1)                       │               │
        │                               ▼                             │               │
        │                       ┌─────────────────┐             ┌─────────────────┐   │
        │                       │     TABLES      │             │     ORDERS      │◄──┘
        │                       ├─────────────────┤             ├─────────────────┤
        │                       │ • table_id      │◄────────────│ • order_id      │
        │                       │ • table_number  │   seated_at │ • customer_id   │◄──┐
        │                       │ • capacity      │   (M:1)     │ • employee_id   │   │
        │                       │ • location      │             │ • table_id      │   │
        │                       │ • is_active     │             │ • order_type    │   │
        │                       └─────────────────┘             │ • status        │   │
        │                                                       │ • order_date    │   │
        └──────────────────────────────────────────────────────►│ • order_time    │   │
                                                                │ • subtotal      │   │
                                                                │ • tax           │   │
                                                                │ • tip           │   │
                                                                │ • total         │   │
                                                                └─────────────────┘   │
                                                                        ▲             │
                                                                        │ handles     │
                                                                        │ (1:M)       │
                                                                        │             │
┌─────────────────┐             ┌─────────────────┐                     │             │
│    EMPLOYEES    │◄────────────│     SHIFTS      │                     │             │
├─────────────────┤  assigned   ├─────────────────┤                     │             │
│ • employee_id   │  (1:M)      │ • shift_id      │                     │             │
│ • first_name    │             │ • employee_id   │                     │             │
│ • last_name     │             │ • shift_date    │                     │             │
│ • role          │             │ • start_time    │                     │             │
│ • phone         │             │ • end_time      │                     │             │
│ • email         │             └─────────────────┘                     │             │
│ • hire_date     │                                                     │             │
│ • hourly_wage   │─────────────────────────────────────────────────────┘             │
│ • manager_id    │◄─────┐                                                            │
└─────────────────┘      │ supervises (self-referential 1:M)                          │
        │                │                                                            │
        └────────────────┘                                                            │
```

---

## Entity Descriptions

### Strong Entities

#### CUSTOMERS
Primary entity for restaurant patrons.
- **Primary Key:** customer_id
- **Attributes:** first_name, last_name, phone, email, created_at
- **Relationships:** Makes reservations (1:M), Places orders (1:M)

#### EMPLOYEES
Staff members working at the restaurant.
- **Primary Key:** employee_id
- **Attributes:** first_name, last_name, role, phone, email, hire_date, hourly_wage, manager_id
- **Constraints:** role must be one of: Host, Server, Bartender, Cook, Manager
- **Relationships:** 
  - Assigned to shifts (1:M)
  - Handles orders (1:M)
  - Supervises other employees (self-referential 1:M)

#### TABLES
Physical tables in the restaurant.
- **Primary Key:** table_id
- **Attributes:** table_number, capacity, location, is_active
- **Constraints:** 
  - capacity > 0 AND capacity <= 20
  - location must be one of: Main Dining, Patio, Bar Area, Private Room
- **Relationships:** Has reservations (1:M), Hosts orders (1:M)

#### CATEGORIES
Menu organization groups.
- **Primary Key:** category_id
- **Attributes:** name, description
- **Relationships:** Contains menu items (1:M)

#### MENU_ITEMS
Food and drink items available for ordering.
- **Primary Key:** item_id
- **Attributes:** name, description, price, category_id, is_available, created_at
- **Constraints:** price > 0
- **Relationships:** Belongs to category (M:1), Referenced by order items (1:M)

#### RESERVATIONS
Customer bookings for tables.
- **Primary Key:** reservation_id
- **Attributes:** customer_id, table_id, reservation_date, reservation_time, party_size, status, special_requests, created_at
- **Constraints:** 
  - party_size > 0
  - status must be one of: Confirmed, Seated, Completed, Cancelled, No-Show
- **Relationships:** Made by customer (M:1), For table (M:1)

#### SHIFTS
Employee work schedules.
- **Primary Key:** shift_id
- **Attributes:** employee_id, shift_date, start_time, end_time
- **Constraints:** end_time > start_time
- **Relationships:** Assigned to employee (M:1)

#### ORDERS
Customer orders handled by servers.
- **Primary Key:** order_id
- **Attributes:** customer_id, employee_id, table_id, order_type, status, order_date, order_time, subtotal, tax, tip, total, created_at
- **Constraints:**
  - order_type must be one of: Dine-In, Takeout, Bar
  - status must be one of: Open, In Progress, Completed, Cancelled
- **Relationships:** 
  - Placed by customer (M:1, optional)
  - Handled by employee (M:1)
  - At table (M:1, optional)
  - Contains order items (1:M)

### Weak Entity

#### ORDER_ITEMS
Individual items within an order. **This is a weak entity** because:
- It cannot exist without a parent order
- Its identity is partially derived from the order
- Deleting an order cascades to delete all its items

- **Primary Key:** order_item_id (could also be composite: order_id + item sequence)
- **Attributes:** order_id, item_id, quantity, unit_price, special_instructions
- **Constraints:** quantity > 0
- **Relationships:** 
  - Belongs to order (M:1) with CASCADE delete
  - References menu item (M:1)

---

## Relationship Summary

| Relationship | Type | Description |
|-------------|------|-------------|
| Customer → Reservations | 1:M | A customer can make multiple reservations |
| Customer → Orders | 1:M | A customer can place multiple orders |
| Table → Reservations | 1:M | A table can have many reservations (different times) |
| Table → Orders | 1:M | A table can host multiple orders |
| Employee → Shifts | 1:M | An employee works multiple shifts |
| Employee → Orders | 1:M | A server handles multiple orders |
| Employee → Employee | 1:M | Manager supervises other employees (self-ref) |
| Category → Menu Items | 1:M | A category contains multiple items |
| Menu Item → Order Items | 1:M | An item appears in multiple orders |
| Order → Order Items | 1:M | An order contains multiple items (weak entity) |

---

## Cardinality Constraints

- Each **reservation** must have exactly one customer and one table
- Each **order** must have exactly one server (employee)
- Each **order item** must belong to exactly one order and reference one menu item
- Each **menu item** must belong to exactly one category
- Each **shift** must be assigned to exactly one employee
- **manager_id** is optional (managers don't have managers)
- **customer_id** in orders is optional (walk-in customers)
- **table_id** in orders is optional (takeout orders)

---

## Participation Constraints

| Entity | Participation | Description |
|--------|--------------|-------------|
| Customers in Reservations | Partial | Not all customers make reservations |
| Customers in Orders | Partial | Some orders are anonymous (walk-ins) |
| Employees in Orders | Partial | Only servers/bartenders handle orders |
| Tables in Reservations | Partial | Not all tables have reservations |
| Menu Items in Order Items | Total | All menu items should be orderable |
| Orders in Order Items | Total | All orders should have at least one item |

---

## Key Constraints Summary

### Primary Keys
- All entities use auto-incrementing INTEGER primary keys
- Naming convention: `{entity_name}_id`

### Foreign Keys
```sql
reservations.customer_id → customers.customer_id
reservations.table_id → tables.table_id
orders.customer_id → customers.customer_id
orders.employee_id → employees.employee_id
orders.table_id → tables.table_id
order_items.order_id → orders.order_id (CASCADE)
order_items.item_id → menu_items.item_id
menu_items.category_id → categories.category_id
shifts.employee_id → employees.employee_id (CASCADE)
employees.manager_id → employees.employee_id (self-referential)
```

### Unique Constraints
- `customers.email` - Each customer has unique email
- `employees.email` - Each employee has unique email  
- `tables.table_number` - Each table has unique identifier
- `categories.name` - Each category has unique name

### Check Constraints
- `employees.role IN ('Host', 'Server', 'Bartender', 'Cook', 'Manager')`
- `employees.hourly_wage > 0`
- `tables.capacity > 0 AND capacity <= 20`
- `tables.location IN ('Main Dining', 'Patio', 'Bar Area', 'Private Room')`
- `menu_items.price > 0`
- `reservations.party_size > 0`
- `reservations.status IN ('Confirmed', 'Seated', 'Completed', 'Cancelled', 'No-Show')`
- `orders.order_type IN ('Dine-In', 'Takeout', 'Bar')`
- `orders.status IN ('Open', 'In Progress', 'Completed', 'Cancelled')`
- `order_items.quantity > 0`
- `shifts.end_time > shifts.start_time`

