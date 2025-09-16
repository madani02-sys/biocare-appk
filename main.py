import flet as ft
import sqlite3
from add_form import create_add_view
from consultation_view import create_consultation_view
from consultation_reception_view import create_consultation_reception_view
from auth_view import create_auth_database, create_login_view, create_register_view
from admin_view import create_user_management_view, is_admin
from reception_form import create_reception_view
from home_view import create_home_view
from sheet_form import create_sheet_view
from consultation_sheet_view import create_consultation_sheet_view

def create_database():
    conn = sqlite3.connect('pesees.db')
    c = conn.cursor()
    
    # Table pesees existante
    c.execute('''CREATE TABLE IF NOT EXISTS pesees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  produit TEXT,
                  n_lot TEXT,
                  ddf TEXT,
                  ddp TEXT,
                  nb_caisses_pesees INTEGER,
                  intervalle_pesee TEXT,
                  nb_caisses_conformes INTEGER,
                  nb_caisses_non_conformes INTEGER,
                  numero_caisse_non_conforme TEXT,
                  anomalie_observee TEXT,
                  created_by TEXT)''')
    
    # Nouvelle table controle_reception
    c.execute('''CREATE TABLE IF NOT EXISTS controle_reception
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  heure TEXT,
                  article TEXT,
                  nature_article TEXT,
                  n_lot TEXT,
                  dlc TEXT,
                  ddp TEXT,
                  quantite_receptionnee INTEGER,
                  conformite TEXT,
                  non_conformite TEXT,
                  reference TEXT,
                  anomalie TEXT,
                  created_by TEXT)''')
    
    # Nouvelle table sheet
    c.execute('''CREATE TABLE IF NOT EXISTS sheet
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  produit TEXT NOT NULL,
                  lot TEXT NOT NULL,
                  qte_pesee_caisse INTEGER NOT NULL,
                  anomalie TEXT,
                  action_corrective TEXT,
                  created_by TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def is_authenticated(page):
    """Vérifier si l'utilisateur est authentifié"""
    try:
        auth_status = page.client_storage.get("authenticated")
        return auth_status == "true"
    except:
        return False

def create_logout_button(page):
    """Créer un bouton de déconnexion"""
    def handle_logout(e):
        # Effacer le stockage client
        page.client_storage.clear()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Déconnexion réussie!"),
            bgcolor=ft.Colors.ORANGE
        )
        page.snack_bar.open = True
        page.go("/login")
    
    username = page.client_storage.get("username") or "Utilisateur"
    
    return ft.PopupMenuButton(
        icon=ft.Icons.PERSON,  # Changed from icons to Icons
        tooltip=username,
        items=[
            ft.PopupMenuItem(
                text=f"Connecté en tant que {username}",
                icon=ft.Icons.PERSON_OUTLINE,  # Changed from icons to Icons
                disabled=True
            ),
            ft.PopupMenuItem(
                text="Déconnexion",
                icon=ft.Icons.LOGOUT,  # Changed from icons to Icons
                on_click=handle_logout
            )
        ]
    )

def create_main_app_bar(page):
    """Créer la barre d'application principale avec menu de navigation"""
    actions = [
        ft.IconButton(
            icon=ft.Icons.HOME,
            tooltip="Accueil",
            on_click=lambda _: page.go("/home")
        ),
        ft.IconButton(
            icon=ft.Icons.SCALE,
            tooltip="Gestion des Pesées",
            on_click=lambda _: page.go("/pesees")
        ),
        ft.IconButton(
            icon=ft.Icons.RECEIPT_LONG,
            tooltip="Contrôle de réception",
            on_click=lambda _: page.go("/reception")
        ),
        ft.IconButton(
            icon=ft.Icons.ASSIGNMENT,
            tooltip="Sheet",
            on_click=lambda _: page.go("/sheet")
        )
    ]
    
    # Ajouter le bouton d'administration si l'utilisateur est admin
    if is_admin(page):
        actions.append(
            ft.IconButton(
                icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                tooltip="Administration",
                on_click=lambda _: page.go("/admin")
            )
        )
    
    actions.append(create_logout_button(page))
    
    return ft.AppBar(
        title=ft.Text("Gestion des Pesées", size=20, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        actions=actions
    )

def main(page: ft.Page):
    # Configuration de base
    page.title = "Gestion des Pesées"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(use_material3=True)
    page.padding = 0
    page.spacing = 0
    page.scroll = ft.ScrollMode.AUTO
   
    # Initialisation de la taille de fenêtre pour desktop
    if hasattr(page, "window_width"):
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
    
    # Create databases first to avoid delays
    try:
        create_database()
        create_auth_database()
    except Exception as e:
        print(f"Database error: {e}")
    
    # Define a simpler route change handler
    def route_change(e):
        try:
            page.views.clear()
            
            if page.route == "/login" or not is_authenticated(page):
                page.views.append(create_login_view(page))
            elif page.route == "/" or page.route == "/home":
                view = create_home_view(page)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
            # Route for the weighing form
            elif page.route == "/pesees":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                # Récupérer les données pour la modification
                record_to_edit = page.client_storage.get("record_to_edit")
                
                # Créer la vue avec les données
                view = create_add_view(page, record_to_edit)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
                
                # Nettoyer les données après utilisation
                if record_to_edit:
                    page.client_storage.remove("record_to_edit")
            
            # Private routes (authentication required)
            elif page.route == "/consultation":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                view = create_consultation_view(page)
                if hasattr(view, 'appbar') and view.appbar:
                    actions = [
                        ft.IconButton(
                            icon=ft.Icons.ADD,  # Changed from icons to Icons
                            tooltip="Ajouter une pesée",
                            on_click=lambda _: page.go("/home")
                        )
                    ]
                    
                    if is_admin(page):
                        actions.append(
                            ft.IconButton(
                                icon=ft.Icons.ADMIN_PANEL_SETTINGS,  # Changed from icons to Icons
                                tooltip="Administration",
                                on_click=lambda _: page.go("/admin")
                        )
                    )
                    
                    actions.append(create_logout_button(page))
                    view.appbar.actions = actions
                page.views.append(view)
            
            elif page.route == "/consultation-reception":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                view = create_consultation_reception_view(page)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
            
            elif page.route == "/admin":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                if not is_admin(page):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Accès refusé. Droits d'administrateur requis."),
                        bgcolor=ft.Colors.RED
                    )
                    page.snack_bar.open = True
                    page.go("/home")
                    return
                
                view = create_user_management_view(page)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
            
            elif page.route == "/reception":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                view = create_reception_view(page)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
            
            elif page.route == "/sheet":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                record_to_edit = page.client_storage.get("sheet_to_edit")
                view = create_sheet_view(page, record_to_edit)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
                
                if record_to_edit:
                    page.client_storage.remove("sheet_to_edit")
            
            elif page.route == "/consultation-sheet":
                if not is_authenticated(page):
                    page.go("/login")
                    return
                
                view = create_consultation_sheet_view(page)
                view.appbar = create_main_app_bar(page)
                page.views.append(view)
            
            else:
                # Route par défaut
                if is_authenticated(page):
                    page.go("/home")
                else:
                    page.go("/login")
                return
                
            page.update()
        except Exception as ex:
            print(f"Route error: {ex}")
            # Fall back to login on error
            page.views.clear()
            page.views.append(create_login_view(page))
            page.update()
    
    page.on_route_change = route_change
    
    # Start with login
    page.go("/login")

if __name__ == "__main__":
    import socket
    
    def try_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))  # Try localhost first
            sock.close()
            return True
        except:
            sock.close()
            return False
    
    # Find an available port
    port = 8550
    while not try_port(port) and port < 8600:
        port += 1
    
    if port >= 8600:
        print("No available ports found")
        exit(1)
    
    print(f"\n{'='*50}")
    print(f"App running at http://127.0.0.1:{port} (local)")
    print(f"and http://192.168.5.115:{port} (network)")
    print(f"{'='*50}\n")
    
    try:
        # Use a simpler configuration
        ft.app(
            target=main,
            port=port,
            view=ft.WEB_BROWSER
        )
    except Exception as e:
        print(f"App error: {e}")