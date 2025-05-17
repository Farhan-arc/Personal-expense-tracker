import pymysql
import datetime

# Connect to database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Admin',
    database='expense_tracker'
)

cursor = connection.cursor()


cursor.execute("""
create table if not exists expenses (
    id int primary key auto_increment,
    amount float not null ,
    category varchar(150) not null,
    description text,
    expense_date date not null
);
""")

cursor.execute("""
create table if not exists budgets (
    id int primary key auto_increment,
    category varchar(50),
    budget_amount decimal(10, 2)
);
""")

# Function to set a budget for a category
def set_budget(category, budget_amount):
    cursor.execute("select id from budgets where category = %s", (category,))
    result = cursor.fetchone()

    if result:
        sql = "update budgets set budget_amount = %s where category = %s"
        cursor.execute(sql, (budget_amount, category))
        print(f"Budget for {category} updated to {budget_amount}")
    else:
        
        sql = "insert into budgets(category, budget_amount) values(%s, %s)"
        cursor.execute(sql, (category, budget_amount))
        print(f"Budget for {category} set to {budget_amount}")
    
    connection.commit()
    
# Function to check if the expense exceeds the budget
def check_budget(category, new_amount):
    cursor.execute("select budget_amount from budgets where category = %s order by id desc limit 1", (category,))
    result = cursor.fetchone()

    if result:
        budget = result[0]
        
        cursor.execute("select COALESCE(sum(amount), 0) from expenses where category = %s", (category,))
        total_spent = cursor.fetchone()[0]
        
        
        total_spent = float(total_spent)  
        new_amount = float(new_amount)    

        total_after_adding = total_spent + new_amount

        if total_after_adding > budget:
            print(f"Warning: You have exceeded your budget of {budget:.2f} for the {category} category!")
        else:
            print(f"Amount is within the budget for {category}. Current total after adding: {total_after_adding:.2f}")
    else:
        print(f"No budget set for {category}, adding expense without a budget check.")
# Function to add expense
def add_expense(amount, category, description, expense_date):
    check_budget(category, amount)
    sql = "insert into expenses (amount, category, description, expense_date) values (%s, %s, %s, %s)"
    values = (amount, category, description, expense_date)
    cursor.execute(sql, values)
    connection.commit()
    print("Expense Added Successfully!")

# Function to view all expenses
def view_expenses():
    cursor.execute("select * from expenses order by expense_date DESC")
    expenses = cursor.fetchall()

    if not expenses:
        print("\n No expenses found.\n")
        return

    
    print("\n--- All Expenses ---")
    print(f"{'ID':<5} {'Amount':<10} {'Category':<15} {'Description':<30} {'Date':<12}")
    print("-" * 80)

   
    for exp in expenses:
        id, amount, category, description, date = exp
        description = description or "N/A"
        print(f"{id:<5} {float(amount):<10.2f} {category:<15} {description:<30} {date:%Y-%m-%d}")

# Function to filter expenses by month
def filter_expenses_by_month(year, month):
    sql = "select * from expenses where year(expense_date) = %s and month(expense_date) = %s order by expense_date DESC"
    cursor.execute(sql, (year, month))
    results = cursor.fetchall()

    if not results:
        print("No expenses found.")
        return

    print(f"\nExpenses in {month}/{year}:")
    for exp in results:
        print(f"ID: {exp[0]}, Amount: {exp[1]}, Category: {exp[2]}, Description: {exp[3] or 'N/A'}, Date: {exp[4]}")
        
# Function to update an expense
def update_expense(expense_id, amount, category, description, expense_date):
    sql = "update expenses set amount=%s, category=%s, description=%s, expense_date=%s where id=%s"
    values = (amount, category, description, expense_date, expense_id)
    cursor.execute(sql, values)
    connection.commit()
    print(" Expense Updated Successfully!")

# Function to delete an expense
def delete_expense(expense_id):
    sql = "delete from expenses where id = %s"
    cursor.execute(sql, (expense_id,))
    connection.commit()
    print("Expense Deleted Successfully!")

# Function to get total spending in a month
def get_total_spending(year, month):
    sql = "select sum(amount) from expenses where year(expense_date) = %s and month(expense_date) = %s"
    cursor.execute(sql, (year, month))
    result = cursor.fetchone()

    if result[0] is None:
        total = 0
    else:
        total = result[0]

    print("Total spending for", month, "/", year, "is:", total)
    
def get_total_spending_by_category(category):
    sql = "select sum(amount) from expenses where category = %s"
    cursor.execute(sql, (category,))
    result = cursor.fetchone()

    if result[0] is None:
        total = 0
    else:
        total = result[0]

    print(f"Total spending for {category} is: {total:.2f}")
    
# Function to get a valid date input from user

def get_valid_date(message):
    while True:
        date_str = input(message)
        try:
            valid_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD format.")
            
# Function to get a valid float input from user

def get_valid_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Invalid number. Please enter a valid amount.")
            
def get_valid_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            
def get_valid_category(message):
    while True:
        category = input(message).strip()
        if category.isalpha():
            return category
        else:
            print("Invalid input. Please enter only alphabetic characters without numbers or symbols.")

def get_valid_description(message):
    while True:
        description = input(message).strip()
        if all(c.isalpha() or c.isspace() for c in description) and description:
            return description
        else:
            print("Invalid input. Please enter only letters and spaces.")            

import matplotlib.pyplot as plt

def plot_expenses_by_category():
    cursor.execute("select category,sum(amount)from expenses group by category")
    data = cursor.fetchall()
    if not data:
        print("No expense data to plot.")
        return
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]
    plt.figure(figsize=(8,5))
    plt.bar(categories, amounts, color='skyblue')
    plt.title('Total Expenses by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Amount')
    plt.tight_layout()
    plt.show()

def plot_monthly_expense_trend():
    cursor.execute("select DATE_FORMAT(expense_date, '%Y-%m') as month,sum(amount)from expenses group by month order by month")
    data = cursor.fetchall()
    if not data:
        print("No expense data to plot.")
        return
    months = [row[0] for row in data]
    totals = [row[1] for row in data]
    plt.figure(figsize=(8,5))
    plt.plot(months, totals, marker='o', color='green')
    plt.title('Monthly Expense Trend')
    plt.xlabel('Month')
    plt.ylabel('Total Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_expense_pie_chart():
    cursor.execute("select category,sum(amount)from expenses group by category")
    data = cursor.fetchall()
    if not data:
        print("No expense data to plot.")
        return
    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]
    plt.figure(figsize=(7,7))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expense Distribution by Category')
    plt.tight_layout()
    plt.show()
    
def menu():
    while True:
        print("\n----- Personal Expense Tracker -----")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Filter Expenses by Month")
        print("4. Update Expense")
        print("5. Delete Expense")
        print("6. Total Spending of a Month")
        print("7. Set Budget for a Category")
        print("8. Total Spending for a Category")
        print("9. View Visualizations")
        print("10. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            amount = get_valid_float("Enter amount: ")
            category = get_valid_category("Enter category (only letters): ")
            description = get_valid_description("Enter description (only letters and spaces): ")
            expense_date = get_valid_date("Enter date (YYYY-MM-DD): ")
            add_expense(amount, category, description, expense_date)
        
        elif choice == '2':
            view_expenses()
        
        elif choice == '3':
            year = get_valid_int("Enter year (YYYY): ")
            month = get_valid_int("Enter month (MM): ")
            filter_expenses_by_month(year, month)
        
        elif choice == '4':
            expense_id = get_valid_int("Enter expense ID to update: ")
            amount = get_valid_float("Enter new amount: ")
            category = get_valid_category("Enter new category (only letters): ")
            description = get_valid_description("Enter new description (only letters and spaces): ")
            expense_date = get_valid_date("Enter new date (YYYY-MM-DD): ")
        
            update_expense(expense_id, amount, category, description, expense_date)
        
        elif choice == '5':
            expense_id = get_valid_int("Enter expense ID to delete: ")
            confirm = input(f"Are you sure you want to delete Expense ID {expense_id}? (yes/no): ").strip().lower()
            if confirm == 'yes':
                delete_expense(expense_id)
                print(f"Expense id {expense_id} deleted successfully!")
            else:
                 print("Deletion cancelled.")
            
           
        elif choice == '6':
            year = get_valid_int("Enter year (YYYY): ")
            month = get_valid_int("Enter month (1-12): ")
            get_total_spending(year, month)
            
        elif choice == '7':
            category = get_valid_category("Enter category (only letters): ")
            budget_amount = get_valid_float("Enter budget amount: ")
            set_budget(category, budget_amount)

        elif choice == '8':  
            category = get_valid_category("Enter category (only letters): ")
            get_total_spending_by_category(category)


        elif choice == '9':
            print("\n--- Visualization Menu ---")
            print("1. Bar Chart: Expenses by Category")
            print("2. Line Chart: Monthly Expense Trend")
            print("3. Pie Chart: Expense Distribution by Category")
            vis_choice = input("Select visualization (1-3): ")
            if vis_choice == '1':
                plot_expenses_by_category()
            elif vis_choice == '2':
                plot_monthly_expense_trend()
            elif vis_choice == '3':
                plot_expense_pie_chart()
            else:
                print("Invalid choice.")
        elif choice == '10':
            print("Exiting... Thank you!")
            break    
        
        else:
            print(" Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()
    cursor.close()
    connection.close()
