-- Restaurant Database Schema
-- CSC 4402 Database Project

-- ============================================
-- Drop existing tables (in reverse dependency order)
-- ============================================
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS tables;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;

-- ============================================
-- CUSTOMERS TABLE
-- Stores information about restaurant patrons
-- ============================================
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- EMPLOYEES TABLE
-- Stores information about restaurant staff
-- Includes self-referential relationship for manager supervision
-- ============================================
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('Host', 'Server', 'Bartender', 'Cook', 'Manager')),
    phone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    hire_date DATE NOT NULL,
    hourly_wage DECIMAL(6,2) NOT NULL CHECK (hourly_wage > 0),
    manager_id INTEGER,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

-- ============================================
-- TABLES TABLE
-- Stores information about restaurant seating
-- ============================================
CREATE TABLE tables (
    table_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_number VARCHAR(10) NOT NULL UNIQUE,
    capacity INTEGER NOT NULL CHECK (capacity > 0 AND capacity <= 20),
    location VARCHAR(30) NOT NULL CHECK (location IN ('Main Dining', 'Patio', 'Bar Area', 'Private Room')),
    is_active BOOLEAN DEFAULT 1
);

-- ============================================
-- CATEGORIES TABLE
-- Organizes menu items into groups
-- ============================================
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- ============================================
-- MENU_ITEMS TABLE
-- Stores all items available for ordering
-- ============================================
CREATE TABLE menu_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(8,2) NOT NULL CHECK (price > 0),
    category_id INTEGER NOT NULL,
    is_available BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT
);

-- ============================================
-- RESERVATIONS TABLE
-- Links customers to tables at specific times
-- ============================================
CREATE TABLE reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    party_size INTEGER NOT NULL CHECK (party_size > 0),
    status VARCHAR(20) DEFAULT 'Confirmed' CHECK (status IN ('Confirmed', 'Seated', 'Completed', 'Cancelled', 'No-Show')),
    special_requests TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES tables(table_id) ON DELETE RESTRICT
);

-- ============================================
-- SHIFTS TABLE
-- Tracks employee work schedules
-- ============================================
CREATE TABLE shifts (
    shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    shift_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    CHECK (end_time > start_time)
);

-- ============================================
-- ORDERS TABLE
-- Stores customer orders handled by servers
-- ============================================
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    employee_id INTEGER NOT NULL,
    table_id INTEGER,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('Dine-In', 'Takeout', 'Bar')),
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Completed', 'Cancelled')),
    order_date DATE NOT NULL,
    order_time TIME NOT NULL,
    subtotal DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    tip DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT,
    FOREIGN KEY (table_id) REFERENCES tables(table_id) ON DELETE SET NULL
);

-- ============================================
-- ORDER_ITEMS TABLE (Weak Entity)
-- Links orders to menu items with quantities
-- Depends on orders table for existence
-- ============================================
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(8,2) NOT NULL,
    special_instructions TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE RESTRICT
);

-- ============================================
-- INDEXES for improved query performance
-- ============================================
CREATE INDEX idx_reservations_date ON reservations(reservation_date);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_employee ON orders(employee_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_menu_items_category ON menu_items(category_id);
CREATE INDEX idx_shifts_employee_date ON shifts(employee_id, shift_date);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger to update order totals when order_items are added
CREATE TRIGGER update_order_total_insert
AFTER INSERT ON order_items
BEGIN
    UPDATE orders
    SET subtotal = (
        SELECT COALESCE(SUM(quantity * unit_price), 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    tax = (
        SELECT COALESCE(SUM(quantity * unit_price), 0) * 0.0825
        FROM order_items
        WHERE order_id = NEW.order_id
    ),
    total = (
        SELECT COALESCE(SUM(quantity * unit_price), 0) * 1.0825 + COALESCE(orders.tip, 0)
        FROM order_items
        WHERE order_id = NEW.order_id
    )
    WHERE order_id = NEW.order_id;
END;

-- Trigger to update order totals when order_items are deleted
CREATE TRIGGER update_order_total_delete
AFTER DELETE ON order_items
BEGIN
    UPDATE orders
    SET subtotal = (
        SELECT COALESCE(SUM(quantity * unit_price), 0)
        FROM order_items
        WHERE order_id = OLD.order_id
    ),
    tax = (
        SELECT COALESCE(SUM(quantity * unit_price), 0) * 0.0825
        FROM order_items
        WHERE order_id = OLD.order_id
    ),
    total = (
        SELECT COALESCE(SUM(quantity * unit_price), 0) * 1.0825 + COALESCE(orders.tip, 0)
        FROM order_items
        WHERE order_id = OLD.order_id
    )
    WHERE order_id = OLD.order_id;
END;

