from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QDate
import sys
import pyodbc



class MainController(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainController, self).__init__()
        self.current_window = None
        # self.showMaximized()  # Optional: Start in maximized mode


        # Connect to the database
        self.connect_to_database()
        # Start with the Sign-In screen
        self.show_sign_in_screen()

    
    
    def connect_to_database(self):
        """Connect to the SQL Server database."""
        try:
            self.connection = pyodbc.connect(
                "Driver={ODBC Driver 17 for SQL Server};"
                "Server=DESKTOP-C3F64U8\SQLSERVER1;"  # Replace with your server name
                "Database=CriminalDB;"     # Replace with your database name
                "Trusted_Connection=yes;"
            )
            print("Database connection successful!")
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")
            sys.exit()

    def load_ui(self, ui_file):
        """
        Helper to load a .ui file with QMainWindow and scroll support.
        """
        try:
            widget = QtWidgets.QMainWindow()
            uic.loadUi(ui_file, widget)
            return widget
        except Exception as e:
            print(f"Error loading {ui_file}: {e}")
            sys.exit()

    def set_main_widget(self, widget):
        """
        Helper to set the main widget in the QMainWindow.
        """
        if self.current_window:
            self.current_window.close()  # Close the previous window if it exists
        self.current_window = widget
        self.setCentralWidget(self.current_window)  # Set the widget as the central widget



    def show_sign_in_screen(self):
        """Show the Sign-In screen."""
        sign_in = self.load_ui("screens\\Sign_In_Page.ui")
        self.set_main_widget(sign_in)
        user_name = ""
        pass_word= ""
        # Connect buttons
        self.current_sign_in_widget = sign_in
        try:
            signin_button = sign_in.findChild(QtWidgets.QPushButton, "signin_button")
            if signin_button:
                signin_button.clicked.connect(self.validate_login)
                    
        except AttributeError:
            print("Error: 'signin_button' not found in Sign_In_Page.ui.")
            self.show_admin_dashboard(user_name,pass_word)  # Bypass for testing purposes

    def show_admin_dashboard(self,admin_name = "",admin_ID = ""):
        """Show the Admin Dashboard."""
        admin_dashboard = self.load_ui("screens\\home_screen_admin.ui")
        self.set_main_widget(admin_dashboard)

        # Connect buttons for navigation
        try:
            admin_dashboard.findChild(QtWidgets.QLineEdit, "admindisplayname").setText(str(admin_name))
            admin_dashboard.findChild(QtWidgets.QLineEdit, "admindisplayID").setText(str(admin_ID))
            admin_dashboard.findChild(QtWidgets.QPushButton, "modify_operator_button").clicked.connect(self.show_search_operator)
            admin_dashboard.findChild(QtWidgets.QPushButton, "modify_fir_button").clicked.connect(self.show_search_fir)
            admin_dashboard.findChild(QtWidgets.QPushButton, "modify_convicted_person_button").clicked.connect(self.show_search_convicted_person)
            admin_dashboard.findChild(QtWidgets.QPushButton, "requests_button").clicked.connect(self.show_manage_requests)
            admin_dashboard.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        except AttributeError as e:
            print(f"Error in Admin Dashboard button setup: {e}")

    def show_operator_dashboard(self,op_name = "",op_ID = ""):
        """Show the Operator Dashboard."""
        operator_dashboard = self.load_ui("screens\\home_screen_Operator.ui")
        self.set_main_widget(operator_dashboard)

        # Connect buttons for navigation
        try:
            operator_dashboard.findChild(QtWidgets.QLineEdit, "op_name").setText(str(op_name))
            operator_dashboard.findChild(QtWidgets.QLineEdit, "op_id").setText(str(op_ID))
            operator_dashboard.findChild(QtWidgets.QPushButton, "fir_button").clicked.connect(self.show_search_fir(op_ID))
            operator_dashboard.findChild(QtWidgets.QPushButton, "convicted_person_button").clicked.connect(self.show_search_convicted_person)
            operator_dashboard.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        except AttributeError as e:
            print(f"Error in Operator Dashboard button setup: {e}")

    def validate_login(self):
        """Validate login credentials and navigate to the admin dashboard."""
        sign_in = self.current_window
        username = sign_in.findChild(QtWidgets.QLineEdit, "user_input").text().strip()
        password = sign_in.findChild(QtWidgets.QLineEdit, "pass_input").text().strip()

        cursor = self.connection.cursor()
        try:
            query = "SELECT * FROM Users WHERE user_id = ? AND user_password = ?"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                if result[5] == 1:
                    self.show_admin_dashboard(result[2], result[0])  # Navigate to the dashboard
                elif result[5] == 2:
                    self.show_operator_dashboard(result[2], result[0])  # Navigate to the dashboard
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Login", "Username or password is incorrect.")
        except pyodbc.Error as e:
            print(f"Login validation error: {e}")

    # --- Navigation Methods ---
    def show_search_operator(self):
        """Show the Search Operator screen."""
        search_operator = self.load_ui("screens/search_operator.ui")
        self.set_main_widget(search_operator)

        # Populate combo boxes with data from the database
        cursor = self.connection.cursor()
        try:
            # Populate operator IDs
            query = "SELECT user_id FROM Users"
            cursor.execute(query)
            operator_ids = cursor.fetchall()

            combo_op_id = search_operator.findChild(QtWidgets.QComboBox, "op_id_combo")
            combo_op_id.clear()
            combo_op_id.addItem("")  # Add an empty option
            for operator in operator_ids:
                combo_op_id.addItem(operator[0])

            # Populate ranks
            query = "SELECT DISTINCT user_rank FROM Users"
            cursor.execute(query)
            ranks = cursor.fetchall()

            combo_op_rank = search_operator.findChild(QtWidgets.QComboBox, "op_rank")
            combo_op_rank.clear()
            combo_op_rank.addItem("")  # Add an empty option
            for rank in ranks:
                combo_op_rank.addItem(rank[0])

            # Populate departments
            query = "SELECT DISTINCT user_department FROM Users"
            cursor.execute(query)
            departments = cursor.fetchall()

            combo_op_dept = search_operator.findChild(QtWidgets.QComboBox, "op_dept")
            combo_op_dept.clear()
            combo_op_dept.addItem("")  # Add an empty option
            for department in departments:
                combo_op_dept.addItem(department[0])
        except pyodbc.Error as e:
            print(f"Database error: {e}")

        search_operator.findChild(QtWidgets.QPushButton, "search_button").clicked.connect(self.search_operator_logic)

        # Connect buttons
        try:
            search_operator.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            search_operator.findChild(QtWidgets.QPushButton, "view_button").clicked.connect(lambda: self.view_selected_operator(search_operator))
            search_operator.findChild(QtWidgets.QPushButton, "add_button").clicked.connect(self.show_add_operator)
            search_operator.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(lambda: self.show_update_operator(search_operator))
            search_operator.findChild(QtWidgets.QPushButton, "delete_button").clicked.connect(lambda: self.delete_operator_record(search_operator))
            search_operator.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        except AttributeError as e:
            print(f"Error in Search Operator button setup: {e}")

    
    def search_operator_logic(self):
        """Search and display operator records."""
        search_operator = self.current_window
        user_name = str(search_operator.findChild(QtWidgets.QComboBox, "op_id_combo").currentText())
        name = str(search_operator.findChild(QtWidgets.QLineEdit, "op_name").text().strip())
        rank = str(search_operator.findChild(QtWidgets.QComboBox, "op_rank").currentText())
        department = str(search_operator.findChild(QtWidgets.QComboBox, "op_dept").currentText())

        query = "SELECT user_id, user_name, user_rank, user_department FROM Users WHERE 1=1"
        params = []

        # Add conditions based on user inputs
        if user_name:
            query += " AND user_id = ?"
            params.append(user_name)
        if name:
            query += " AND user_name LIKE ?"
            params.append(f"%{name}%")
        if rank:
            query += " AND user_rank = ?"
            params.append(rank)
        if department:
            query += " AND user_department = ?"
            params.append(department)

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            records = cursor.fetchall()

            table_widget = search_operator.findChild(QtWidgets.QTableWidget, "op_table")
            table_widget.setRowCount(len(records))
            table_widget.setColumnCount(4)  # ID, Name, Rank, Department

            for row_index, row_data in enumerate(records):
                for col_index, col_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(col_data))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(row_index, col_index, item)
        except pyodbc.Error as e:
            print(f"Database query error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to fetch operator records!")

    def show_add_operator(self):
        add_operator = self.load_ui("screens/add_operator.ui")
        self.set_main_widget(add_operator)

        try:
            cursor = self.connection.cursor()

            # Populate rank combo box from the database
            query_rank = "SELECT DISTINCT user_rank FROM Users"
            cursor.execute(query_rank)
            ranks = [row[0] for row in cursor.fetchall()]  # Fetch all unique ranks
            rank_combo = add_operator.findChild(QtWidgets.QComboBox, "rank_line")
            rank_combo.clear()  # Clear any existing items
            rank_combo.addItems([""] + ranks)  # Add an empty option followed by ranks

            # Populate department combo box from the database
            query_department = "SELECT DISTINCT user_department FROM Users"
            cursor.execute(query_department)
            departments = [row[0] for row in cursor.fetchall()]  # Fetch all unique departments
            dept_combo = add_operator.findChild(QtWidgets.QComboBox, "dept_line")
            dept_combo.clear()  # Clear any existing items
            dept_combo.addItems([""] + departments)  # Add an empty option followed by departments

            # Populate department combo box from the database

            dept_combo = add_operator.findChild(QtWidgets.QComboBox, "user_type_display")
            dept_combo.clear()  # Clear any existing items
            dept_combo.addItems(["","admin","operator"])  # Add an empty option followed by departments

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading ranks or departments: {e}")
            return

        # Connect buttons to their respective logic
        add_operator.findChild(QtWidgets.QPushButton, "add_op_button").clicked.connect(self.add_operator_logic)
        add_operator.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        add_operator.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)



    def show_search_fir(self,op_ID = ""):
        """Show the Search FIR Report screen."""
        search_fir = self.load_ui("screens\\search_fir_report.ui")
        self.set_main_widget(search_fir)

        try:
            cursor = self.connection.cursor()

            # Populate FIR combo box with FIRNo
            cursor.execute("SELECT FIRNo FROM FIR")  # Use FIRNo as the primary key
            fir_ids = [str(row[0]) for row in cursor.fetchall()]  # Convert integers to strings
            fir_combo = search_fir.findChild(QtWidgets.QComboBox, "fir_combo")
            fir_combo.clear()  # Clear existing items to avoid duplicates
            fir_combo.addItems([""] + fir_ids)  # Add an empty option for default

            # Populate location combo box with distinct locations
            cursor.execute("SELECT DISTINCT Location FROM FIR")
            locations = [row[0] for row in cursor.fetchall() if row[0]]  # Avoid null or empty values
            location_combo = search_fir.findChild(QtWidgets.QComboBox, "location_combo")
            location_combo.clear()
            location_combo.addItems([""] + locations)

            # Populate station combo box with distinct station IDs
            cursor.execute("SELECT DISTINCT policeStationCode FROM FIR")
            stations = [row[0] for row in cursor.fetchall() if row[0]]
            station_combo = search_fir.findChild(QtWidgets.QComboBox, "station_combo")
            station_combo.clear()
            station_combo.addItems([""] + stations)

            # Populate nature combo box with distinct nature types
            cursor.execute("SELECT DISTINCT crimeNature FROM FIR")
            natures = [row[0] for row in cursor.fetchall() if row[0]]
            nature_combo = search_fir.findChild(QtWidgets.QComboBox, "nature_combo")
            nature_combo.clear()
            nature_combo.addItems([""] + natures)

            # Populate section combo box with distinct sections
            cursor.execute("SELECT DISTINCT sectionofLaw FROM FIR")
            sections = [row[0] for row in cursor.fetchall() if row[0]]
            section_combo = search_fir.findChild(QtWidgets.QComboBox, "section_combo")
            section_combo.clear()
            section_combo.addItems([""] + sections)

            # Populate status combo box with distinct statuses
            cursor.execute("SELECT DISTINCT status FROM FIR")
            statuses = [row[0] for row in cursor.fetchall() if row[0]]
            status_combo = search_fir.findChild(QtWidgets.QComboBox, "status_combo")
            status_combo.clear()
            status_combo.addItems([""] + statuses)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading FIR data: {e}")

        # Default date placeholders
        search_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText("valid date (dd/MM/yyyy)")
        search_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText("valid date (dd/MM/yyyy)")

        # Connect buttons
        search_fir.findChild(QtWidgets.QPushButton, "search_button").clicked.connect(self.search_fir_logic)
        try:
            search_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            search_fir.findChild(QtWidgets.QPushButton, "view_button").clicked.connect(lambda: self.view_selected_fir(search_fir))
            if op_ID != "":
                search_fir.findChild(QtWidgets.QPushButton, "add_button").clicked.connect(self.op_show_add_fir(op_ID))
            search_fir.findChild(QtWidgets.QPushButton, "add_button").clicked.connect(self.show_add_fir)
            search_fir.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(lambda: self.show_update_fir(search_fir))
            search_fir.findChild(QtWidgets.QPushButton, "delete_button").clicked.connect(lambda: self.delete_fir_record(search_fir))
            search_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        except AttributeError as e:
            print(f"Error in Search FIR button setup: {e}")


        # Populate table with all FIRs by default
        self.populate_all_firs(search_fir)

    def populate_all_firs(self, search_fir):
        """Populate the table widget with all FIRs by default."""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT FIRNo, dateofFiling, dateofIncident, Location, 
                    policeStationCode, crimeNature, sectionofLaw, status
                FROM FIR
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Populate the table widget with all FIRs
            table_widget = search_fir.findChild(QtWidgets.QTableWidget, "fir_table")
            table_widget.setRowCount(len(results))
            table_widget.setColumnCount(8)  # Adjust the column count to match the query

            for i, record in enumerate(results):
                for j, value in enumerate(record):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    # Make the items non-editable
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(i, j, item)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading all FIRs: {e}")


    def validate_date(self, date_text, format="dd/MM/yyyy"):
        """Validate the date entered in QLineEdit and return QDate if valid."""
        default_placeholder = "(dd/MM/yyyy)"
        
        # Treat default placeholder and empty string as valid (no date entered)
        if not date_text.strip() or date_text.strip() == default_placeholder:
            return None

        # Try to parse the date
        date = QDate.fromString(date_text.strip(), format)
        if date.isValid():
            return date

        # Return None if the date is invalid
        return None
    

    def show_view_fir(self, full_record):
        """Display FIR details in the view FIR screen."""
        view_fir = self.load_ui("screens/view_fir_report.ui")
        self.set_main_widget(view_fir)

        # Populate the fields with FIR details
        try:
            view_fir.findChild(QtWidgets.QLineEdit, "fir_display").setText(str(full_record[0]))
            view_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText(full_record[1].strftime("%d/%m/%Y"))
            view_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText(full_record[2].strftime("%d/%m/%Y"))
            view_fir.findChild(QtWidgets.QLineEdit, "location_display").setText(full_record[3])
            view_fir.findChild(QtWidgets.QLineEdit, "station_display").setText(full_record[4])
            view_fir.findChild(QtWidgets.QLineEdit, "complain_display").setText(full_record[5])
            view_fir.findChild(QtWidgets.QLineEdit, "accused_detail_display").setText(full_record[6])
            view_fir.findChild(QtWidgets.QLineEdit, "witness_detail_display").setText(full_record[7])
            view_fir.findChild(QtWidgets.QLineEdit, "nature_display").setText(full_record[8])
            view_fir.findChild(QtWidgets.QLineEdit, "section_display").setText(full_record[9])
            view_fir.findChild(QtWidgets.QLineEdit, "officer_detail_display").setText(full_record[10])
            view_fir.findChild(QtWidgets.QLineEdit, "status_display").setText(full_record[11])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Data mapping issue: {e}")

        # Connect navigation buttons
        view_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        view_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
    
    def view_selected_fir(self, search_fir):
        """Get the selected FIR from the table and show details in the view screen."""
        table_widget = search_fir.findChild(QtWidgets.QTableWidget, "fir_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to view details.")
            return

        # Extract the FIR number from the selected row (assuming it's in the first column)
        fir_no_item = table_widget.item(selected_row, 0)
        if not fir_no_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve FIR details.")
            return

        selected_fir_no = fir_no_item.text()

        try:
            # Fetch FIR details from the database using the selected FIR number
            cursor = self.connection.cursor()
            query = """
                SELECT FIRNo, dateofFiling, dateofIncident, Location, policeStationCode, 
                    complainantDetails, accusedDetails, witnessDetails, crimeNature, 
                    sectionofLaw, officerDetails, status
                FROM FIR
                WHERE FIRNo = ?
            """
            cursor.execute(query, (selected_fir_no,))
            full_record = cursor.fetchone()

            if not full_record:
                QtWidgets.QMessageBox.warning(self, "Error", "FIR details not found in the database.")
                return

            # Call show_view_fir with full_record
            self.show_view_fir(full_record)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching FIR details: {e}")
    
    def show_add_fir(self):
        try:
            # Load the Add FIR UI
            add_fir = self.load_ui("screens/add_fir_report.ui")
            self.set_main_widget(add_fir)

            cursor = self.connection.cursor()

            # --- Populate FIR Number ---
            cursor.execute("SELECT ISNULL(MAX(FIRNo), 0) + 1 FROM FIR")
            next_fir_no = cursor.fetchone()[0]  # Get the next FIR number
            fir_no_display = add_fir.findChild(QtWidgets.QLineEdit, "fir_no_display")
            if fir_no_display:
                fir_no_display.setText(str(next_fir_no))
                fir_no_display.setReadOnly(True)

            # --- Populate Combo Boxes ---
            # Locations
            cursor.execute("SELECT DISTINCT Location FROM FIR")
            locations = [row[0] for row in cursor.fetchall()]
            location_combo = add_fir.findChild(QtWidgets.QComboBox, "location_combo")
            location_combo.addItems([""] + locations)

            # Police Stations
            cursor.execute("SELECT DISTINCT policeStationCode FROM FIR")
            stations = [row[0] for row in cursor.fetchall()]
            station_combo = add_fir.findChild(QtWidgets.QComboBox, "station_combo")
            station_combo.addItems([""] + stations)

            # Nature of Crimes
            cursor.execute("SELECT DISTINCT crimeNature FROM FIR")
            natures = [row[0] for row in cursor.fetchall()]
            nature_combo = add_fir.findChild(QtWidgets.QComboBox, "nature_combo")
            nature_combo.addItems([""] + natures)

            # Sections of Law
            cursor.execute("SELECT DISTINCT sectionofLaw FROM FIR")
            sections = [row[0] for row in cursor.fetchall()]
            section_combo = add_fir.findChild(QtWidgets.QComboBox, "section_combo")
            section_combo.addItems([""] + sections)

            # Statuses (active/inactive)
            cursor.execute("SELECT DISTINCT status FROM FIR")
            statuses = [row[0] for row in cursor.fetchall()]
            status_combo = add_fir.findChild(QtWidgets.QComboBox, "status_combo")
            status_combo.addItems([""] + statuses)

            # --- Set Default Placeholders for Dates ---
            add_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText("(dd/MM/yyyy)")
            add_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText("(dd/MM/yyyy)")

    

            # --- Connect Buttons ---
            add_fir.findChild(QtWidgets.QPushButton, "add_fir_button").clicked.connect(self.add_fir_logic)
            add_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            add_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading FIR form: {e}")

    def op_show_add_fir(self,op_ID = ""):
        try:
            # Load the Add FIR UI
            add_fir = self.load_ui("screens\\op_add_fir_report.ui")
            self.set_main_widget(add_fir)

            cursor = self.connection.cursor()

            # --- Populate FIR Number ---
            cursor.execute("SELECT ISNULL(MAX(FIRNo), 0) + 1 FROM FIR")
            next_fir_no = cursor.fetchone()[0]  # Get the next FIR number
            fir_no_display = add_fir.findChild(QtWidgets.QLineEdit, "fir_no_display")
            if fir_no_display:
                fir_no_display.setText(str(next_fir_no))
                fir_no_display.setReadOnly(True)

            # --- Populate Combo Boxes ---
            # Locations
            cursor.execute("SELECT DISTINCT Location FROM FIR")
            locations = [row[0] for row in cursor.fetchall()]
            location_combo = add_fir.findChild(QtWidgets.QComboBox, "location_combo")
            location_combo.addItems([""] + locations)

            # Police Stations
            cursor.execute("SELECT DISTINCT policeStationCode FROM FIR")
            stations = [row[0] for row in cursor.fetchall()]
            station_combo = add_fir.findChild(QtWidgets.QComboBox, "station_combo")
            station_combo.addItems([""] + stations)

            # Nature of Crimes
            cursor.execute("SELECT DISTINCT crimeNature FROM FIR")
            natures = [row[0] for row in cursor.fetchall()]
            nature_combo = add_fir.findChild(QtWidgets.QComboBox, "nature_combo")
            nature_combo.addItems([""] + natures)

            # Sections of Law
            cursor.execute("SELECT DISTINCT sectionofLaw FROM FIR")
            sections = [row[0] for row in cursor.fetchall()]
            section_combo = add_fir.findChild(QtWidgets.QComboBox, "section_combo")
            section_combo.addItems([""] + sections)

            # Statuses (active/inactive)
            cursor.execute("SELECT DISTINCT status FROM FIR")
            statuses = [row[0] for row in cursor.fetchall()]
            status_combo = add_fir.findChild(QtWidgets.QComboBox, "status_combo")
            status_combo.addItems([""] + statuses)

            # --- Set Default Placeholders for Dates ---
            add_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText("(dd/MM/yyyy)")
            add_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText("(dd/MM/yyyy)")

    

            # --- Connect Buttons ---
            add_fir.findChild(QtWidgets.QPushButton, "add_fir_button").clicked.connect(self.op_add_fir_logic(op_ID))
            add_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            add_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading FIR form: {e}")


    
    def show_update_fir(self, search_operator_widget):
        """Get the selected FIR from the table and show details in the update screen."""
        table_widget = search_operator_widget.findChild(QtWidgets.QTableWidget, "fir_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to update.")
            return

        # Extract the FIR number from the selected row (assuming it's in the first column)
        fir_no_item = table_widget.item(selected_row, 0)
        if not fir_no_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve FIR details.")
            return

        selected_fir_no = fir_no_item.text()

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM FIR WHERE FIRNo = ?", (selected_fir_no,))
            fir_data = cursor.fetchone()

            if not fir_data:
                QtWidgets.QMessageBox.warning(self, "Error", "FIR details not found.")
                return

            # Load the update FIR screen
            update_fir = self.load_ui("screens/update_fir_report.ui")
            self.set_main_widget(update_fir)

            fir_no_display = update_fir.findChild(QtWidgets.QLineEdit, "fir_no")
            if fir_no_display:
                fir_no_display.setText(str(selected_fir_no))
                fir_no_display.setReadOnly(True)

            # --- Populate Combo Boxes ---
            # Locations
            cursor.execute("SELECT DISTINCT Location FROM FIR")
            locations = [row[0] for row in cursor.fetchall()]
            location_combo = update_fir.findChild(QtWidgets.QComboBox, "location_combo")
            location_combo.addItems([""] + locations)

            # Police Stations
            cursor.execute("SELECT DISTINCT policeStationCode FROM FIR")
            stations = [row[0] for row in cursor.fetchall()]
            station_combo = update_fir.findChild(QtWidgets.QComboBox, "station_combo")
            station_combo.addItems([""] + stations)

            # Nature of Crimes
            cursor.execute("SELECT DISTINCT crimeNature FROM FIR")
            natures = [row[0] for row in cursor.fetchall()]
            nature_combo = update_fir.findChild(QtWidgets.QComboBox, "nature_combo")
            nature_combo.addItems([""] + natures)

            # Sections of Law
            cursor.execute("SELECT DISTINCT sectionofLaw FROM FIR")
            sections = [row[0] for row in cursor.fetchall()]
            section_combo = update_fir.findChild(QtWidgets.QComboBox, "section_combo")
            section_combo.addItems([""] + sections)

            # Statuses (active/inactive)
            cursor.execute("SELECT DISTINCT status FROM FIR")
            statuses = [row[0] for row in cursor.fetchall()]
            status_combo = update_fir.findChild(QtWidgets.QComboBox, "status_combo")
            status_combo.addItems([""] + statuses)

            # --- Set Default Placeholders for Dates ---
            update_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText("(dd/MM/yyyy)")
            update_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText("(dd/MM/yyyy)")

            # Connect buttons
            update_fir.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(lambda: self.update_fir_logic(fir_data))
            update_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            update_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading FIR details: {e}")

    def delete_fir_record(self, search_operator_widget):
        """Get the selected FIR from the table and prepare for deletion."""
        table_widget = search_operator_widget.findChild(QtWidgets.QTableWidget, "fir_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        # Extract the FIR number from the selected row (assuming it's in the first column)
        fir_no_item = table_widget.item(selected_row, 0)
        if not fir_no_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve FIR details.")
            return

        selected_fir_no = fir_no_item.text()

        # Load the delete FIR confirmation UI
        delete_fir = self.load_ui("screens/delete_FIR_Report.ui")
        self.set_main_widget(delete_fir)

        # Populate the fields with FIR details
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT FIRNo, dateofFiling, dateofIncident, Location, policeStationCode, 
                    complainantDetails, accusedDetails, witnessDetails, crimeNature, 
                    sectionofLaw, officerDetails, status
                FROM FIR
                WHERE FIRNo = ?
            """
            cursor.execute(query, (selected_fir_no,))
            full_record = cursor.fetchone()

            if not full_record:
                QtWidgets.QMessageBox.warning(self, "Error", "FIR details not found in the database.")
                return

            # Populate the fields in the UI
            delete_fir.findChild(QtWidgets.QLineEdit, "fir_display").setText(str(full_record[0]))
            delete_fir.findChild(QtWidgets.QLineEdit, "date_file_display").setText(full_record[1].strftime("%d/%m/%Y"))
            delete_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").setText(full_record[2].strftime("%d/%m/%Y"))
            delete_fir.findChild(QtWidgets.QLineEdit, "location_display").setText(full_record[3])
            delete_fir.findChild(QtWidgets.QLineEdit, "station_display").setText(full_record[4])
            delete_fir.findChild(QtWidgets.QLineEdit, "complain_display").setText(full_record[5])
            delete_fir.findChild(QtWidgets.QLineEdit, "accused_detail_display").setText(full_record[6])
            delete_fir.findChild(QtWidgets.QLineEdit, "witness_detail_display").setText(full_record[7])
            delete_fir.findChild(QtWidgets.QLineEdit, "nature_display").setText(full_record[8])
            delete_fir.findChild(QtWidgets.QLineEdit, "section_display").setText(full_record[9])
            delete_fir.findChild(QtWidgets.QLineEdit, "officer_detail_display").setText(full_record[10])
            delete_fir.findChild(QtWidgets.QLineEdit, "status_display").setText(full_record[11])

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error retrieving FIR details: {e}")
            return

        # Connect the delete button to the deletion logic
        delete_fir.findChild(QtWidgets.QPushButton, "delete_button").clicked.connect(lambda: self.delete_fir_logic(selected_fir_no))
        delete_fir.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        delete_fir.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

    def delete_fir_logic(self, selected_fir_no):
        """Delete the FIR record from the database along with its dependencies."""
        try:
            cursor = self.connection.cursor()

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            query_delete_fir_person = """
                DELETE FROM FIR_Person
                WHERE FIR_No = ?
            """
            cursor.execute(query_delete_fir_person, (selected_fir_no,))


            # Delete the FIR record from the FIR table
            query_delete_fir = """
                DELETE FROM FIR
                WHERE FIRNo = ?
            """
            cursor.execute(query_delete_fir, (selected_fir_no,))

            # Commit the transaction
            self.connection.commit()

            QtWidgets.QMessageBox.information(self, "Success", "FIR record and its related data deleted successfully!")
            self.show_admin_dashboard()

        except pyodbc.Error as e:
            # Rollback the transaction in case of an error
            self.connection.rollback()
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error deleting FIR record: {e}")



    def search_fir_logic(self):
        search_fir = self.current_window

        # Retrieve filter values from the UI
        fir_No = str(search_fir.findChild(QtWidgets.QComboBox, "fir_combo").currentText()).strip()
        location = str(search_fir.findChild(QtWidgets.QComboBox, "location_combo").currentText()).strip()
        station_code = str(search_fir.findChild(QtWidgets.QComboBox, "station_combo").currentText()).strip()
        nature = str(search_fir.findChild(QtWidgets.QComboBox, "nature_combo").currentText()).strip()
        section = str(search_fir.findChild(QtWidgets.QComboBox, "section_combo").currentText()).strip()
        status = str(search_fir.findChild(QtWidgets.QComboBox, "status_combo").currentText()).strip()
        filing_date_text = str(search_fir.findChild(QtWidgets.QLineEdit, "date_file_display").text()).strip()
        incident_date_text = str(search_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").text()).strip()

        # Validate dates
        filing_date = self.validate_date(filing_date_text)
        incident_date = self.validate_date(incident_date_text)

        if filing_date_text and filing_date_text.strip() != "valid date (dd/MM/yyyy)" and not filing_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid filing date (dd/MM/yyyy).")
            return
        if incident_date_text and incident_date_text.strip() != "valid date (dd/MM/yyyy)" and not incident_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid incident date (dd/MM/yyyy).")
            return

        try:
            cursor = self.connection.cursor()

            # Construct the query dynamically
            query = """
                SELECT 
                    FIRNo, dateofFiling, dateofIncident, Location, 
                    policeStationCode, crimeNature, sectionofLaw, status
                FROM FIR
                WHERE 1=1
            """
            params = []

            # Apply filters only if they are provided
            if fir_No:
                query += " AND FIRNo = ?"
                params.append(fir_No)
            if location:
                query += " AND Location = ?"
                params.append(location)
            if station_code:
                query += " AND policeStationCode = ?"
                params.append(station_code)
            if nature:
                query += " AND crimeNature = ?"
                params.append(nature)
            if section:
                query += " AND sectionofLaw = ?"
                params.append(section)
            if status:
                query += " AND status = ?"
                params.append(status)
            if filing_date:
                query += " AND dateofFiling = ?"
                params.append(filing_date.toString("yyyy-MM-dd"))
            if incident_date:
                query += " AND dateofIncident = ?"
                params.append(incident_date.toString("yyyy-MM-dd"))

            # If no filters are applied, fetch all FIRs
            if not params:
                cursor.execute("SELECT FIRNo, dateofFiling, dateofIncident, Location, policeStationCode, crimeNature, sectionofLaw, status FROM FIR")
            else:
                cursor.execute(query, params)

            results = cursor.fetchall()

            # Populate the table with results
            table_widget = search_fir.findChild(QtWidgets.QTableWidget, "fir_table")
            table_widget.setRowCount(len(results))
            table_widget.setColumnCount(8)  # Based on selected columns in the query

            for i, record in enumerate(results):
                for j, value in enumerate(record):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    # Make the items non-editable
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(i, j, item)

            if not results:
                QtWidgets.QMessageBox.information(self, "No Results", "No FIRs found.")

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error querying FIR data: {e}")


    def add_fir_logic(self):
        add_fir = self.current_window

        # Retrieve the FIR number from the QLineEdit widget
        fir_no = str(add_fir.findChild(QtWidgets.QLineEdit, "fir_no_display").text()).strip()

        # Retrieve input data from the UI
        location = str(add_fir.findChild(QtWidgets.QComboBox, "location_combo").currentText()).strip()
        station = str(add_fir.findChild(QtWidgets.QComboBox, "station_combo").currentText()).strip()
        nature = str(add_fir.findChild(QtWidgets.QComboBox, "nature_combo").currentText()).strip()
        section = str(add_fir.findChild(QtWidgets.QComboBox, "section_combo").currentText()).strip()
        status = str(add_fir.findChild(QtWidgets.QComboBox, "status_combo").currentText()).strip()
        filing_date_text = str(add_fir.findChild(QtWidgets.QLineEdit, "date_file_display").text()).strip()
        incident_date_text = str(add_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").text()).strip()
        complain_details = str(add_fir.findChild(QtWidgets.QLineEdit, "complain_display").text()).strip()
        witness_details = str(add_fir.findChild(QtWidgets.QLineEdit, "witness_detail_display").text()).strip()
        accused_details = str(add_fir.findChild(QtWidgets.QLineEdit, "accused_detail_display").text()).strip()
        officer_details = str(add_fir.findChild(QtWidgets.QLineEdit, "officer_detail_display").text()).strip()

        # Validate FIR number
        if not fir_no:
            QtWidgets.QMessageBox.warning(self, "Invalid FIR Number", "FIR number is missing. Please try again.")
            return
        if not location or not station or not nature or not section or not status or not officer_details:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "location, station, nature, section, status, officer_details are mandatory!")
            return


        # Validate dates
        filing_date = self.validate_date(filing_date_text)
        incident_date = self.validate_date(incident_date_text)

        if not filing_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid filing date (dd/MM/yyyy).")
            return
        if not incident_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid incident date (dd/MM/yyyy).")
            return

        try:
            cursor = self.connection.cursor()

            # Insert the FIR record into the database
            query = """
                INSERT INTO FIR (
                    dateofFiling, dateofIncident, Location, policeStationCode, 
                    complainantDetails, accusedDetails, witnessDetails, 
                    crimeNature, sectionofLaw, officerDetails, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    filing_date.toString("yyyy-MM-dd"),
                    incident_date.toString("yyyy-MM-dd"),
                    location,
                    station,
                    complain_details,
                    accused_details,
                    witness_details,
                    nature,
                    section,
                    officer_details,
                    status,
                )
            )
            self.connection.commit()  # Commit the transaction

            

            QtWidgets.QMessageBox.information(self, "Success", "FIR added successfully!")
            self.show_admin_dashboard()
            

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error adding FIR: {e}")

    def op_add_fir_logic(self,op_ID = ""):
        add_fir = self.current_window

        # Retrieve the FIR number from the QLineEdit widget
        fir_no = str(add_fir.findChild(QtWidgets.QLineEdit, "fir_no_display").text()).strip()

        # Retrieve input data from the UI
        location = str(add_fir.findChild(QtWidgets.QComboBox, "location_combo").currentText()).strip()
        station = str(add_fir.findChild(QtWidgets.QComboBox, "station_combo").currentText()).strip()
        nature = str(add_fir.findChild(QtWidgets.QComboBox, "nature_combo").currentText()).strip()
        section = str(add_fir.findChild(QtWidgets.QComboBox, "section_combo").currentText()).strip()
        status = str(add_fir.findChild(QtWidgets.QComboBox, "status_combo").currentText()).strip()
        filing_date_text = str(add_fir.findChild(QtWidgets.QLineEdit, "date_file_display").text()).strip()
        incident_date_text = str(add_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").text()).strip()
        complain_details = str(add_fir.findChild(QtWidgets.QLineEdit, "complain_display").text()).strip()
        witness_details = str(add_fir.findChild(QtWidgets.QLineEdit, "witness_detail_display").text()).strip()
        accused_details = str(add_fir.findChild(QtWidgets.QLineEdit, "accused_detail_display").text()).strip()
        officer_details = str(add_fir.findChild(QtWidgets.QLineEdit, "officer_detail_display").text()).strip()

        # Validate FIR number
        if not fir_no:
            QtWidgets.QMessageBox.warning(self, "Invalid FIR Number", "FIR number is missing. Please try again.")
            return
        if not location or not station or not nature or not section or not status or not officer_details:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "location, station, nature, section, status, officer_details are mandatory!")
            return


        # Validate dates
        filing_date = self.validate_date(filing_date_text)
        incident_date = self.validate_date(incident_date_text)

        if not filing_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid filing date (dd/MM/yyyy).")
            return
        if not incident_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Date", "Please enter a valid incident date (dd/MM/yyyy).")
            return

        try:
            cursor = self.connection.cursor()

            # Insert the FIR record into the database
            query = """
                INSERT INTO FIR_Request (
                    FIRNo,ApprovalDate,approval,requestor_user_id,approver_user_id,new_date_of_Filing, new_date_of_incident, new_Location , new_policeStationCode, 
                    new_complainantDetails, new_accusedDetails, new_witnessDetails, 
                    new_crimeNature, new_sectionofLaw, new_officerDetails, new_status
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """
            current_date = cursor.execute("SELECT CAST(GETDATE() AS DATE) AS CURRENT_DATE")
            cursor.execute(
                query,
                (
                    fir_no,
                    "",
                    "",
                    op_ID,
                    "",
                    filing_date.toString("yyyy-MM-dd"),
                    incident_date.toString("yyyy-MM-dd"),
                    location,
                    station,
                    complain_details,
                    accused_details,
                    witness_details,
                    nature,
                    section,
                    officer_details,
                    status,
                )
            )
            self.connection.commit()  # Commit the transaction

            

            QtWidgets.QMessageBox.information(self, "Success", "FIR added successfully!")
            self.show_admin_dashboard()
            

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error adding FIR: {e}")




    def update_fir_logic(self, fir_data):
        update_fir = self.current_window

        # Get input values from the form
        location = update_fir.findChild(QtWidgets.QComboBox, "location_combo").currentText().strip()
        station = update_fir.findChild(QtWidgets.QComboBox, "station_combo").currentText().strip()
        nature = update_fir.findChild(QtWidgets.QComboBox, "nature_combo").currentText().strip()
        section = update_fir.findChild(QtWidgets.QComboBox, "section_combo").currentText().strip()
        status = update_fir.findChild(QtWidgets.QComboBox, "status_combo").currentText().strip()
        filing_date_text = update_fir.findChild(QtWidgets.QLineEdit, "date_file_display").text().strip()
        incident_date_text = update_fir.findChild(QtWidgets.QLineEdit, "date_inc_display").text().strip()
        complain_details = update_fir.findChild(QtWidgets.QLineEdit, "complain_display").text().strip()
        witness_details = update_fir.findChild(QtWidgets.QLineEdit, "witness_detail_display").text().strip()
        accused_details = update_fir.findChild(QtWidgets.QLineEdit, "accused_detail_display").text().strip()
        officer_details = update_fir.findChild(QtWidgets.QLineEdit, "officer_detail_display").text().strip()


        fir_no = fir_data[0]
        if not location:
            location = fir_data[3]
        if not station:
            station = fir_data[4]
        if not nature:
            nature = fir_data[8]
        if not section:
            section = fir_data[9]
        if not status:
            status = fir_data[11]

        filing_date = self.validate_date(filing_date_text)
        incident_date = self.validate_date(incident_date_text)

        if not filing_date:
            filing_date = fir_data[1]  # Use existing date if invalid or not provided
        else:
            filing_date = filing_date.toString("dd/MM/yyyy")

        if not incident_date:
            incident_date = fir_data[2]
        else:
            incident_date = incident_date.toString("dd/MM/yyyy")


        if not complain_details:
            complain_details = fir_data[5]
        if not witness_details:
            witness_details = fir_data[7]
        if not accused_details:
            accused_details = fir_data[6]
        if not officer_details:
            officer_details = fir_data[10]
        try:
            cursor = self.connection.cursor()

            # Update the FIR record in the database
            query = """
            UPDATE FIR
            SET dateofFiling = ?, dateofIncident = ?, Location = ?, policeStationCode = ?, complainantDetails = ?,
                accusedDetails = ?, witnessDetails = ?, crimeNature = ?, sectionofLaw = ?, officerDetails = ?, status = ?
            WHERE FIRNo = ?
            """
            cursor.execute(query, (
                filing_date,
                incident_date,
                location,
                station,
                complain_details,
                accused_details,
                witness_details,
                nature,
                section,
                officer_details,
                status,
                fir_no
            ))
            self.connection.commit()

            QtWidgets.QMessageBox.information(self, "Success", "FIR updated successfully!")
            self.show_admin_dashboard()

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error updating FIR: {e}")

    def populate_nature_of_crime(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT crimeNature FROM FIR")
            crimes = [row[0] for row in cursor.fetchall()]
            crime_combo_box = self.current_window.findChild(QtWidgets.QComboBox, "nature_combo")
            crime_combo_box.addItems([""] + crimes)
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching crime nature: {e}")

    def populate_section_of_law(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT sectionofLaw FROM FIR")
            sections = [row[0] for row in cursor.fetchall()]
            section_combo_box = self.current_window.findChild(QtWidgets.QComboBox, "section_combo")
            section_combo_box.addItems([""] + sections)
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching sections of law: {e}")

    def populate_station_code(self, location):
        station_codes = {
            "Karachi": "KHI-001",
            "Lahore": "LHR-002",
            "Islamabad": "ISB-003",
            "Peshawar": "PSW-004",
            "Quetta": "QTA-005"
        }
        station_code = station_codes.get(location, "UNKNOWN")
        station_combo_box = self.current_window.findChild(QtWidgets.QComboBox, "station_combo")
        station_combo_box.clear()
        station_combo_box.addItem(station_code)

    def show_search_convicted_person(self):
        """Show the Search Convicted Person Records screen."""
        try:
            # Load the Search Convicted Person UI
            search_convicted_person = self.load_ui("screens/search_convicted_person_record.ui")
            self.set_main_widget(search_convicted_person)

            cursor = self.connection.cursor()

            # --- Populate Combo Boxes ---
            # Convicted Person IDs
            cursor.execute("SELECT DISTINCT Person_ID FROM Convicted_Person")
            person_ids = [""] + [str(row[0]) for row in cursor.fetchall()]
            search_convicted_person.findChild(QtWidgets.QComboBox, "person_combo").addItems(person_ids)

            # Gender
            cursor.execute("SELECT DISTINCT Gender FROM Convicted_Person")
            genders = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            search_convicted_person.findChild(QtWidgets.QComboBox, "gender_combo").addItems(genders)

            # Fingerprint IDs
            cursor.execute("SELECT DISTINCT FingerPrintID FROM Convicted_Person")
            fingerprints = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            search_convicted_person.findChild(QtWidgets.QComboBox, "fp_combo").addItems(fingerprints)

            # DNA Profiles
            cursor.execute("SELECT DISTINCT DNAProfile FROM Convicted_Person")
            dna_profiles = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            search_convicted_person.findChild(QtWidgets.QComboBox, "dna_combo").addItems(dna_profiles)

            # Status
            cursor.execute("SELECT DISTINCT Status FROM Convicted_Person")
            statuses = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            search_convicted_person.findChild(QtWidgets.QComboBox, "status_combo").addItems(statuses)

            # Charges
            cursor.execute("SELECT DISTINCT Charges FROM Convicted_Person")
            charges = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            search_convicted_person.findChild(QtWidgets.QComboBox, "charge_combo").addItems(charges)

            # --- Connect Buttons ---
            search_convicted_person.findChild(QtWidgets.QPushButton, "search_button").clicked.connect(self.search_person_logic)
            search_convicted_person.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            search_convicted_person.findChild(QtWidgets.QPushButton, "view_button").clicked.connect(
                lambda: self.view_selected_person(search_convicted_person)
            )
            search_convicted_person.findChild(QtWidgets.QPushButton, "add_button").clicked.connect(self.show_add_convicted_person)
            search_convicted_person.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(
                lambda: self.show_update_person(search_convicted_person)
            )
            search_convicted_person.findChild(QtWidgets.QPushButton, "delete_button").clicked.connect(
                lambda: self.delete_person_record(search_convicted_person)
            )
            search_convicted_person.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

            # Populate table with all convicted persons by default
            self.populate_all_convicted_persons(search_convicted_person)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading convicted person data: {e}")
        except AttributeError as e:
            print(f"Error in Search Convicted Person button setup: {e}")


    def populate_all_convicted_persons(self, search_convicted_person):
        """Populate the table widget with all convicted persons by default."""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    Person_ID, CNIC, Name, DateOfBirth, LastKnownAddress, Gender, 
                    FingerPrintID, DNAProfile, Charges, Status
                FROM Convicted_Person
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # Populate the table widget with all convicted persons
            table_widget = search_convicted_person.findChild(QtWidgets.QTableWidget, "person_table")
            table_widget.setRowCount(len(results))
            table_widget.setColumnCount(10)  # Adjust the column count to match the query

            for i, record in enumerate(results):
                for j, value in enumerate(record):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    # Make the items non-editable
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(i, j, item)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading all convicted persons: {e}")


    def search_person_logic(self):
        search_person = self.current_window

        # Retrieve filter values from the UI
        person_id = str(search_person.findChild(QtWidgets.QComboBox, "person_combo").currentText()).strip()
        gender = str(search_person.findChild(QtWidgets.QComboBox, "gender_combo").currentText()).strip()
        dna = str(search_person.findChild(QtWidgets.QComboBox, "dna_combo").currentText()).strip()
        status = str(search_person.findChild(QtWidgets.QComboBox, "status_combo").currentText()).strip()
        fingerprint = str(search_person.findChild(QtWidgets.QComboBox, "fp_combo").currentText()).strip()
        charge = str(search_person.findChild(QtWidgets.QComboBox, "charge_combo").currentText()).strip()
        last_address = str(search_person.findChild(QtWidgets.QLineEdit, "address_display").text()).strip()
        name = str(search_person.findChild(QtWidgets.QLineEdit, "name_display").text()).strip()

        try:
            cursor = self.connection.cursor()

            # Construct dynamic SQL query
            query = """
                SELECT 
                    Person_ID, CNIC, Name, DateOfBirth, LastKnownAddress, Gender, 
                    FingerPrintID, DNAProfile, Charges, Status
                FROM Convicted_Person
                WHERE 1=1
            """
            params = []

            # Apply filters dynamically
            if person_id:
                query += " AND Person_ID = ?"
                params.append(person_id)
            if gender:
                query += " AND Gender = ?"
                params.append(gender)
            if dna:
                query += " AND DNAProfile = ?"
                params.append(dna)
            if status:
                query += " AND Status = ?"
                params.append(status)
            if fingerprint:
                query += " AND FingerPrintID = ?"
                params.append(fingerprint)
            if charge:
                query += " AND Charges = ?"
                params.append(charge)
            if last_address:
                query += " AND LastKnownAddress LIKE ?"
                params.append(f"%{last_address}%")
            if name:
                query += " AND Name LIKE ?"
                params.append(f"%{name}%")

            # If no filters are applied, fetch all convicted person records
            if not params:
                cursor.execute("SELECT Person_ID, CNIC, Name, DateOfBirth, LastKnownAddress, Gender, FingerPrintID, DNAProfile, Charges, Status  FROM Convicted_Person WHERE 1=1")
            else:
                cursor.execute(query, params)
            results = cursor.fetchall()


            # Populate the table with matching records
            table_widget = search_person.findChild(QtWidgets.QTableWidget, "person_table")
            table_widget.setRowCount(len(results))
            table_widget.setColumnCount(10)  # Adjust based on the columns you want to display

            # Insert results into the table
            for i, record in enumerate(results):
                for j, value in enumerate(record):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    # Make the items non-editable
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(i, j, item)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error querying convicted person data: {e}")


    def view_selected_person(self, search_convicted_person):
        """Get the selected convicted person from the table and show details in the view screen."""
        table_widget = search_convicted_person.findChild(QtWidgets.QTableWidget, "person_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to view details.")
            return

        # Extract the Person_ID from the selected row (assuming it's in the first column)
        person_id_item = table_widget.item(selected_row, 0)
        if not person_id_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve person details.")
            return

        selected_person_id = person_id_item.text()

        try:
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    Person_ID, Name, DateOfBirth, Gender, LastKnownAddress, 
                    Aliases, physicalDescription, FingerPrintID, DNAProfile, Status
                FROM Convicted_Person
                WHERE Person_ID = ?
            """
            cursor.execute(query, (selected_person_id,))
            person_record = cursor.fetchone()

            if not person_record:
                QtWidgets.QMessageBox.warning(self, "Error", "Person details not found in the database.")
                return

            # Navigate to the "View Person" screen and display details
            self.show_view_person(person_record)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching person details: {e}")


    def show_view_person(self, person_record):
        """Display person details in the View Person screen."""
        view_person = self.load_ui("screens/view_convicted_person_record.ui")
        self.set_main_widget(view_person)

        # Populate the fields with the person record
        try:
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_4").setText(str(person_record[0]))
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_5").setText(person_record[1])
            view_person.findChild(QtWidgets.QDateEdit, "dateEdit").setDate(person_record[2])
            view_person.findChild(QtWidgets.QComboBox, "comboBox").setCurrentText(person_record[3])
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_8").setText(person_record[4])
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_6").setText(person_record[5])
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_9").setText(person_record[6])
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_10").setText(person_record[7])
            view_person.findChild(QtWidgets.QLineEdit, "lineEdit_11").setText(person_record[8])
            view_person.findChild(QtWidgets.QLineEdit, "comboBox_3").setText(person_record[9])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Data mapping issue: {e}")

        # Connect navigation buttons
        view_person.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        view_person.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)



    def show_add_convicted_person(self):
        try:
            # Load the Add Convicted Person UI
            add_person = self.load_ui("screens/add_convicted_person_record.ui")
            self.set_main_widget(add_person)
            # --- Populate Combo Boxes ---
            cursor = self.connection.cursor()
            cursor.execute("SELECT ISNULL(MAX(Person_ID), 0) + 1 FROM Convicted_Person")

            next_id_no = cursor.fetchone()[0]  # Get the next FIR number
            person_id_display = add_person.findChild(QtWidgets.QLineEdit, "lineEdit_personID")
            if person_id_display:
                person_id_display.setText(str(next_id_no))
                person_id_display.setReadOnly(True)

            # --- Populate Combo Boxes ---
            cursor = self.connection.cursor()

            # --- Populate Combo Boxes ---

            # Gender
            cursor.execute("SELECT DISTINCT Gender FROM Convicted_Person")
            genders = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            add_person.findChild(QtWidgets.QComboBox, "comboBox_gender").addItems(genders)

            # Fingerprint IDs
            cursor.execute("SELECT DISTINCT FingerPrintID FROM Convicted_Person")
            fingerprints = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            add_person.findChild(QtWidgets.QComboBox, "fingerprint_line").addItems(fingerprints)

            # DNA Profiles
            cursor.execute("SELECT DISTINCT DNAProfile FROM Convicted_Person")
            dna_profiles = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            add_person.findChild(QtWidgets.QComboBox, "dna_line").addItems(dna_profiles)

            # Status
            cursor.execute("SELECT DISTINCT Status FROM Convicted_Person")
            statuses = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            add_person.findChild(QtWidgets.QComboBox, "status_line").addItems(statuses)

            # Charges
            cursor.execute("SELECT DISTINCT Charges FROM Convicted_Person")
            charges = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            add_person.findChild(QtWidgets.QComboBox, "charges_line").addItems(charges)

            # --- Populate Gender ComboBox ---
            # gender_combo = add_person.findChild(QtWidgets.QComboBox, "comboBox_gender")
            # gender_combo.addItems(["", "Male", "Female", "Other"])

            # # --- Set Default Date Placeholder ---
            # date_edit_dob = add_person.findChild(QtWidgets.QDateEdit, "dateEdit_dob")
            # date_edit_dob.setDisplayFormat("dd/MM/yyyy")
            # date_edit_dob.setDate(QDate.currentDate())

            # --- Connect Buttons ---
            # Submit button for adding data
            submit_button = add_person.findChild(QtWidgets.QPushButton, "pushButton_submit")
            submit_button.clicked.connect(self.add_convicted_person_logic)

            # # File upload buttons (if implemented)
            # upload_dna_button = add_person.findChild(QtWidgets.QPushButton, "pushButton_uploadDNA")
            # upload_dna_button.clicked.connect(lambda: self.upload_file("DNAProfile"))

            # upload_fingerprint_button = add_person.findChild(QtWidgets.QPushButton, "pushButton_uploadFingerprint")
            # upload_fingerprint_button.clicked.connect(lambda: self.upload_file("FingerPrintID"))

            # upload_photo_button = add_person.findChild(QtWidgets.QPushButton, "pushButton_uploadPhoto")
            # upload_photo_button.clicked.connect(lambda: self.upload_file("Photograph"))

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while loading the Add Convicted Person form: {e}")

        add_person.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)

    def add_convicted_person_logic(self):
        add_person = self.current_window

        # Retrieve input data from the UI
        name = add_person.findChild(QtWidgets.QLineEdit, "lineEdit_name").text().strip()
        dob = add_person.findChild(QtWidgets.QDateEdit, "dateEdit_dob").date().toString("yyyy-MM-dd")
        address = add_person.findChild(QtWidgets.QLineEdit, "lineEdit_address").text().strip()
        gender = add_person.findChild(QtWidgets.QComboBox, "comboBox_gender").currentText().strip()
        physical_desc = add_person.findChild(QtWidgets.QLineEdit, "lineEdit_physicalDesc").text().strip()
        aliases = add_person.findChild(QtWidgets.QLineEdit, "lineEdit_aliases").text().strip()
        fingerprint = add_person.findChild(QtWidgets.QComboBox, "fingerprint_line").currentText().strip()
        dna = add_person.findChild(QtWidgets.QComboBox, "dna_line").currentText().strip()
        cnic = add_person.findChild(QtWidgets.QLineEdit, "cnic_line").text().strip()
        charges = add_person.findChild(QtWidgets.QComboBox, "charges_line").currentText().strip()
        status = add_person.findChild(QtWidgets.QComboBox, "status_line").currentText().strip()
        arrest_history = add_person.findChild(QtWidgets.QLineEdit, "arrest_line").text().strip()
        convic_detail = add_person.findChild(QtWidgets.QLineEdit, "convict_line").text().strip()
        incarc_detail = add_person.findChild(QtWidgets.QLineEdit, "incarc_line").text().strip()
        parole_detail = add_person.findChild(QtWidgets.QLineEdit, "parole_line").text().strip()
        remarks = add_person.findChild(QtWidgets.QLineEdit, "remarks_line").text().strip()
        # Validate mandatory fields
        if not name or not dob:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Name and date of birth are mandatory fields.")
            return

        try:
            cursor = self.connection.cursor()

            # SQL Query to Insert Convicted Person Data
            query = """
                INSERT INTO Convicted_Person (
                    CNIC, Name, DateOfBirth, LastKnownAddress, Gender,FingerPrintID,DNAProfile,Charges,Status, Aliases, PhysicalDescription, ArrestHistory, ConvictionDetails, IncarcerationDetails,ParoleDetails,Remarks
                ) VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?,?,?)
            """
            cursor.execute(query, (cnic,name, dob, address, gender,fingerprint,dna,charges,status,aliases, physical_desc, arrest_history,convic_detail,incarc_detail,parole_detail,remarks))
            self.connection.commit()  # Commit the transaction

            QtWidgets.QMessageBox.information(self, "Success", "Convicted Person added successfully!")
            self.show_admin_dashboard()

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error adding convicted person: {e}")

    def show_update_person(self, search_convicted_widget):
        """Display the update convicted person form with the selected person's details."""
        table_widget = search_convicted_widget.findChild(QtWidgets.QTableWidget, "person_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to update.")
            return

        # Extract the Person ID from the selected row (assuming it's in the first column)
        person_id_item = table_widget.item(selected_row, 0)
        if not person_id_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve convicted person details.")
            return

        selected_person_id = person_id_item.text()

        try:

            # Load the Update Convicted Person UI
            update_person = self.load_ui("screens\\update_convicted_person_record.ui")
            self.set_main_widget(update_person)
             # Fetch the person's details from the database using the selected Person ID
            cursor = self.connection.cursor()
                        # Gender
            cursor.execute("SELECT DISTINCT Gender FROM Convicted_Person")
            genders = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            update_person.findChild(QtWidgets.QComboBox, "gender_line").addItems(genders)

            # Fingerprint IDs
            cursor.execute("SELECT DISTINCT FingerPrintID FROM Convicted_Person")
            fingerprints = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            update_person.findChild(QtWidgets.QComboBox, "fingerprint_line").addItems(fingerprints)

            # DNA Profiles
            cursor.execute("SELECT DISTINCT DNAProfile FROM Convicted_Person")
            dna_profiles = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            update_person.findChild(QtWidgets.QComboBox, "dna_line").addItems(dna_profiles)

            # Status
            cursor.execute("SELECT DISTINCT Status FROM Convicted_Person")
            statuses = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            update_person.findChild(QtWidgets.QComboBox, "status_line").addItems(statuses)

            # Charges
            cursor.execute("SELECT DISTINCT Charges FROM Convicted_Person")
            charges = [""] + [row[0] for row in cursor.fetchall() if row[0]]
            update_person.findChild(QtWidgets.QComboBox, "charge_line").addItems(charges)

            query = """
                SELECT Person_ID,CNIC, Name, DateOfBirth, LastKnownAddress, Gender,FingerPrintID,DNAProfile,Charges,Status, Aliases, PhysicalDescription, ArrestHistory, ConvictionDetails, IncarcerationDetails,ParoleDetails,Remarks
                FROM Convicted_Person
                WHERE Person_ID = ?
            """
            cursor.execute(query, (selected_person_id,))
            person_data = cursor.fetchone()

            if not person_data:
                QtWidgets.QMessageBox.warning(self, "Error", "Convicted person details not found.")
                return

            # Populate the fields with the person's details
            update_person.findChild(QtWidgets.QLineEdit, "person_id_line").setText(str(person_data[0]))

            # Connect the Update button to the update logic
            update_person.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(
                lambda: self.update_convicted_person_logic(person_data)
            )

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching convicted person details: {e}")
        update_person.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        update_person.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)


    def update_convicted_person_logic(self, person_data):
        update_person = self.current_window

        # Retrieve updated data from the UI
        name = update_person.findChild(QtWidgets.QLineEdit, "name_line").text().strip()
        dob = update_person.findChild(QtWidgets.QDateEdit, "dateEdit_dob").date().toString("yyyy-MM-dd")
        address = update_person.findChild(QtWidgets.QLineEdit, "address_line").text().strip()
        gender = update_person.findChild(QtWidgets.QComboBox, "gender_line").currentText().strip()
        physical_desc = update_person.findChild(QtWidgets.QLineEdit, "physical_line").text().strip()
        aliases = update_person.findChild(QtWidgets.QLineEdit, "alias_line").text().strip()
        fingerprint = update_person.findChild(QtWidgets.QComboBox, "fingerprint_line").currentText().strip()
        dna = update_person.findChild(QtWidgets.QComboBox, "dna_line").currentText().strip()
        cnic = update_person.findChild(QtWidgets.QLineEdit, "cnic_line").text().strip()
        charges = update_person.findChild(QtWidgets.QComboBox, "charge_line").currentText().strip()
        status = update_person.findChild(QtWidgets.QComboBox, "status_line").currentText().strip()
        arrest_history = update_person.findChild(QtWidgets.QLineEdit, "arrest_line").text().strip()
        convict_detail = update_person.findChild(QtWidgets.QLineEdit, "convict_line").text().strip()
        incarc_detail = update_person.findChild(QtWidgets.QLineEdit, "incarc_line").text().strip()
        parole_detail = update_person.findChild(QtWidgets.QLineEdit, "parole_line").text().strip()
        remarks = update_person.findChild(QtWidgets.QLineEdit, "remark_line").text().strip()

        # Validate mandatory fields
        if not name:
            name = person_data[2]
        if not dob:
            dob = person_data[3]
        if not address:
            address = person_data[4]
        if not gender:
            gender = person_data[5]
        if not physical_desc:
            physical_desc = person_data[11]
        if not aliases:
            aliases = person_data[10]
        if not fingerprint:
            fingerprint = person_data[6]
        if not dna:
            dna = person_data[7]
        if not cnic:
            cnic = person_data[1]
        if not charges:
            charges = person_data[8]
        if not status:
            status = person_data[9]
        if not arrest_history:
            arrest_history = person_data[12]
        if not convict_detail :
            convict_detail  = person_data[13]
        if not incarc_detail:
            incarc_detail = person_data[14]
        if not parole_detail :
            parole_detail  = person_data[15]
        if not remarks:
            remarks = person_data[16]
        try:
            cursor = self.connection.cursor()

            # Update the person's details in the database
            query = """
                UPDATE Convicted_Person
                SET CNIC = ? , Name = ?, DateOfBirth = ?, LastKnownAddress = ?, Gender = ?,FingerPrintID = ?,DNAProfile = ?,Charges = ?,Status = ?, Aliases = ?, PhysicalDescription = ?, ArrestHistory = ?, ConvictionDetails = ?, IncarcerationDetails = ?,ParoleDetails = ?,Remarks = ?
                WHERE Person_ID = ?
            """
            cursor.execute(query, (cnic, name, dob, address, gender, fingerprint, dna, charges, status, aliases, physical_desc, arrest_history, convict_detail, incarc_detail, parole_detail, remarks,   person_data[0]))
            self.connection.commit()  # Commit the transaction

            QtWidgets.QMessageBox.information(self, "Success", "Convicted person details updated successfully!")
            self.show_admin_dashboard()

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error updating convicted person: {e}")

    def delete_person_record(self, search_convicted_widget):
        """Get the selected convicted person from the table and display details for confirmation before deletion."""
        table_widget = search_convicted_widget.findChild(QtWidgets.QTableWidget, "person_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
            return

        # Extract the Person ID from the selected row (assuming it's in the first column)
        person_id_item = table_widget.item(selected_row, 0)
        if not person_id_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve convicted person details.")
            return

        selected_person_id = person_id_item.text()

        try:
            # Fetch the person's details from the database using the selected Person ID
            cursor = self.connection.cursor()
            query = """
                SELECT Person_ID, Name, DateOfBirth, LastKnownAddress, Gender
                FROM Convicted_Person
                WHERE Person_ID = ?
            """
            cursor.execute(query, (selected_person_id,))
            person_data = cursor.fetchone()

            if not person_data:
                QtWidgets.QMessageBox.warning(self, "Error", "Convicted person details not found.")
                return

            # Load the Delete Confirmation UI
            delete_person = self.load_ui("screens/delete_convicted_person_record.ui")
            self.set_main_widget(delete_person)

            # Populate the fields with the person's details for confirmation
            delete_person.findChild(QtWidgets.QLineEdit, "lineEdit_4").setText(str(person_data[0]))
            delete_person.findChild(QtWidgets.QLineEdit, "lineEdit_5").setText(person_data[1])
            delete_person.findChild(QtWidgets.QDateEdit, "dateEdit").date().toString("yyyy-MM-dd")
            delete_person.findChild(QtWidgets.QLineEdit, "lineEdit_17").setText(person_data[3])
            delete_person.findChild(QtWidgets.QLineEdit, "lineEdit_2").setText(person_data[4])

            # Disable all fields for read-only confirmation
            # for field in ["lineEdit_personID", "lineEdit_name", "dateEdit_dob", "lineEdit_address", "comboBox_gender"]:
            #     widget = delete_person.findChild(QtWidgets.QLineEdit, field)
            #     if widget:
            #         widget.setReadOnly(True)

            # Connect the delete button to the deletion logic
            delete_person.findChild(QtWidgets.QPushButton, "pushButton_4").clicked.connect(
                lambda: self.delete_person_logic(selected_person_id)
            )

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error fetching convicted person details: {e}")

    def delete_person_logic(self, person_id):
        """Delete the convicted person record from the database."""
        try:
            cursor = self.connection.cursor()

            # Check for dependencies before deletion
            # Example: Check if the person is referenced in other tables
            dependency_query = """
                SELECT COUNT(*)
                FROM FIR_Person
                WHERE Person_ID = ?
            """
            cursor.execute(dependency_query, (person_id,))
            if cursor.fetchone()[0] > 0:
                QtWidgets.QMessageBox.warning(self, "Dependency Error", "This person is referenced in other records and cannot be deleted.")
                return

            # Delete the person's record
            query = "DELETE FROM Convicted_Person WHERE Person_ID = ?"
            cursor.execute(query, (person_id,))
            self.connection.commit()  # Commit the transaction

            QtWidgets.QMessageBox.information(self, "Success", f"Convicted person record (ID: {person_id}) deleted successfully!")
            self.show_admin_dashboard()

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error deleting convicted person record: {e}")


    # def add_accused_to_fir_person(self, fir_no, person_id, accused_details):
    #     """
    #     Add an accused person to FIR_Person and update Convicted_Person if necessary.
    #     """
    #     try:
    #         cursor = self.connection.cursor()

    #         # Insert the accused details into FIR_Person
    #         query_fir_person = """
    #         INSERT INTO FIR_Person (FIRNo, Person_ID)
    #         VALUES (?, ?);
    #         """
    #         cursor.execute(query_fir_person, (fir_no, person_id))

    #         # Update Convicted_Person
    #         query_convicted_person = """
    #         IF EXISTS (SELECT 1 FROM Convicted_Person WHERE Person_ID = ?)
    #         BEGIN
    #             UPDATE Convicted_Person
    #             SET Status = ?, DNAProfile = ?, FingerPrintID = ?, LastKnownAddress = ?
    #             WHERE Person_ID = ?;
    #         END
    #         ELSE
    #         BEGIN
    #             INSERT INTO Convicted_Person (Person_ID, CNIC, Name, DateOfBirth, LastKnownAddress, Gender, DNAProfile, FingerPrintID, Status)
    #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    #         END;
    #         """
    #         cursor.execute(query_convicted_person, (
    #             person_id, accused_details["Status"], accused_details["DNAProfile"],
    #             accused_details["FingerPrintID"], accused_details["LastKnownAddress"],
    #             person_id,  # For updating if the record exists
    #             person_id, accused_details["CNIC"], accused_details["Name"],
    #             accused_details["DateOfBirth"], accused_details["LastKnownAddress"],
    #             accused_details["Gender"], accused_details["DNAProfile"],
    #             accused_details["FingerPrintID"], accused_details["Status"]
    #         ))

    #         self.connection.commit()
    #         QtWidgets.QMessageBox.information(self, "Success", "Accused person added and updated successfully!")

    #     except pyodbc.Error as e:
    #         QtWidgets.QMessageBox.critical(self, "Database Error", f"Error adding accused person: {e}")

    # def delete_fir_and_check_convicted_person(self, fir_no):
    #     """
    #     Delete FIR and ensure convicted person records are deleted if no other FIR references them.
    #     """
    #     try:
    #         cursor = self.connection.cursor()

    #         # Begin transaction
    #         self.connection.autocommit = False

    #         # Delete related records in FIR_Person
    #         query_delete_fir_person = """
    #         DELETE FROM FIR_Person
    #         WHERE FIRNo = ?;
    #         """
    #         cursor.execute(query_delete_fir_person, (fir_no,))

    #         # Delete FIR entry
    #         query_delete_fir = """
    #         DELETE FROM FIR
    #         WHERE FIRNo = ?;
    #         """
    #         cursor.execute(query_delete_fir, (fir_no,))

    #         # Delete convicted persons with no FIR references
    #         query_delete_convicted_person = """
    #         DELETE FROM Convicted_Person
    #         WHERE Person_ID NOT IN (SELECT DISTINCT Person_ID FROM FIR_Person);
    #         """
    #         cursor.execute(query_delete_convicted_person)

    #         # Commit transaction
    #         self.connection.commit()
    #         self.connection.autocommit = True

    #         QtWidgets.QMessageBox.information(self, "Success", "FIR and related records deleted successfully!")

    #     except pyodbc.Error as e:
    #         self.connection.rollback()  # Rollback transaction in case of error
    #         QtWidgets.QMessageBox.critical(self, "Database Error", f"Error deleting FIR: {e}")



    def show_manage_requests(self):
        """Show the Requests screen."""
        manage_requests = self.load_ui("screens/admin_request_page.ui")
        self.set_main_widget(manage_requests)

        try:
            cursor = self.connection.cursor()

            # Populate operator ID combo box
            query_operator_ids = "SELECT DISTINCT requestor_user_id FROM Person_Request UNION SELECT DISTINCT approver_user_id FROM Person_Request"
            cursor.execute(query_operator_ids)
            operator_ids = [row[0] for row in cursor.fetchall()]
            
            # Convert IDs to strings before adding to the combo box
            operator_id_combo = manage_requests.findChild(QtWidgets.QComboBox, "operator_id_combo")
            operator_id_combo.clear()
            operator_id_combo.addItems([""] + [str(id) for id in operator_ids])

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error loading requests data: {e}")
            return

        # Connect buttons
        manage_requests.findChild(QtWidgets.QPushButton, "search_button").clicked.connect(self.search_request_logic)
        try:
            manage_requests.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
            manage_requests.findChild(QtWidgets.QPushButton, "approve_button").clicked.connect(lambda: self.approve_request(manage_requests))
            manage_requests.findChild(QtWidgets.QPushButton, "deny_button").clicked.connect(lambda: self.deny_request(manage_requests))
            manage_requests.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        except AttributeError:
            print("Error: 'home_button' not found in admin_request_page.ui.")



    def search_request_logic(self):
        search_request = self.current_window
        self.clear_table_request(search_request)

        # Retrieve filter values from the UI
        request_id = str(search_request.findChild(QtWidgets.QComboBox, "request_combo").currentText()).strip()
        request_user_id = str(search_request.findChild(QtWidgets.QComboBox, "request_user_id_combo").currentText()).strip()
        approve_user_id = str(search_request.findChild(QtWidgets.QComboBox, "approve_user_id_combo").currentText()).strip()
        approval = str(search_request.findChild(QtWidgets.QComboBox, "approval").currentText()).strip()
        operator_id = str(search_request.findChild(QtWidgets.QComboBox, "operator_id_combo").currentText()).strip()
        person_id = str(search_request.findChild(QtWidgets.QComboBox, "person_id_combo").currentText()).strip()
        fir_id = str(search_request.findChild(QtWidgets.QComboBox, "fir_id_combo").currentText()).strip()

        try:
            # Connect to the database
            cursor = self.connection.cursor()

            # Construct the dynamic query
            query = """
                SELECT RequestID, person_id, requestor_user_id, approver_user_id, approval, ApprovalDate
                FROM Person_Request
                WHERE 1=1
            """
            params = []

            # Add filters dynamically
            if request_id:
                query += " AND RequestID = ?"
                params.append(request_id)
            if request_user_id:
                query += " AND requestor_user_id = ?"
                params.append(request_user_id)
            if approve_user_id:
                query += " AND approver_user_id = ?"
                params.append(approve_user_id)
            if approval:
                query += " AND approval = ?"
                params.append(1 if approval.lower() == "approved" else 0)
            if operator_id:
                query += " AND person_id = ?"
                params.append(operator_id)
            if person_id:
                query += " AND person_id = ?"
                params.append(person_id)

            # Execute the query
            cursor.execute(query, params)
            results = cursor.fetchall()

            # If no records found, clear the table and return
            if not results:
                self.clear_table_request(search_request)
                return

            # Populate the table with results
            table_widget = search_request.findChild(QtWidgets.QTableWidget, "request_table")
            table_widget.setRowCount(len(results))
            table_widget.setColumnCount(len(results[0]))

            for i, row in enumerate(results):
                for j, value in enumerate(row):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    table_widget.setItem(i, j, item)

        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error querying requests: {e}")

    def approve_request(self, manage_requests_widget):
        """Approve the selected request in the table."""
        table_widget = manage_requests_widget.findChild(QtWidgets.QTableWidget, "request_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to approve.")
            return

        # Extract the RequestID and current approval status from the selected row
        request_id_item = table_widget.item(selected_row, 0)
        approval_status_item = table_widget.item(selected_row, 3)

        if not request_id_item or not approval_status_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve request details.")
            return

        request_id = request_id_item.text()
        current_status = approval_status_item.text()

        # Check if the current status is already approved
        if current_status.lower() == "approved":
            QtWidgets.QMessageBox.warning(self, "Already Approved", "This request is already approved.")
            return

        try:
            cursor = self.connection.cursor()

            # Determine the table for the request based on the selected RequestID
            # Check if the RequestID exists in the Person_Request table
            query_check_person_request = "SELECT COUNT(*) FROM Person_Request WHERE RequestID = ?"
            cursor.execute(query_check_person_request, (request_id,))
            is_person_request = cursor.fetchone()[0] > 0

            if is_person_request:
                # Update approval status for Person_Request
                query_update_person_request = """
                    UPDATE Person_Request
                    SET approval = 1, ApprovalDate = GETDATE()
                    WHERE RequestID = ?
                """
                cursor.execute(query_update_person_request, (request_id,))
            else:
                # Update approval status for FIR_Request
                query_update_fir_request = """
                    UPDATE FIR_Request
                    SET approval = 1, ApprovalDate = GETDATE()
                    WHERE RequestID = ?
                """
                cursor.execute(query_update_fir_request, (request_id,))

            # Commit the changes
            self.connection.commit()

            # Refresh the table to reflect the changes
            self.search_request_logic()

            QtWidgets.QMessageBox.information(self, "Success", "Request approved successfully.")

        except pyodbc.Error as e:
            self.connection.rollback()  # Rollback changes in case of error
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error updating approval status: {e}")

    def deny_request(self, manage_requests_widget):
        """Deny the selected request in the table."""
        table_widget = manage_requests_widget.findChild(QtWidgets.QTableWidget, "request_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to deny.")
            return

        # Extract the RequestID and current approval status from the selected row
        request_id_item = table_widget.item(selected_row, 0)
        approval_status_item = table_widget.item(selected_row, 3)

        if not request_id_item or not approval_status_item:
            QtWidgets.QMessageBox.warning(self, "Error", "Unable to retrieve request details.")
            return

        request_id = request_id_item.text()
        current_status = approval_status_item.text()

        # Check if the current status is already denied
        if current_status.lower() == "denied":
            QtWidgets.QMessageBox.warning(self, "Already Denied", "This request is already denied.")
            return

        try:
            cursor = self.connection.cursor()

            # Determine the table for the request based on the selected RequestID
            # Check if the RequestID exists in the Person_Request table
            query_check_person_request = "SELECT COUNT(*) FROM Person_Request WHERE RequestID = ?"
            cursor.execute(query_check_person_request, (request_id,))
            is_person_request = cursor.fetchone()[0] > 0

            if is_person_request:
                # Update approval status for Person_Request
                query_update_person_request = """
                    UPDATE Person_Request
                    SET approval = 0, ApprovalDate = GETDATE()
                    WHERE RequestID = ?
                """
                cursor.execute(query_update_person_request, (request_id,))
            else:
                # Update approval status for FIR_Request
                query_update_fir_request = """
                    UPDATE FIR_Request
                    SET approval = 0, ApprovalDate = GETDATE()
                    WHERE RequestID = ?
                """
                cursor.execute(query_update_fir_request, (request_id,))

            # Commit the changes
            self.connection.commit()

            # Refresh the table to reflect the changes
            self.search_request_logic()

            QtWidgets.QMessageBox.information(self, "Success", "Request denied successfully.")

        except pyodbc.Error as e:
            self.connection.rollback()  # Rollback changes in case of error
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error updating denial status: {e}")





    # --- View Methods ---


    def view_selected_operator(self, search_operator_widget):
        """Get the selected operator from the table and show details in the view screen."""
        table_widget = search_operator_widget.findChild(QtWidgets.QTableWidget, "op_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to view details.")
            return

        # Extract operator details from the selected row
        operator_data = []
        for col in range(table_widget.columnCount()):
            item = table_widget.item(selected_row, col)
            operator_data.append(item.text() if item else "")

        # Navigate to the view operator screen
        self.show_view_operator(operator_data)


    def show_view_operator(self,operator_data):
        view_operator = self.load_ui("screens/view_operator.ui")
        self.set_main_widget(view_operator)

        # Populate the fields with operator details
        try:
            view_operator.findChild(QtWidgets.QLineEdit, "name_display").setText(operator_data[1])
            view_operator.findChild(QtWidgets.QLineEdit, "rank_display").setText(operator_data[2])
            view_operator.findChild(QtWidgets.QLineEdit, "department_display").setText(operator_data[3])
        except IndexError:
            QtWidgets.QMessageBox.warning(self, "Error", "Operator data is incomplete.")
        view_operator.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        view_operator.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)


    # --- Add Methods --

    def add_operator_logic(self):
        add_operator = self.current_window

        # Get inputs from the form
        user_id = add_operator.findChild(QtWidgets.QLineEdit, "username_line").text().strip()
        password = add_operator.findChild(QtWidgets.QLineEdit, "pass_line").text().strip()
        user_name = add_operator.findChild(QtWidgets.QLineEdit, "name_line").text().strip()
        rank = add_operator.findChild(QtWidgets.QComboBox, "rank_line").currentText().strip()
        department = add_operator.findChild(QtWidgets.QComboBox, "dept_line").currentText().strip()
        user_type = add_operator.findChild(QtWidgets.QComboBox, "user_type_display").currentText().strip()

        # Validate inputs
        # if not user_id or not password or not user_name or not rank or not department:
        #     QtWidgets.QMessageBox.warning(self, "Error", "All fields are required!")
        #     return
        if not user_id or not password or not user_name or not user_type:
            QtWidgets.QMessageBox.warning(self, "Error", "ID, Password, user_type and Name fields are required!")
            return
        
        if user_type == "admin":
            user_type = 1
        elif user_type == "operator":
            user_type = 2

        # SQL Query to insert operator
        query = """
        INSERT INTO Users (user_id, user_password, user_name, user_rank, user_department, user_type_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id, password, user_name, rank, department, user_type))  # 2 is user_type_id for operators
            self.connection.commit()
            QtWidgets.QMessageBox.information(self, "Success", "Operator added successfully!")
            self.show_admin_dashboard()  # Redirect to admin dashboard
        except pyodbc.IntegrityError as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Failed to add operator: {e}")


    # --- Update Methods ---

    def show_update_operator(self,search_operator_widget):
        """Get the selected operator from the table and show details in the view screen."""
        table_widget = search_operator_widget.findChild(QtWidgets.QTableWidget, "op_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to view details.")
            return

            # Extract operator details from the selected row
        operator_data = []
        for col in range(table_widget.columnCount()):
            item = table_widget.item(selected_row, col)
            operator_data.append(item.text() if item else "")


        # Fetch the password for the selected user_id
        user_id = operator_data[0]  # Assuming the first column is user_id
        query = "SELECT * FROM Users WHERE user_id = ?"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                operator_data = result
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to fetch password for the selected operator.")
                return
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Failed to fetch password: {e}")
            return

        update_operator = self.load_ui("screens\\update_operator.ui")
        self.set_main_widget(update_operator)
        update_operator.findChild(QtWidgets.QComboBox, "rank_display").addItem("")
        update_operator.findChild(QtWidgets.QComboBox, "dept_display").addItem("")
        update_operator.findChild(QtWidgets.QComboBox, "rank_display").addItem("Senior Detective")
        update_operator.findChild(QtWidgets.QComboBox, "dept_display").addItem("Investigations")
        update_operator.findChild(QtWidgets.QComboBox, "rank_display").addItem("Police Chief")
        update_operator.findChild(QtWidgets.QComboBox, "dept_display").addItem("Administration")
                
        update_operator.findChild(QtWidgets.QPushButton, "update_button").clicked.connect(lambda: self.update_operator_logic(operator_data))
        update_operator.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        update_operator.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)
        


    def update_operator_logic(self, operator_data):
        update_operator = self.current_window

        # Get updated inputs
        name = update_operator.findChild(QtWidgets.QLineEdit, "name_display").text().strip()
        rank = update_operator.findChild(QtWidgets.QComboBox, "rank_display").currentText().strip()
        department = update_operator.findChild(QtWidgets.QComboBox, "dept_display").currentText().strip()
        password = update_operator.findChild(QtWidgets.QLineEdit, "pass_display").text().strip()

        # # Validate inputs
        # if not name or not rank or not department or not password:
        #     QtWidgets.QMessageBox.warning(self, "Error", "All fields are required!")
        #     return
        if not name:
            name = operator_data[2]
        if not password:
            password = operator_data[1]
        if not rank:
            rank = operator_data[3]
        if not department:
            department = operator_data[4]
        # SQL Query to update operator
        query = """
        UPDATE Users
        SET user_name = ?, user_password = ?, user_rank = ?, user_department = ?
        WHERE user_id = ?
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (name, password, rank, department, operator_data[0]))  # operator_data[0] is user_id
            self.connection.commit()
            QtWidgets.QMessageBox.information(self, "Success", "Operator updated successfully!")
            self.show_admin_dashboard()  # Redirect to admin dashboard
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Failed to update operator: {e}")
      

    # --- Delete Methods ---
      

    def delete_operator_record(self, search_operator_widget):
        """Get the selected operator from the table and show details in the view screen."""
        table_widget = search_operator_widget.findChild(QtWidgets.QTableWidget, "op_table")
        selected_row = table_widget.currentRow()

        if selected_row == -1:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select a row to view details.")
            return

        # Extract operator details from the selected row
        operator_data = []
        for col in range(table_widget.columnCount()):
            item = table_widget.item(selected_row, col)
            operator_data.append(item.text() if item else "")

        # Load delete operator confirmation UI
        delete_operator = self.load_ui("screens\\delete_operator.ui")
        self.set_main_widget(delete_operator)

        # Populate the fields with operator details
        try:
            delete_operator.findChild(QtWidgets.QLineEdit, "name_display").setText(operator_data[1])  # Name
            delete_operator.findChild(QtWidgets.QLineEdit, "rank_display").setText(operator_data[2])  # Rank
            delete_operator.findChild(QtWidgets.QLineEdit, "dept_display").setText(operator_data[3])  # Department
            delete_operator.findChild(QtWidgets.QLineEdit, "user_display").setText(operator_data[0])  # User ID

            # Fetch the password for the user from the database
            cursor = self.connection.cursor()
            query = "SELECT user_password FROM Users WHERE user_id = ?"
            cursor.execute(query, (operator_data[0],))
            password_row = cursor.fetchone()
            if password_row:
                delete_operator.findChild(QtWidgets.QLineEdit, "pass_display").setText(password_row[0])
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to fetch operator password.")
        except IndexError:
            QtWidgets.QMessageBox.warning(self, "Error", "Operator data is incomplete.")
            return

        # Connect delete button to SQL-based deletion logic
        delete_operator.findChild(QtWidgets.QPushButton, "delete_button").clicked.connect(
            lambda: self.delete_operator_logic(operator_data)
        )
        delete_operator.findChild(QtWidgets.QPushButton, "home_button").clicked.connect(self.show_admin_dashboard)
        delete_operator.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(self.show_sign_in_screen)

    def delete_operator_logic(self, operator_data):
        """Delete the operator from the Users table in the database."""
        user_id = operator_data[0]  # Extract the User ID to delete

        # SQL query to delete the operator
        query = "DELETE FROM Users WHERE user_id = ?"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id,))
            self.connection.commit()

            QtWidgets.QMessageBox.information(self, "Success", f"Operator {user_id} deleted successfully!")
            self.show_admin_dashboard()  # Redirect to the admin dashboard
        except pyodbc.IntegrityError as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete operator: {e}")
        except pyodbc.Error as e:
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Database error: {e}")



    def delete_record(self, record_type):
        """Delete the selected record from the table."""
        table_widget = self.current_window.findChild(QtWidgets.QTableWidget, "tableWidget")
        if table_widget and table_widget.currentRow() != -1:
            table_widget.removeRow(table_widget.currentRow())
            QtWidgets.QMessageBox.information(self, "Success", f"{record_type} record deleted successfully!")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No record selected for deletion.")

    def delete_fir_and_check_convicted_person(self, fir_no):
        """
        Delete FIR and ensure convicted person records are deleted if no other FIR references them.
        """
        try:
            cursor = self.connection.cursor()

            # Begin transaction
            self.connection.autocommit = False

            # Delete related records in FIR_Person
            query_delete_fir_person = """
            DELETE FROM FIR_Person
            WHERE FIRNo = ?;
            """
            cursor.execute(query_delete_fir_person, (fir_no,))

            # Delete FIR entry
            query_delete_fir = """
            DELETE FROM FIR
            WHERE FIRNo = ?;
            """
            cursor.execute(query_delete_fir, (fir_no,))

            # Delete convicted persons with no FIR references
            query_delete_convicted_person = """
            DELETE FROM Convicted_Person
            WHERE Person_ID NOT IN (SELECT DISTINCT Person_ID FROM FIR_Person);
            """
            cursor.execute(query_delete_convicted_person)

            # Commit transaction
            self.connection.commit()
            self.connection.autocommit = True

            QtWidgets.QMessageBox.information(self, "Success", "FIR and related records deleted successfully!")

        except pyodbc.Error as e:
            self.connection.rollback()  # Rollback transaction in case of error
            QtWidgets.QMessageBox.critical(self, "Database Error", f"Error deleting FIR: {e}")



# Main application loop
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    controller = MainController()
    controller.show()
    sys.exit(app.exec())
