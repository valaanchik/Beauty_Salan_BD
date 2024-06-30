import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from tkcalendar import DateEntry
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='111111111',
            database='mydate_beauty'
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка подключения к базе данных", f"Error: {err}")
        return None


class SalonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Salon Manager App")
        self.geometry("950x560")
        self.create_widgets()

    def create_widgets(self):
        # Left menu
        menu_frame = tk.Frame(self, bg="#D4CDC3")
        menu_frame.pack(side="left", fill="y")

        menu_buttons = [("Главная", MainFrame), ("Клиенты", ClientsFrame), ("Услуги", ServicesFrame),
                        ("Расходники", SuppliesFrame), ("Работники", EmployeesFrame), ("Отчет", ReportFrame)]
        for button_text, frame_class in menu_buttons:
            button = tk.Button(menu_frame, text=button_text, width=20, pady=10,
                               command=lambda fc=frame_class: self.switch_frame(fc))
            button.pack(pady=5)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.frames = {}
        for button_text, frame_class in menu_buttons:
            frame = frame_class(parent=self.main_frame, controller=self)
            self.frames[frame_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.switch_frame(MainFrame)

    def switch_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Главная", font=("Arial", 22))
        label.pack(pady=50, padx=50)
        label = tk.Label(self, text="Помощник для Салона красоты", font=("Arial", 18))
        label.pack(pady=20, padx=20)

        self.salon_count_label = tk.Label(self, text="Сейчас в управлении: ", font=("Arial", 19))
        self.salon_count_label.pack(pady=15)
        self.client_count_label = tk.Label(self, text="Количество клиентов: ", font=("Arial", 19))
        self.client_count_label.pack(pady=15)
        self.master_count_label = tk.Label(self, text="Количество мастеров: ", font=("Arial", 19))
        self.master_count_label.pack(pady=15)
        self.manager_count_label = tk.Label(self, text="Количество менеджеров: ", font=("Arial", 19))
        self.manager_count_label.pack(pady=15)

    def update_counts(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM firm_avv")
            salon_count = cursor.fetchone()[0]
            self.salon_count_label.config(text=f"Сейчас в управлении: {salon_count} салона красоты")

            cursor.execute("SELECT COUNT(*) FROM client_avv")
            client_count = cursor.fetchone()[0]
            self.client_count_label.config(text=f"Количество клиентов: {client_count}")

            cursor.execute("SELECT COUNT(*) FROM master_avv")
            master_count = cursor.fetchone()[0]
            self.master_count_label.config(text=f"Количество мастеров: {master_count}")

            cursor.execute("SELECT COUNT(*) FROM maneger_avv")
            manager_count = cursor.fetchone()[0]
            self.manager_count_label.config(text=f"Количество менеджеров: {manager_count}")

            cursor.close()
            conn.close()

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        self.update_counts()


class ClientsFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Клиенты", font=("Arial", 18))
        label.pack(pady=10, padx=10)

        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Имя:").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        tk.Label(self, text="Телефон:").pack()
        self.phone_entry = tk.Entry(self)
        self.phone_entry.pack()

        tk.Label(self, text="Салон красоты:").pack()
        self.salon_combobox = ttk.Combobox(self)
        self.salon_combobox.pack()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_client).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.update_client).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_client).pack(side="left", padx=5)

        self.clients_table = ttk.Treeview(self, columns=("id", "name", "phone", "salon"), show='headings')
        self.clients_table.heading("id", text="ID")
        self.clients_table.heading("name", text="Имя")
        self.clients_table.heading("phone", text="Телефон")
        self.clients_table.heading("salon", text="Салон красоты")
        self.clients_table.column("id", width=0, stretch=tk.NO)
        self.clients_table.column("name", width=150)
        self.clients_table.column("phone", width=150)
        self.clients_table.column("salon", width=150)
        self.clients_table.pack(fill="both", expand=True)

        self.clients_table.bind('<<TreeviewSelect>>', self.fill_entry_fields)
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Фильтр по салону:").pack(side="left")
        self.filter_salon_combobox = ttk.Combobox(filter_frame)
        self.filter_salon_combobox.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).pack(side="left", padx=5)

        self.load_clients()
        self.load_salon_data()


    def fill_entry_fields(self, event):
        selected_item = self.clients_table.selection()
        if selected_item:
            data = self.clients_table.item(selected_item, 'values')
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, data[1])
            self.phone_entry.delete(0, 'end')
            self.phone_entry.insert(0, data[2])
            self.salon_combobox.set(data[3])

    def load_salon_data(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name_firm FROM firm_avv")
            salons = [row[0] for row in cursor.fetchall()]
            self.salon_combobox['values'] = salons
            self.filter_salon_combobox['values'] = salons
            cursor.close()
            conn.close()
    def load_clients(self, salon_filter=None):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            if salon_filter:
                cursor.execute("SELECT c.id_client, c.name, c.phone_num, f.name_firm FROM client_avv c "
                               "JOIN firm_avv_has_client_avv fc ON c.id_client = fc.Client_AVV_id_client "
                               "JOIN firm_avv f ON fc.firm_AVV_id_firm = f.id_firm "
                               "WHERE f.name_firm = %s", (salon_filter,))
            else:
                cursor.execute("SELECT c.id_client, c.name, c.phone_num, f.name_firm FROM client_avv c "
                               "JOIN firm_avv_has_client_avv fc ON c.id_client = fc.Client_AVV_id_client "
                               "JOIN firm_avv f ON fc.firm_AVV_id_firm = f.id_firm")
            rows = cursor.fetchall()
            self.clients_table.delete(*self.clients_table.get_children())
            for row in rows:
                self.clients_table.insert('', tk.END, values=row)
            cursor.close()
            conn.close()

    def add_client(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        salon = self.salon_combobox.get()
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO client_avv (name, phone_num) VALUES (%s, %s)", (name, phone))
            client_id = cursor.lastrowid

            cursor.execute("SELECT id_firm FROM firm_avv WHERE name_firm = %s", (salon,))
            firm_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO firm_avv_has_client_avv (firm_AVV_id_firm, Client_AVV_id_client) VALUES (%s, %s)",
                (firm_id, client_id))
            conn.commit()

            cursor.close()
            conn.close()

        self.load_clients()

    def update_client(self):
        selected_item = self.clients_table.selection()
        if not selected_item:
            return
        client_id = self.clients_table.item(selected_item, 'values')[0]
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        salon = self.salon_combobox.get()

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE client_avv SET name = %s, phone_num = %s WHERE id_client = %s",
                           (name, phone, client_id))

            cursor.execute("SELECT id_firm FROM firm_avv WHERE name_firm = %s", (salon,))
            firm_id = cursor.fetchone()[0]

            cursor.execute("UPDATE firm_avv_has_client_avv SET firm_AVV_id_firm = %s WHERE Client_AVV_id_client = %s",
                           (firm_id, client_id))

            conn.commit()
            cursor.close()
            conn.close()

        self.load_clients()


    def delete_client(self):
        selected_item = self.clients_table.selection()
        if not selected_item:
            return

        client_id = self.clients_table.item(selected_item, "values")[0]  # Получаем ID клиента

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()

            try:
                cursor.execute("DELETE FROM firm_avv_has_client_avv WHERE Client_AVV_id_client = %s", (client_id,))
                cursor.execute("DELETE FROM client_avv WHERE id_client = %s", (client_id,))

                conn.commit()
                cursor.close()
                conn.close()
            except mysql.connector.Error as e:
                messagebox.showerror("Ошибка удаления клиента", f"Произошла ошибка при удалении клиента: {e}")
            except TypeError:
                messagebox.showerror("Ошибка удаления клиента", "Клиент с указанным ID не найден.")

        self.load_clients()

    def apply_filter(self):
        selected_salon = self.filter_salon_combobox.get()
        if selected_salon:
            self.load_clients(salon_filter=selected_salon)
        else:
            self.load_clients()

class ServicesFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Услуги", font=("Arial", 18))
        label.pack(pady=10, padx=10)

        self.controller = controller
        self.create_widgets()

    def create_widgets(self):

        tk.Label(self, text="Название:").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        tk.Label(self, text="Цена:").pack()
        self.price_entry = tk.Entry(self)
        self.price_entry.pack()

        tk.Label(self, text="Салон красоты:").pack()
        self.salon_combobox = ttk.Combobox(self)
        self.salon_combobox.pack()

        tk.Label(self, text="Мастер").pack()
        self.master_combobox = ttk.Combobox(self)
        self.master_combobox.pack()


        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_service).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_service).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Обновить", command=self.update_service).grid(row=0, column=3, padx=5)

        self.services_table = ttk.Treeview(self, columns=("name", "price","name_master" ), show='headings')
        self.services_table.heading("name", text="Название услуги")
        self.services_table.heading("price", text="Цена")
        self.services_table.heading("name_master", text="Имя мастера")
        self.services_table.pack(fill="both", expand=True)

        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Фильтр по цене:").grid(row=0, column=0, padx=5)
        self.filter_price_entry = tk.Entry(filter_frame)
        self.filter_price_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=2, padx=5)

        self.load_services()

        tk.Label(filter_frame, text="Фильтр по салону:").grid(row=1, column=0, padx=5)
        self.filter_salon_combobox = ttk.Combobox(filter_frame)
        self.filter_salon_combobox.grid(row=1, column=1, padx=5)


        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_salon_filter).grid(row=1, column=2, padx=5)
        self.load_services()
        self.load_salon_data()



    def apply_salon_filter(self):
        selected_salon = self.filter_salon_combobox.get()
        self.load_services(selected_salon)

    def load_services(self, salon=None):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            if salon:
                cursor.execute("SELECT s.name_servs, s.price_serv, m.name "
                               "FROM servies_avv s "
                               "LEFT JOIN servies_avv_has_master_avv sm ON s.id_servies = sm.servies_AVV_id_servies "
                               "LEFT JOIN master_avv m ON sm.mastet_AVV_id_master = m.id_master "
                               "LEFT JOIN firm_avv_has_master_avv fmm ON m.id_master = fmm.mastet_AVV_id_master "
                               "LEFT JOIN firm_avv f ON fmm.firm_AVV_id_firm = f.id_firm "
                               "WHERE f.name_firm = %s", (salon,))
            else:
                cursor.execute("SELECT s.name_servs, s.price_serv, m.name "
                               "FROM servies_avv s "
                               "LEFT JOIN servies_avv_has_master_avv sm ON s.id_servies = sm.servies_AVV_id_servies "
                               "LEFT JOIN master_avv m ON sm.mastet_AVV_id_master = m.id_master")
            rows = cursor.fetchall()
            self.services_table.delete(*self.services_table.get_children())
            for row in rows:
                self.services_table.insert('', tk.END, values=row)
            cursor.close()
            conn.close()

    def load_salon_data(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name_firm FROM firm_avv")
            salons = [row[0] for row in cursor.fetchall()]
            self.salon_combobox['values'] = salons
            self.filter_salon_combobox['values'] = salons
            cursor.close()
            conn.close()

            # Load master data when a salon is selected
            self.salon_combobox.bind("<<ComboboxSelected>>", self.load_master_data)

    def load_master_data(self, event=None):
        selected_salon = self.salon_combobox.get()
        if selected_salon:
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT m.name "
                               "FROM master_avv m "
                               "INNER JOIN firm_avv_has_master_avv fmm ON m.id_master = fmm.mastet_AVV_id_master "
                               "INNER JOIN firm_avv f ON fmm.firm_AVV_id_firm = f.id_firm "
                               "WHERE f.name_firm = %s", (selected_salon,))
                masters = [row[0] for row in cursor.fetchall()]
                self.master_combobox['values'] = masters
                cursor.close()
                conn.close()
        else:
            # If no salon is selected, clear the master combobox
            self.master_combobox['values'] = []
    def add_service(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        salon = self.salon_combobox.get()
        master = self.master_combobox.get()

        if name and price and salon and master:
            try:
                price = int(price)
                conn = connect_to_db()
                if conn:
                    cursor = conn.cursor()
                    # Insert service
                    cursor.execute("INSERT INTO servies_avv (name_servs, price_serv) VALUES (%s, %s)", (name, price))
                    service_id = cursor.lastrowid

                    # Get salon id
                    cursor.execute("SELECT id_firm FROM firm_avv WHERE name_firm = %s", (salon,))
                    salon_id = cursor.fetchone()[0]

                    # Get master id
                    cursor.execute("SELECT id_master FROM master_avv WHERE name = %s", (master,))
                    master_id = cursor.fetchone()[0]

                    # Insert service-master relation
                    cursor.execute(
                        "INSERT INTO servies_avv_has_master_avv (servies_AVV_id_servies, mastet_AVV_id_master) VALUES (%s, %s)",
                        (service_id, master_id))

                    conn.commit()
                    cursor.close()
                    conn.close()
                    self.load_services()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите целочисленное значение для цены.")

    def delete_service(self):
        selected_item = self.services_table.selection()
        if not selected_item:
            return
        name = self.services_table.item(selected_item, 'values')[0]
        conn = connect_to_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM servies_avv WHERE name_servs = %s", (name,))
                    conn.commit()
            finally:
                conn.close()
            self.load_services()

    def update_service(self):
        selected_item = self.services_table.selection()
        if not selected_item:
            return
        current_name = self.services_table.item(selected_item, 'values')[0]  # Get the current name from the table
        new_name = self.name_entry.get()  # Get the new name from the entry widget
        price = self.price_entry.get()
        if price and new_name:
            try:
                price = int(price)
                conn = connect_to_db()
                if conn:
                    try:
                        with conn.cursor() as cursor:
                            # Update the service with the new name and price
                            cursor.execute(
                                "UPDATE servies_avv SET name_servs = %s, price_serv = %s WHERE name_servs = %s",
                                (new_name, price, current_name))
                            conn.commit()
                    finally:
                        conn.close()
                    self.load_services()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите целочисленное значение для цены.")

    def apply_filter(self):
        filter_price = self.filter_price_entry.get()
        if filter_price:
            try:
                filter_price = int(filter_price)
                conn = connect_to_db()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name_servs, price_serv FROM servies_avv WHERE price_serv <= %s",
                                   (filter_price,))
                    rows = cursor.fetchall()
                    self.services_table.delete(*self.services_table.get_children())
                    for row in rows:
                        self.services_table.insert('', tk.END, values=row)
                    cursor.close()
                    conn.close()
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите целочисленное значение для фильтрации цены.")


class SuppliesFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Расходники", font=("Arial", 18))
        label.pack(pady=10, padx=10)

        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=10)
        tk.Label(entry_frame, text="Название расходника:").grid(row=0, column=0, padx=5)
        self.supply_name_entry = tk.Entry(entry_frame)
        self.supply_name_entry.grid(row=0, column=1, padx=5)

        tk.Label(entry_frame, text="Количество:").grid(row=0, column=2, padx=5)
        self.supply_count_entry = tk.Entry(entry_frame)
        self.supply_count_entry.grid(row=0, column=3, padx=5)

        tk.Label(entry_frame, text="Номер поставки:").grid(row=1, column=0, padx=5)
        self.supply_delivery_entry = tk.Entry(entry_frame)
        self.supply_delivery_entry.grid(row=1, column=1, padx=5)

        tk.Label(entry_frame, text="Срок годности:").grid(row=1, column=2, padx=5)
        self.supply_expiration_entry = DateEntry(entry_frame, date_pattern="dd.mm.yyyy")
        self.supply_expiration_entry.grid(row=1, column=3, padx=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.update_supply).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_supply).pack(side="left", padx=5)

        self.supply_table = ttk.Treeview(self, columns=("name", "count", "delivery", "expiration"), show='headings')
        self.supply_table.heading("name", text="Название")
        self.supply_table.heading("count", text="Количество")
        self.supply_table.heading("delivery", text="Номер поставвки")
        self.supply_table.heading("expiration", text="Срок годности")
        self.supply_table.pack(fill="both", expand=True)

        self.load_supplies()
        self.supply_table.bind('<ButtonRelease-1>', self.fill_entry_fields)

    def fill_entry_fields(self, event):
        selected_item = self.supply_table.selection()
        if selected_item:
            data = self.supply_table.item(selected_item, 'values')
            self.supply_name_entry.delete(0, 'end')
            self.supply_name_entry.insert(0, data[0])
            self.supply_count_entry.delete(0, 'end')
            self.supply_count_entry.insert(0, data[1])
            self.supply_delivery_entry.delete(0, 'end')
            self.supply_delivery_entry.insert(0, data[2])
            self.supply_expiration_entry.delete(0, 'end')
            self.supply_expiration_entry.insert(0, data[3])

    def load_supplies(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name_sup, count, delivery, expiration_date FROM supplies_avv")
            rows = cursor.fetchall()
            self.supply_table.delete(*self.supply_table.get_children())
            for row in rows:
                self.supply_table.insert("", "end", values=row)
            cursor.close()
            conn.close()

    def add_supply(self):
        name = self.supply_name_entry.get()
        count = self.supply_count_entry.get()
        delivery = self.supply_delivery_entry.get()
        expiration = self.supply_expiration_entry.get_date().strftime("%Y-%m-%d")

        if not all([name, count, delivery, expiration]):
            messagebox.showerror("Ошибка", "Заполните все поля для добавления расходника")
            return

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                query = "INSERT INTO supplies_avv (name_sup, count, delivery, expiration_date) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (name, count, delivery, expiration))
                conn.commit()
            except mysql.connector.Error as err:
                print("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()
            self.load_supplies()

    def delete_supply(self):
        selected_item = self.supply_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите расходник для удаления")
            return

        name = self.supply_table.item(selected_item, 'values')[0]

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM supplies_avv WHERE name_sup = %s"
                cursor.execute(query, (name,))
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()
            self.load_supplies()

    def update_supply(self):
        selected_item = self.supply_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите расходник для обновления")
            return

        name = self.supply_name_entry.get()
        count = self.supply_count_entry.get()
        delivery = self.supply_delivery_entry.get()
        expiration = self.supply_expiration_entry.get_date().strftime("%Y-%m-%d")

        if not all([name, count, delivery, expiration]):
            messagebox.showerror("Ошибка", "Заполните все поля для обновления расходника")
            return

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                query = "UPDATE supplies_avv SET count = %s, delivery = %s, expiration_date = %s WHERE name_sup = %s"
                cursor.execute(query, (count, delivery, expiration, name))
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()
            self.load_supplies()

class EmployeesFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Работники", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Направление").pack()
        self.direction_combobox = ttk.Combobox(self, values=["Менеджер", "Мастер"])
        self.direction_combobox.pack()
        self.direction_combobox.bind("<<ComboboxSelected>>", self.on_direction_change)

        # Salon combobox
        tk.Label(self, text="Салон красоты:").pack()
        self.salon_combobox = ttk.Combobox(self)
        self.salon_combobox.pack()

        # Name entry
        tk.Label(self, text="Имя:").pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        # Placeholder frame for salary or specialization
        self.dynamic_frame = tk.Frame(self)
        self.dynamic_frame.pack()

        # Phone entry
        tk.Label(self, text="Телефон:").pack()
        self.phone_entry = tk.Entry(self)
        self.phone_entry.pack()

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Добавить", command=self.add_employee).pack(side="left", padx=5)
        tk.Button(button_frame, text="Обновить", command=self.update_employee).pack(side="left", padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_employee).pack(side="left", padx=5)



        self.employee_table = ttk.Treeview(self, columns=("name", "phone", "salon", "additional"), show='headings')
        self.employee_table.heading("name", text="Имя")
        self.employee_table.heading("phone", text="Телефон")
        self.employee_table.heading("salon", text="Салон красоты")
        self.employee_table.heading("additional", text="Зарплата / Специализация")
        self.employee_table.pack(fill="both", expand=True)

        self.load_salon_data()
        self.employee_table.bind('<ButtonRelease-1>', self.fill_entry_fields)

    def fill_entry_fields(self, event):
        selected_item = self.employee_table.selection()
        if selected_item:
            data = self.employee_table.item(selected_item, 'values')
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, data[0])
            self.phone_entry.delete(0, 'end')
            self.phone_entry.insert(0, data[1])
            self.salon_combobox.set(data[2])

            direction = self.direction_combobox.get()
            if direction == "Менеджер":
                self.salary_entry.delete(0, 'end')
                self.salary_entry.insert(0, data[3])
            elif direction == "Мастер":
                self.specialization_entry.delete(0, 'end')
                self.specialization_entry.insert(0, data[3])
    def load_salon_data(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name_firm FROM firm_avv")
            salons = [row[0] for row in cursor.fetchall()]
            self.salon_combobox['values'] = salons
            cursor.close()
            conn.close()

    def on_direction_change(self, event):
        direction = self.direction_combobox.get()

        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        if direction == "Менеджер":
            tk.Label(self.dynamic_frame, text="Зарплата:").pack()
            self.salary_entry = tk.Entry(self.dynamic_frame)
            self.salary_entry.pack()
        elif direction == "Мастер":
            tk.Label(self.dynamic_frame, text="Специализация:").pack()
            self.specialization_entry = tk.Entry(self.dynamic_frame)
            self.specialization_entry.pack()

        self.load_employee()

    def load_employee(self):
        direction = self.direction_combobox.get()
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                if direction == "Менеджер":
                    cursor.execute("""
                            SELECT m.name, m.phone, f.name_firm, m.price
                            FROM maneger_avv m
                            JOIN firm_avv f ON m.firm_AVV_id_firm = f.id_firm
                        """)
                elif direction == "Мастер":
                    cursor.execute("""
                            SELECT ma.name, ma.phone, f.name_firm, ma.spec
                            FROM master_avv ma
                            JOIN firm_avv_has_master_avv fma ON ma.id_master = fma.mastet_AVV_id_master
                            JOIN firm_avv f ON fma.firm_AVV_id_firm = f.id_firm
                        """)

                rows = cursor.fetchall()
                self.employee_table.delete(*self.employee_table.get_children())
                for row in rows:
                    values = row[:3] + (row[3],)
                    self.employee_table.insert("", "end", values=values)
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()

    def add_employee(self):
        direction = self.direction_combobox.get()
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        salon = self.salon_combobox.get()

        if direction == "Менеджер":
            salary = self.salary_entry.get()
            if not all([name, phone, salon, salary]):
                messagebox.showerror("Ошибка", "Заполните все поля для менеджера")
                return
            data = (name, phone, salary, salon)
            query = """
                    INSERT INTO maneger_avv (name, phone, price, firm_AVV_id_firm) 
                    VALUES (%s, %s, %s, (SELECT id_firm FROM firm_avv WHERE name_firm = %s))
                """
        elif direction == "Мастер":
            specialization = self.specialization_entry.get()
            if not all([name, phone, salon, specialization]):
                messagebox.showerror("Ошибка", "Заполните все поля для мастера")
                return
            data = (name, phone, specialization)
            query = """
                    INSERT INTO master_avv (name, phone, spec) 
                    VALUES (%s, %s, %s)
                """
            firm_query = """
                    INSERT INTO firm_avv_has_master_avv (firm_AVV_id_firm, mastet_AVV_id_master) 
                    VALUES ((SELECT id_firm FROM firm_avv WHERE name_firm = %s), 
                            (SELECT id_master FROM master_avv WHERE name = %s AND phone = %s))
                """
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, data)
                if direction == "Мастер":
                    cursor.execute(firm_query, (salon, name, phone))
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()
            self.load_employee()

    def update_employee(self):
        selected_item = self.employee_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите работника для обновления")
            return

        direction = self.direction_combobox.get()
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        salon = self.salon_combobox.get()

        if direction == "Менеджер":
            salary = self.salary_entry.get()
            if not all([name, phone, salon, salary]):
                messagebox.showerror("Ошибка", "Заполните все поля для менеджера")
                return
            data = (name, phone, salary, salon, self.employee_table.item(selected_item, 'values')[0])
            query = """
                         UPDATE maneger_avv
SET name = %s, phone = %s, price = %s, firm_AVV_id_firm = (SELECT id_firm FROM firm_avv WHERE name_firm = %s)
WHERE name = %s
                     """
        elif direction == "Мастер":
            selected_item = self.employee_table.selection()
            if not selected_item:
                return
            master_id = self.employee_table.item(selected_item, 'values')[0]
            name = self.name_entry.get()
            phone = self.phone_entry.get()
            specialization = self.specialization_entry.get()
            if not all([name, phone, specialization]):
                messagebox.showerror("Ошибка", "Заполните все поля для мастера")
                return
            if master_id is None:
                messagebox.showerror("Ошибка", "Выберите существующего мастера")
                return
            data = (name, phone, specialization, master_id, salon)
            query = """
                         UPDATE master_avv
                         SET name = %s, phone = %s, spec = %s
                         WHERE name = %s AND id_master IN 
                         (SELECT mastet_AVV_id_master FROM firm_avv_has_master_avv 
                         WHERE firm_AVV_id_firm = (SELECT id_firm FROM firm_avv WHERE name_firm = %s))
                     """

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                print("Executing query:", query)
                print("Data:", data)
                cursor.execute(query, data)
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
                print("Database Error:", err)
            finally:
                cursor.close()
                conn.close()
            self.load_employee()

    def delete_employee(self):
        selected_item = self.employee_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите работника для удаления")
            return

        name = self.employee_table.item(selected_item, 'values')[0]
        direction = self.direction_combobox.get()

        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            try:
                if direction == "Менеджер":
                    query = "DELETE FROM maneger_avv WHERE name = %s"
                    cursor.execute(query, (name,))
                elif direction == "Мастер":
                    subquery = """
                        DELETE FROM firm_avv_has_master_avv 
                        WHERE mastet_AVV_id_master = 
                        (SELECT id_master FROM master_avv WHERE name = %s)
                    """
                    cursor.execute(subquery, (name,))
                    query = "DELETE FROM master_avv WHERE name = %s"
                    cursor.execute(query, (name,))
                conn.commit()
            except mysql.connector.Error as err:
                messagebox.showerror("Ошибка", f"Ошибка базы данных: {err}")
            finally:
                cursor.close()
                conn.close()
            self.load_employee()


class ReportFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Отчет о салоне красоты", font=("Arial", 18))
        label.pack(pady=10, padx=10)

        tk.Label(self, text="Салон красоты:").pack()
        self.salon_combobox = ttk.Combobox(self)
        self.salon_combobox.pack()

        tk.Button(self, text="Отчет", command=self.generate_report).pack(pady=10)

        self.report_text = tk.Text(self, wrap="word")
        self.report_text.pack(fill="both", expand=True)
        self.load_salon_data()

    def load_salon_data(self):
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name_firm FROM firm_avv")
            salons = [row[0] for row in cursor.fetchall()]
            self.salon_combobox['values'] = salons
            cursor.close()
            conn.close()

    def generate_report(self):
        salon = self.salon_combobox.get()
        conn = connect_to_db()
        if conn:
            cursor = conn.cursor()

            query_employee = """
               SELECT name, phone, 'Employee' AS type
               FROM maneger_avv
               JOIN firm_avv ON maneger_avv.firm_AVV_id_firm = firm_avv.id_firm
               WHERE firm_avv.name_firm = %s
               UNION
               SELECT name, phone, 'Employee' AS type
               FROM master_avv
               JOIN firm_avv_has_master_avv ON master_avv.id_master = firm_avv_has_master_avv.mastet_AVV_id_master
               JOIN firm_avv ON firm_avv_has_master_avv.firm_AVV_id_firm = firm_avv.id_firm
               WHERE firm_avv.name_firm = %s
               """
            cursor.execute(query_employee, (salon, salon))
            employee_rows = cursor.fetchall()

            query_supplies = """
               SELECT name_sup, count, 'Supply' AS type
               FROM supplies_avv
               """
            cursor.execute(query_supplies)
            supply_rows = cursor.fetchall()

            query_clients = """
                      SELECT name, phone_num, 'Client' AS type
                      FROM Client_AVV
                      JOIN firm_AVV_has_Client_AVV ON Client_AVV.id_client = firm_AVV_has_Client_AVV.Client_AVV_id_client
                      JOIN firm_avv ON firm_AVV_has_Client_AVV.firm_AVV_id_firm = firm_avv.id_firm
                      WHERE firm_avv.name_firm = %s
                      """
            cursor.execute(query_clients, (salon,))
            client_rows = cursor.fetchall()

            report = ""
            report += "==============================================\n"
            report += "================Работники=====================\n"
            report += "==============================================\n"
            for row in employee_rows:
                report += f" Имя: {row[0]}, Телефон: {row[1]}\n"
            '''  report += "==============================================\n"
                report += "=============Расходные материалы==============\n"
                report += "==============================================\n"
                for row in supply_rows:
                    report += f" Название: {row[0]}, Количество: {row[1]}\n"'''

            report += "==============================================\n"
            report += "=================Клиенты======================\n"
            report += "==============================================\n"
            for row in client_rows:
                report += f" Имя: {row[0]}, Телефон: {row[1]}\n"

            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)

            cursor.close()
            conn.close()


if __name__ == "__main__":
    app = SalonApp()
    app.mainloop()
