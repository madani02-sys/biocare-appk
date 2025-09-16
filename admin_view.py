import flet as ft
import sqlite3
from auth_view import hash_password

def is_admin(page):
    """Vérifier si l'utilisateur connecté est un administrateur"""
    try:
        # Use client_storage instead of session
        role = page.client_storage.get("user_role")
        return role == "admin"
    except Exception as ex:
        print(f"Error checking admin status: {ex}")
        return False

def add_role_column_if_not_exists():
    """Ajouter la colonne role si elle n'existe pas et définir admin comme administrateur"""
    try:
        conn = sqlite3.connect('pesees.db')
        c = conn.cursor()
        
        # Vérifier si la colonne role existe
        result = c.execute("PRAGMA table_info(users)").fetchall()
        has_role_column = any(column[1] == 'role' for column in result)
        
        if not has_role_column:
            # Ajouter la colonne role
            c.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT "user"')
            # Définir l'utilisateur admin comme administrateur
            c.execute('UPDATE users SET role = "admin" WHERE username = "admin"')
            conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'ajout de la colonne role: {e}")

def create_user_management_view(page: ft.Page):
    """Créer la vue de gestion des utilisateurs"""
    
    add_role_column_if_not_exists()
    
    # Table des utilisateurs
    users_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", size=14, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Nom d'utilisateur", size=14, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Rôle", size=14, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Date de création", size=14, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", size=14, weight=ft.FontWeight.BOLD))
        ],
        border=ft.border.all(2, ft.Colors.BLUE),
        column_spacing=30,
        heading_row_height=50,
    )
    
    # Formulaire d'ajout d'utilisateur
    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=250,
        prefix_icon=ft.Icons.PERSON
    )
    
    password_field = ft.TextField(
        label="Mot de passe",
        width=250,
        password=True,
        prefix_icon=ft.Icons.LOCK
    )
    
    role_dropdown = ft.Dropdown(
        label="Rôle",
        width=150,
        options=[
            ft.dropdown.Option("user", "Utilisateur"),
            ft.dropdown.Option("admin", "Administrateur")
        ],
        value="user"
    )
    
    def load_users():
        users_table.rows.clear()
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            users = c.execute('''SELECT id, username, role, created_at 
                               FROM users ORDER BY id DESC''').fetchall()
            conn.close()
            
            if not users:
                users_table.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Aucun utilisateur"))] * 5)
                )
            else:
                for user in users:
                    users_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(user[0]))),
                                ft.DataCell(ft.Text(user[1])),
                                ft.DataCell(ft.Text(user[2] or "user")),
                                ft.DataCell(ft.Text(user[3] or "N/A")),
                                ft.DataCell(
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED,
                                            tooltip="Supprimer",
                                            on_click=lambda e, uid=user[0], uname=user[1]: delete_user(e, uid, uname),
                                            disabled=(user[1] == "admin" and user[1] == page.session.get("username"))
                                        )
                                    ])
                                )
                            ]
                        )
                    )
        except Exception as e:
            print(f"Erreur lors du chargement des utilisateurs: {e}")
        page.update()
    
    def create_user(e):
        if not username_field.value or not password_field.value:
            show_error("Veuillez remplir tous les champs")
            return
        
        if len(password_field.value) < 4:
            show_error("Le mot de passe doit contenir au moins 4 caractères")
            return
        
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            hashed_password = hash_password(password_field.value)
            c.execute('''INSERT INTO users (username, password, role) 
                        VALUES (?, ?, ?)''',
                     (username_field.value, hashed_password, role_dropdown.value))
            
            conn.commit()
            conn.close()
            
            # Vider les champs
            username_field.value = ""
            password_field.value = ""
            role_dropdown.value = "user"
            
            show_success(f"Utilisateur '{username_field.value}' créé avec succès!")
            load_users()
            
        except sqlite3.IntegrityError:
            show_error("Ce nom d'utilisateur existe déjà")
        except Exception as ex:
            show_error(f"Erreur lors de la création: {str(ex)}")
    
    def delete_user(e, user_id, username):
        current_user = page.session.get("username")
        
        if username == "admin" and username == current_user:
            show_error("Vous ne pouvez pas supprimer votre propre compte administrateur")
            return
        
        def confirm_delete(e):
            if e.control.text == "Oui":
                try:
                    conn = sqlite3.connect('pesees.db')
                    c = conn.cursor()
                    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    conn.commit()
                    conn.close()
                    
                    dialog.open = False
                    show_success(f"Utilisateur '{username}' supprimé!")
                    load_users()
                    
                except Exception as ex:
                    show_error(f"Erreur lors de la suppression: {str(ex)}")
            else:
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text(f"Voulez-vous vraiment supprimer l'utilisateur '{username}'?"),
            actions=[
                ft.TextButton("Oui", on_click=confirm_delete),
                ft.TextButton("Non", on_click=confirm_delete),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()
    
    def show_success(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    # Charger les utilisateurs au démarrage
    load_users()
    
    return ft.View(
        "/admin",
        [
            ft.Container(
                content=ft.Column([
                    # En-tête
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40, color=ft.Colors.BLUE),
                            ft.Text(
                                "Administration des utilisateurs",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_800
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        margin=ft.margin.only(bottom=30)
                    ),
                    
                    # Formulaire de création d'utilisateur
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Créer un nouvel utilisateur", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                username_field,
                                password_field,
                                role_dropdown,
                                ft.ElevatedButton(
                                    "Créer utilisateur",
                                    icon=ft.Icons.PERSON_ADD,
                                    on_click=create_user,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    height=40
                                )
                            ], alignment=ft.MainAxisAlignment.START, spacing=15)
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.GREEN_200),
                        margin=ft.margin.only(bottom=30)
                    ),
                    
                    # Liste des utilisateurs
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Liste des utilisateurs", size=18, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    tooltip="Actualiser",
                                    on_click=lambda _: load_users()
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([users_table], scroll=ft.ScrollMode.AUTO, expand=True)
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                        expand=True
                    ),
                    
                    # Bouton de retour
                    ft.Container(
                        content=ft.ElevatedButton(
                            "Retour au menu principal",
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda _: page.go("/home"),
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLUE,
                                shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            width=200
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=20)
                    )
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=30,
                expand=True
            )
        ]
    )

def create_login_view(page: ft.Page):
    def handle_login(e):
        if not username_field.value or not password_field.value:
            show_error("Veuillez remplir tous les champs")
            return

        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            # Hash the password
            hashed_password = hash_password(password_field.value)
            
            # Get user with role
            result = c.execute('''

                SELECT username, role 
                FROM users 
                WHERE username = ? AND password = ?
            ''', (username_field.value, hashed_password)).fetchone()
            
            conn.close()
            
            if result:
                username, role = result
                # Store in client_storage
                page.client_storage.set("authenticated", "true")
                page.client_storage.set("username", username)
                page.client_storage.set("user_role", role)  # Store the role
                
                # Show success message
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Bienvenue {username}!"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()
                page.go("/home")
            else:
                show_error("Nom d'utilisateur ou mot de passe incorrect")
                
        except Exception as ex:
            print(f"Login error: {ex}")
            show_error("Erreur lors de la connexion")
    
    # Champ de nom d'utilisateur
    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=250,
        prefix_icon=ft.Icons.PERSON
    )
    
    # Champ de mot de passe
    password_field = ft.TextField(
        label="Mot de passe",
        width=250,
        password=True,
        prefix_icon=ft.Icons.LOCK
    )
    
    return ft.View(
        "/login",
        [
            ft.Container(
                content=ft.Column([
                    # En-tête
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGIN, size=40, color=ft.Colors.BLUE),
                            ft.Text(
                                "Connexion",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_800
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        margin=ft.margin.only(bottom=30)
                    ),
                    
                    # Formulaire de connexion
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Veuillez vous connecter", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                username_field,
                                password_field,
                                ft.ElevatedButton(
                                    "Se connecter",
                                    icon=ft.Icons.LOGIN,
                                    on_click=handle_login,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    ),
                                    height=40
                                )
                            ], alignment=ft.MainAxisAlignment.START, spacing=15)
                        ]),
                        padding=20,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                        margin=ft.margin.only(bottom=30)
                    ),
                    
                    # Lien vers la page d'inscription
                    ft.Container(
                        content=ft.TextButton(
                            "Créer un compte",
                            on_click=lambda _: page.go("/register"),
                            style=ft.TextButtonStyle(
                                color=ft.Colors.BLUE,
                                text_decoration=ft.TextDecoration.UNDERLINE
                            )
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=10, bottom=20)
                    ),
                    
                    # Message d'erreur (si nécessaire)
                    ft.Container(
                        content=ft.Text(""),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=10, bottom=20)
                    )
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=30,
                expand=True
            )
        ]
    )