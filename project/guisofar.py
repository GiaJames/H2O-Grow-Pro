"""
Gia Jame & Shinny No
Final Project for CPTR 215
Water Intake Tracker

2024-12-08 structure of app
2024-12-09 added lineedit for inputting water amount, added date feature to pick day;
           new logs have time, amount, and units user entered & picked; PROBLEM with clearing lineedit
           (might have to do with DoubleValidator it has?)
           added units for goal; a save log thing, doesn't do persistence yet
2024-12-10 conversion function, added charts (not dynamic), added persistence (TODO: need to be able to only show logs
           for specific days still); also TODO: set correct X and Y axis
           TODO: add functionality to set_goal button (get the value from lineedit, use to calculate % or something)
           QUESTION : how to make a chart for "yearly" TODO: remove specific logs
           TODO: doctests

"""



import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget, QDateEdit
)
from PySide6.QtGui import QFont, QPixmap, QDoubleValidator, QPainter
from PySide6.QtCore import Qt, QDate, QTime, QPointF
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QBarCategoryAxis


class H2OGrowApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window Properties
        self.setWindowTitle("H2O Grow")
        self.setGeometry(100, 100, 1200, 700)

        # Data Management
        self.data_logs = []  # Stores logs as dictionaries
        self.daily_goal = 64  # Default daily goal in ounces

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        central_widget.setStyleSheet("background-color: #e6f2e6;")  # Background color

        # Header Section
        title_label = QLabel("H2O Grow")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2d604b;")  # Dark green
        main_layout.addWidget(title_label)

        # Top Section Layout
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout, stretch=5)

        # Left Section (Date Selector and Log Table)
        left_section = QVBoxLayout()
        top_layout.addLayout(left_section, stretch=3)

        # Date Selector
        date_layout = QHBoxLayout()
        date_label = QLabel("Water Log:")

        self.lineedit = QLineEdit()
        float_validator = QDoubleValidator()
        self.lineedit.setValidator(float_validator)
        self.lineedit.setMaxLength(6)       # input for water amt
        self.lineedit.setPlaceholderText("Enter Amt...")


        date_label.setFont(QFont("Arial", 10))
        date_label.setStyleSheet("color: #2d604b;")
        # self.date_dropdown = QComboBox()
        # self.date_dropdown.addItem("12/5/2024")  # Example date
        # self.date_dropdown.setFont(QFont("Arial", 12))
        # self.date_dropdown.setStyleSheet("background-color: #ffffff; border: 1px solid #2d604b;")

        self.date_pick = QDateEdit()
        self.date_pick.setDate(QDate.currentDate()) 
        self.date_pick.setMaximumDate(QDate.currentDate())
        self.date_pick.setCalendarPopup(True)

        self.pick_units = QComboBox()
        self.pick_units.addItems(["Fl Oz", "Cups", "Pints", "Quarts", "Gallon", "Liter"])
        
        date_layout.addWidget(date_label)
        
        # date_layout.addWidget(self.date_dropdown)
        date_layout.addWidget(self.date_pick)
        date_layout.addWidget(self.lineedit)
        date_layout.addWidget(self.pick_units)
        left_section.addLayout(date_layout)

        # Add and Remove Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.add_button.setFont(QFont("Arial", 16))
        self.add_button.setStyleSheet("background-color: #91cba9; color: #ffffff; border-radius: 5px;")
        self.add_button.clicked.connect(self.add_log_entry)
        self.remove_button = QPushButton("-")
        self.remove_button.setFont(QFont("Arial", 16))
        self.remove_button.setStyleSheet("background-color: #91cba9; color: #ffffff; border-radius: 5px;")
        self.remove_button.clicked.connect(self.remove_log_entry)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_section.addLayout(button_layout)

        # Log Table
        self.log_table = QTableWidget(0, 3)  # 5 rows, 3 columns
        self.log_table.setHorizontalHeaderLabels(["Time", "Amount", "Unit"])
        self.log_table.setStyleSheet("background-color: #ffffff; border: 1px solid #91cba9;")
        left_section.addWidget(self.log_table)

        # Middle Section (Chart Area)
        middle_section = QVBoxLayout()
        
        top_layout.addLayout(middle_section, stretch=5)

        
        self.daily_data_points = QLineSeries()
        # axisX = QChart.QCategoryAxis()
        # axisX.append("Low", 10)
        # axisX.append("Medium", 20)
        # axisX.append("High", 30)

        self.daily_graph = QChart()
        self.daily_graph.legend().hide()
        self.daily_graph.addSeries(self.daily_data_points)
        self.daily_graph.createDefaultAxes()
        self.daily_graph.setTitle("Daily Water Intake")

        self.daily_chart_view = QChartView(self.daily_graph)
        self.daily_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Tabs above the chart
        chart_tabs = QTabWidget()
        chart_tabs.addTab(self.daily_chart_view, "Daily")


        # self.weekly_data_points = QLineSeries()
        # self.weekly_data_points.append(QPointF(7, 14))
        # self.weekly_data_points.append(QPointF(8, 10))
        # self.weekly_data_points.append(QPointF(9, 7))
        # self.weekly_data_points.append(QPointF(10, 9))
        # self.weekly_data_points.append(QPointF(11, 18))

        self.weekly_graph = QChart()

        weeks = "Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split()
        axisX = QBarCategoryAxis()
        axisX.append(weeks)

        # self.weekly_graph.addAxis(axisX, AlignmentFlag)
        # TODO: what params??

        self.weekly_graph.legend().hide()
        # self.weekly_graph.addSeries(self.weekly_data_points)
        self.weekly_graph.createDefaultAxes()
        self.weekly_graph.setTitle("Weekly Water Intake")

        self.weekly_chart_view = QChartView(self.weekly_graph)
        self.weekly_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)


        chart_tabs.addTab(self.weekly_chart_view, "Weekly")

        self.monthly_data_points = QLineSeries()
        self.monthly_data_points.append(QPointF(3, 12))
        self.monthly_data_points.append(QPointF(6, 15))
        self.monthly_data_points.append(QPointF(7, 17))
        self.monthly_data_points.append(QPointF(11, 15))
        self.monthly_data_points.append(QPointF(12, 12))

        self.monthly_graph = QChart()

        

        self.monthly_graph.legend().hide()
        self.monthly_graph.addSeries(self.monthly_data_points)
        self.monthly_graph.createDefaultAxes()
        self.monthly_graph.setTitle("Monthly Water Intake")

        self.monthly_chart_view = QChartView(self.monthly_graph)
        self.monthly_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        chart_tabs.addTab(self.monthly_chart_view, "Monthly")
        chart_tabs.addTab(QWidget(), "Yearly")
        chart_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #91cba9; }
            QTabBar::tab { background: #d8e8d8; padding: 8px; border: 1px solid #91cba9; }
            QTabBar::tab:selected { background: #91cba9; color: #ffffff; }
        """)
        middle_section.addWidget(chart_tabs)





        # Placeholder for Chart
        self.daily_graph_placeholder = QLabel("Water Tracker Chart")
        self.daily_graph_placeholder.setFont(QFont("Arial", 16))
        self.daily_graph_placeholder.setAlignment(Qt.AlignCenter)
        self.daily_graph_placeholder.setStyleSheet("background-color: #ffffff; border: 1px solid #91cba9; padding: 10px;")
        middle_section.addWidget(self.daily_graph_placeholder)

        # Right Section (Plant and Goals)
        right_section = QVBoxLayout()
        top_layout.addLayout(right_section, stretch=2)

        # Daily Water Goal
        goal_layout = QVBoxLayout()
        daily_goal_label = QLabel("Daily Water Goal:")
        daily_goal_label.setFont(QFont("Arial", 14))
        daily_goal_label.setStyleSheet("color: #2d604b;")
        goal_layout.addWidget(daily_goal_label)

        goal_and_units = QHBoxLayout()

        self.daily_goal_input = QLineEdit()
        self.daily_goal_input.setFixedWidth(100)
        self.daily_goal_input.setPlaceholderText("Enter goal...")
        self.daily_goal_input.setValidator(float_validator)     # from when we used it for logging
        self.daily_goal_input.setStyleSheet("background-color: #ffffff; border: 1px solid #91cba9;")
        self.daily_goal_input.returnPressed.connect(self.update_daily_goal)
        goal_and_units.addWidget(self.daily_goal_input)

        self.confirm_set_goal = QPushButton("✓")
        self.confirm_set_goal.setFixedWidth(25)
        goal_and_units.addWidget(self.confirm_set_goal)

        self.units_for_goal = QComboBox()
        self.units_for_goal.addItems(["Fl Oz", "Cups", "Pints", "Quarts", "Gallon", "Liter"])
        goal_and_units.addWidget(self.units_for_goal)

        goal_layout.addLayout(goal_and_units)

        right_section.addLayout(goal_layout)

        # Plant Image Section
        plant_image_path = r"cute-cartoon-home-plant-in-clay-pot-illustration-vector.jpg"
        self.plant_image_placeholder = QLabel()
        self.plant_image_placeholder.setPixmap(
            QPixmap(plant_image_path).scaled(200, 200, Qt.KeepAspectRatio)
        )
        self.plant_image_placeholder.setAlignment(Qt.AlignCenter)
        self.plant_image_placeholder.setStyleSheet("background-color: #ffffff; border: 1px solid #91cba9; padding: 10px;")
        right_section.addWidget(self.plant_image_placeholder, stretch=2)

        # Pie Charts
        self.pie_chart_1 = QLabel("Pie Chart 1\n(% Water Logged)")
        self.pie_chart_2 = QLabel("Pie Chart 2\n(Plant Success)")
        for pie_chart in [self.pie_chart_1, self.pie_chart_2]:
            pie_chart.setAlignment(Qt.AlignCenter)
            pie_chart.setStyleSheet("background-color: #ffffff; border: 1px solid #91cba9; padding: 10px;")
            right_section.addWidget(pie_chart)

        # setting focus on water input line for calender doesn't get highlighted
        self.lineedit.setFocus()
        self.load_logs()
    

    # QUESTION: lineedit.clear doesn't clear when there is a float (eg. 3.0); only clears when input is .
    def add_log_entry(self):
        water_amt = self.lineedit.text()
        units = self.pick_units.currentText()
        current_date = self.date_pick.date().toString("yyyy-MM-dd") 
        current_time = QTime.currentTime()

        if water_amt and water_amt != ".":
            new_log = {
                "date": current_date,  # Add the selected date to the log
                "time": current_time.toString("hh:mm:ss AP"),
                "amount": water_amt,
                "unit": units
            }
            self.data_logs.append(new_log)
            self.update_log_table()
            self.save_logs()
        self.lineedit.clear()


    def remove_log_entry(self):
        if self.data_logs:
            self.data_logs.pop()  # Remove the last log for now
            self.update_log_table()

    def update_log_table(self):
        self.log_table.setRowCount(len(self.data_logs))
        for row, log in enumerate(self.data_logs):
            self.log_table.setItem(row, 0, QTableWidgetItem(log["time"]))
            self.log_table.setItem(row, 1, QTableWidgetItem(str(log["amount"])))
            self.log_table.setItem(row, 2, QTableWidgetItem(log["unit"]))
        self.update_pie_chart()

    def update_daily_goal(self):
        goal = int(self.daily_goal_input.text())
        if goal > 0:
            self.daily_goal = goal

    def update_pie_chart(self):
        pass
        # total_intake = sum(log["amount"] for log in self.data_logs)
        # progress = min((total_intake / self.daily_goal) * 100, 100)
        # self.pie_chart_1.setText(f"{progress:.1f}% Logged")

    def save_logs(self):
        """ saves logs in txt file for persistence """
        logs_by_date = {}
        for log in self.data_logs:
            date = log["date"]  
            if date not in logs_by_date:
                logs_by_date[date] = []
            logs_by_date[date].append({
                "time": log["time"],
                "amount": log["amount"],
                "unit": log["unit"]
            })

        with open('logs.txt', 'w') as file:
            for date, entries in logs_by_date.items():
                file.write(f"{date}:\n")
                for entry in entries:
                    file.write(f"  {entry}\n")
    def load_logs(self):
        """ loads prev inputted logs """
        if os.path.exists('logs.txt'):
            with open('logs.txt', 'r') as file:
                lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.endswith(":"):
                    current_date = line[:-1]        # removing the : from (ex: 2024-12-10":"")
                elif current_date and line.startswith("{") and line.endswith("}"):  # the {...} inside a time thing
                    entry = eval(line)      # turns the string dict to actaul python dict!!
                    log_entry = {
                        "date": current_date,
                        "time": entry["time"],
                        "amount": entry["amount"],
                        "unit": entry["unit"]
                    }
                    self.data_logs.append(log_entry)
            self.update_log_table()





def convert_to_oz(x: float, scale: str) -> str:
    """ "Fl Oz", "Cups", "Pints", "Quarts", "Gallon", "Liter"
    >>> convert_to_oz(5.00, "Fl Oz")
    '5.0'
    >>> convert_to_oz(12.12, "Cups")
    '97.0'
    >>> convert_to_oz(1, "Quarts")
    '32.0'
    """
    if scale == "Fl Oz":
        oz = x
    elif scale == "Cups":
        oz = x * 8
    elif scale == "Pints":
        oz = x * 16
    elif scale == "Quarts":
        oz = x * 32
    elif scale == "Gallon":
        oz = x * 128
    elif scale == "Liter":
        oz = x * 33.814
    formatted_oz = format(oz, ".1f")
    return formatted_oz


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    app = QApplication(sys.argv)

    window = H2OGrowApp()
    window.show()

    sys.exit(app.exec())