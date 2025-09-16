import flet as ft
import sqlite3
import hashlib

def create_auth_database():
    """Créer la base de données pour l'authentification"""
    conn = sqlite3.connect('pesees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Créer un utilisateur par défaut (admin/admin)
    default_password = hashlib.sha256("admin".encode()).hexdigest()
    c.execute('''INSERT OR IGNORE INTO users (username, password) 
                 VALUES (?, ?)''', ("admin", default_password))
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hasher le mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Vérifier les identifiants utilisateur"""
    conn = sqlite3.connect('pesees.db')
    c = conn.cursor()
    
    hashed_password = hash_password(password)
    # Modifié pour retourner plus d'informations sur l'utilisateur
    result = c.execute('''SELECT id, username, role 
                         FROM users 
                         WHERE username = ? AND password = ?''', 
                      (username, hashed_password)).fetchone()
    
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "role": result[2] if result[2] else "user"  # Valeur par défaut si role est NULL
        }
    return None

def create_login_view(page: ft.Page):
    """Créer la vue de connexion"""
    
    # Champs de saisie
    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=300,
        prefix_icon=ft.Icons.PERSON,
        border_radius=10
    )
    
    password_field = ft.TextField(
        label="Mot de passe",
        width=300,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=10
    )
    
    # Checkbox "Se souvenir de moi"
    remember_checkbox = ft.Checkbox(
        label="Se souvenir de moi",
        value=False
    )
    
    def handle_login(e):
        if not username_field.value or not password_field.value:
            show_error("Veuillez saisir votre nom d'utilisateur et mot de passe")
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
                # Store in client_storage instead of session
                page.client_storage.set("authenticated", "true")
                page.client_storage.set("username", username)
                page.client_storage.set("user_role", role)
                
                # Show success message
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Bienvenue {username}!"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.go("/home")
            else:
                show_error("Nom d'utilisateur ou mot de passe incorrect")
                
        except Exception as ex:
            print(f"Login error: {ex}")
            show_error("Erreur lors de la connexion")
    
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()
    
    def handle_register(e):
        # Désactiver l'inscription publique - seuls les admins peuvent créer des utilisateurs
        page.snack_bar = ft.SnackBar(
            content=ft.Text("L'inscription publique est désactivée. Contactez votre administrateur."),
            bgcolor=ft.Colors.ORANGE
        )
        page.snack_bar.open = True
        page.update()
    
    def on_enter_key(e):
        if e.key == "Enter":
            handle_login(e)
    
    # Ajouter les gestionnaires d'événements pour Enter
    username_field.on_submit = handle_login
    password_field.on_submit = handle_login
    
    return ft.View(
        "/login",
        [
            ft.Container(
                content=ft.Column(
                    [
                        # Logo/Titre
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(
                                    ft.Icons.SCALE,
                                    size=80,
                                    color=ft.Colors.BLUE
                                ),
                                ft.Text(
                                    "Gestion des Pesées",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_800
                                ),
                                ft.Text(
                                    "Connexion à votre compte",
                                    size=16,
                                    color=ft.Colors.GREY_600
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            margin=ft.margin.only(bottom=30)
                        ),
                        
                        # Formulaire de connexion
                        ft.Container(
                            content=ft.Column([
                                username_field,
                                password_field,
                                remember_checkbox,
                                
                                # Bouton de connexion
                                ft.ElevatedButton(
                                    "Se connecter",
                                    width=300,
                                    height=45,
                                    on_click=handle_login,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    )
                                ),
                                
                                ft.Container(height=10),
                                
                                # Lien d'inscription (désactivé)
                                ft.TextButton(
                                    "Créer un nouveau compte",
                                    on_click=handle_register,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.GREY
                                    )
                                ),
                                
                                # Informations de connexion par défaut
                                ft.Container(
                                    content=ft.Column([
                                        ft.Divider(),
                                        ft.Text(
                                            "Compte par défaut:",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.GREY_600
                                        ),
                                        ft.Text(
                                            "Utilisateur: admin",
                                            size=12,
                                            color=ft.Colors.GREY_600
                                        ),
                                        ft.Text(
                                            "Mot de passe: admin",
                                            size=12,
                                            color=ft.Colors.GREY_600
                                        )
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    margin=ft.margin.only(top=20)
                                )
                                
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                            padding=30,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=15,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=ft.Colors.GREY_400,
                                offset=ft.Offset(0, 5),
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=20,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_50
            )
        ],
        bgcolor=ft.Colors.BLUE_50
    )

def create_register_view(page: ft.Page):
    """Créer la vue d'inscription"""
    
    username_field = ft.TextField(
        label="Nom d'utilisateur",
        width=300,
        prefix_icon=ft.Icons.PERSON,
        border_radius=10
    )
    
    password_field = ft.TextField(
        label="Mot de passe",
        width=300,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=10
    )
    
    confirm_password_field = ft.TextField(
        label="Confirmer le mot de passe",
        width=300,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=10
    )
    
    def handle_register(e):
        if not all([username_field.value, password_field.value, confirm_password_field.value]):
            show_error("Veuillez remplir tous les champs")
            return
        
        if password_field.value != confirm_password_field.value:
            show_error("Les mots de passe ne correspondent pas")
            return
        
        if len(password_field.value) < 4:
            show_error("Le mot de passe doit contenir au moins 4 caractères")
            return
        
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            hashed_password = hash_password(password_field.value)
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (username_field.value, hashed_password))
            
            conn.commit()
            conn.close()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Compte créé avec succès!"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.go("/login")
            
        except sqlite3.IntegrityError:
            show_error("Ce nom d'utilisateur existe déjà")
        except Exception as ex:
            show_error(f"Erreur lors de la création du compte: {str(ex)}")
    
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()
    
    return ft.View(
        "/register",
        [
            ft.Container(
                content=ft.Column(
                    [
                        # Titre
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(
                                    ft.Icons.PERSON_ADD,
                                    size=80,
                                    color=ft.Colors.GREEN
                                ),
                                ft.Text(
                                    "Créer un compte",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_800
                                ),
                                ft.Text(
                                    "Inscrivez-vous pour accéder à l'application",
                                    size=16,
                                    color=ft.Colors.GREY_600
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            margin=ft.margin.only(bottom=30)
                        ),
                        
                        # Formulaire d'inscription
                        ft.Container(
                            content=ft.Column([
                                username_field,
                                password_field,
                                confirm_password_field,
                                
                                # Bouton d'inscription
                                ft.ElevatedButton(
                                    "S'inscrire",
                                    width=300,
                                    height=45,
                                    on_click=handle_register,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN,
                                        shape=ft.RoundedRectangleBorder(radius=10)
                                    )
                                ),
                                
                                ft.Container(height=10),
                                
                                # Lien de retour à la connexion
                                ft.TextButton(
                                    "Déjà un compte? Se connecter",
                                    on_click=lambda _: page.go("/login"),
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.GREEN
                                    )
                                )
                                
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                            padding=30,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=15,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=ft.Colors.GREY_400,
                                offset=ft.Offset(0, 5),
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                padding=20,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.GREEN_50
            )
        ],
        bgcolor=ft.Colors.GREEN_50
    )