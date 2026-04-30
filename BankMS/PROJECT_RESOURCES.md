# Project Stack & Implementation Overview

This document provides a comprehensive list of all technologies, libraries, and architectural strategies used in the **QuickSay Pay** Bank Management System project.

---

## 1. Database Stack (Oracle Ecosystem)
The project utilizes a robust Oracle-based backend for all data storage and business logic.

*   **Oracle Database (Local XE/EE):** The primary relational database management system.
*   **cx_Oracle (Python Driver):** The extension module that enables Python to communicate with Oracle Database.
*   **Oracle Instant Client:** The essential set of libraries (DLLs) required on the host machine for `cx_Oracle` to establish a connection.
*   **SQL Developer:** The IDE used for designing the schema, writing complex queries, and managing PL/SQL objects (Procedures, Functions, Triggers).
*   **PL/SQL Components:**
    *   **Stored Procedures:** Used for complex operations like fund transfers, loan approvals, and employee registration.
    *   **Functions:** Used for data retrieval like calculating interest or getting customer balances.
    *   **Sequences & Triggers:** Used for automatic ID generation and data integrity.

---

## 2. GUI Stack (Python Backend & Frontend)
The interface is built to be "Premium" and modern, moving away from the standard "gray" look of legacy desktop apps.

*   **Python 3.x:** The core programming language.
*   **CustomTkinter (ctk):** A modern UI library based on Tkinter that provides rounded corners, dark mode support, and high-DPI scaling.
*   **Tkinter:** Used as the underlying engine and for specific low-level components like the `Canvas` for animations.
*   **Threading:** Used to run database queries in the background, preventing the GUI from "freezing" during network or disk I/O.
*   **Custom Fonts:** Integration of **Playfair Display** (via `ctypes` for Windows font injection) to achieve a premium branding feel.

---

## 3. How the GUI was Implemented
The GUI was implemented using a modular, event-driven architecture designed for high performance and visual appeal.

### A. Architectural Patterns
*   **Singleton Connection:** A single `DatabaseConnection` instance is shared across all windows, managed via a Python Singleton pattern to prevent multiple redundant connections.
*   **Model-View Separation:** GUI views (in `gui/views/`) do not write SQL directly. Instead, they call methods in "Model" classes (in `gui/models/`), which handle the `cx_Oracle` logic.
*   **Dynamic View Switching:** The main `App` class acts as a controller, destroying current view frames and packing new ones (Dashboard, Login, etc.) based on user authentication and role.

### B. Visual Excellence & UX
*   **Premium Aesthetics:** Implemented a curated color palette (Gold `#C9A84C` on Deep Blue `#0A1628`) to create a "bank-like" luxury feel.
*   **Micro-Animations:**
    *   **Particle Systems:** A canvas-based background animation on the login screen using custom physics.
    *   **Slide-ins:** UI elements slide into position using a recursive `after()` loop.
    *   **Feedback Loops:** Buttons change text to "Connecting..." during I/O, and cards "shake" on invalid credentials.
*   **Role-Based Dashboards:** Distinct interfaces for **Admin, Manager, Teller,** and **Customer**, each with customized sidebars and permission-restricted views.

### C. Performance Strategy
*   **Lazy Loading:** Data is only fetched from Oracle when a specific tab or dashboard section is opened.
*   **Error Handling:** A global traceback logger captures GUI-related crashes into `error.txt` for debugging without stopping the application.
