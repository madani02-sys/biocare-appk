import flet as ft
import sqlite3
from datetime import datetime

def create_modern_search_bar(
    date_field: ft.TextField,
    product_field: ft.TextField,
    lot_field: ft.TextField,
    on_search,
    on_reset,
    is_mobile: bool = False
):
    """Create a modern search bar with consistent styling"""
    
    # Style the date field
    date_field.label = "Date"
    date_field.hint_text = "YYYY-MM-DD"
    date_field.prefix_icon = ft.Icons.CALENDAR_TODAY
    date_field.border_radius = 8
    date_field.filled = True
    date_field.expand = True if is_mobile else False
    date_field.width = None if is_mobile else 180
    date_field.height = 48
    date_field.border_color = ft.Colors.BLUE_100
    date_field.focused_border_color = ft.Colors.BLUE
    date_field.focused_bgcolor = ft.Colors.BLUE_50

    # Style the product field
    product_field.label = "Produit"
    product_field.hint_text = "Rechercher produit..."
    product_field.prefix_icon = ft.Icons.INVENTORY_2
    product_field.border_radius = 8
    product_field.filled = True
    product_field.expand = True if is_mobile else False
    product_field.width = None if is_mobile else 220
    product_field.height = 48
    product_field.border_color = ft.Colors.BLUE_100
    product_field.focused_border_color = ft.Colors.BLUE
    product_field.focused_bgcolor = ft.Colors.BLUE_50

    # Style the lot field
    lot_field.label = "N° LOT"
    lot_field.hint_text = "Numéro de lot..."
    lot_field.prefix_icon = ft.Icons.NUMBERS
    lot_field.border_radius = 8
    lot_field.filled = True
    lot_field.expand = True if is_mobile else False
    lot_field.width = None if is_mobile else 180
    lot_field.height = 48
    lot_field.border_color = ft.Colors.BLUE_100
    lot_field.focused_border_color = ft.Colors.BLUE
    lot_field.focused_bgcolor = ft.Colors.BLUE_50

    # Create styled search button
    search_button = ft.ElevatedButton(
        "Rechercher",
        icon=ft.Icons.SEARCH,
        on_click=on_search,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE,
            elevation=0,
            padding=15,
            animation_duration=200,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    # Create styled reset button
    reset_button = ft.OutlinedButton(
        "Réinitialiser",
        icon=ft.Icons.REFRESH,
        on_click=on_reset,
        style=ft.ButtonStyle(
            color=ft.Colors.BLUE_GREY,
            padding=15,
        ),
    )

    # Create layout based on mobile or desktop view
    if is_mobile:
        search_layout = ft.Column(
            [
                ft.Text("Rechercher", size=16, weight=ft.FontWeight.BOLD),
                date_field,
                product_field,
                lot_field,
                ft.Row(
                    [search_button, reset_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    else:
        search_layout = ft.Column(
            [
                ft.Text("Filtrer les résultats", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        date_field,
                        product_field,
                        lot_field,
                    ],
                    wrap=True,
                    spacing=10,
                ),
                ft.Row(
                    [search_button, reset_button],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                ),
            ],
            spacing=15,
        )

    # Return a container with shadow and rounded corners
    return ft.Container(
        content=search_layout,
        padding=20,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        border=ft.border.all(1, ft.Colors.BLUE_100),
    )

def create_consultation_view(page: ft.Page):
    try:
        # Déterminer si on est en mode mobile de manière sûre
        def is_mobile():
            try:
                # Tenter d'accéder à window_width s'il existe
                if hasattr(page, "window_width") and page.window_width:
                    return page.window_width < 768
                
                # Sinon, utiliser la propriété width qui est toujours disponible
                if page.width:
                    return page.width < 768
                
                # Par défaut, supposer une vue bureau (desktop)
                return False
            except:
                # En cas d'erreur, utiliser la vue bureau par défaut
                return False
        
        mobile = is_mobile()
        print(f"Est mobile: {mobile}")
        
        if mobile:
            # Vue mobile - cartes empilées avec seulement les colonnes demandées
            return create_mobile_consultation_view(page)
        else:
            # Vue desktop - tableau simplifié
            return create_desktop_consultation_view(page)
            
    except Exception as ex:
        print(f"Error creating consultation view: {ex}")
        return ft.View(
            "/consultation",
            [ft.Text(f"Error: {str(ex)}", color=ft.Colors.RED)]
        )

def create_mobile_consultation_view(page: ft.Page):
    # État pour contrôler la visibilité de la barre de recherche
    search_visible = False
    
    # Container pour les cartes
    records_column = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    # Créer les champs de recherche
    date_search = ft.TextField()
    product_search = ft.TextField()
    lot_search = ft.TextField()
    
    def do_search(_):
        load_mobile_data(
            date_search.value,
            product_search.value,
            lot_search.value
        )
    
    def reset_search(_):
        date_search.value = ""
        product_search.value = ""
        lot_search.value = ""
        page.update()
        load_mobile_data()

    # Créer la barre de recherche mobile
    search_bar = create_modern_search_bar(
        date_search,
        product_search,
        lot_search,
        do_search,
        reset_search,
        is_mobile=True
    )

    # Créer un conteneur pour la barre de recherche avec animation
    search_container = ft.AnimatedSwitcher(
        content=search_bar,
        visible=False,  # Caché par défaut
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    def toggle_search(_):
        nonlocal search_visible
        search_visible = not search_visible
        search_container.visible = search_visible
        page.update()

    # Bouton de recherche dans l'AppBar
    search_button = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_color=ft.Colors.WHITE,
        tooltip="Rechercher",
        on_click=toggle_search
    )

    # Container pour les cartes
    records_column = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
    
    def load_mobile_data():
        records_column.controls.clear()
        conn = sqlite3.connect('pesees.db')
        c = conn.cursor()
        
        try:
            # Récupérer uniquement les colonnes nécessaires
            rows = c.execute('SELECT id, date, produit, n_lot, created_by FROM pesees ORDER BY date DESC').fetchall()
            
            if not rows:
                records_column.controls.append(
                    ft.Container(
                        content=ft.Text("Aucune donnée disponible", text_align=ft.TextAlign.CENTER),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=8,
                        margin=10
                    )
                )
            else:
                for row in rows:
                    record_id = row[0]
                    date = str(row[1]) if row[1] else "-"
                    produit = str(row[2]) if row[2] else "-"
                    n_lot = str(row[3]) if row[3] else "-"
                    created_by = str(row[4]) if row[4] else "N/A"
                    
                    # Création d'une carte pour chaque enregistrement avec seulement les colonnes demandées
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.CALENDAR_TODAY),
                                    title=ft.Text(f"Date: {date}", weight=ft.FontWeight.BOLD),
                                    subtitle=ft.Text(f"Produit: {produit}"),
                                ),
                                ft.Divider(height=1),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"N° LOT: {n_lot}"),
                                        ft.Text(f"Créé par: {created_by}")
                                    ]),
                                    padding=10,
                                ),
                                ft.Row([
                                    ft.TextButton(
                                        "Modifier",
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda e, id=record_id: edit_record(e, id),
                                    ),
                                    ft.TextButton(
                                        "Supprimer",
                                        icon=ft.Icons.DELETE,
                                        on_click=lambda e, rid=record_id: delete_record(e, rid),
                                    ),
                                ], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=10
                        ),
                        margin=10
                    )
                    records_column.controls.append(card)
                
        except Exception as ex:
            print(f"Error loading data: {ex}")
            records_column.controls.append(
                ft.Container(
                    content=ft.Text(f"Erreur: {str(ex)}", color=ft.Colors.RED),
                    padding=20
                )
            )
        finally:
            conn.close()
            page.update()

    def delete_record(e, record_id):
        def confirm_delete(e):
            if e.control.text == "Oui":
                conn = sqlite3.connect('pesees.db')
                c = conn.cursor()
                c.execute('DELETE FROM pesees WHERE id = ?', (record_id,))
                conn.commit()
                conn.close()
                
                # Reload data
                load_mobile_data()
                
                # Show message
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Enregistrement supprimé!"))
                page.snack_bar.open = True
                page.update()
            else:
                dialog.open = False
                page.update()

        # Create confirmation dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmation"),
            content=ft.Text("Voulez-vous vraiment supprimer cet enregistrement?"),
            actions=[
                ft.TextButton("Oui", on_click=confirm_delete),
                ft.TextButton("Non", on_click=confirm_delete),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def edit_record(e, record_id):
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            record = c.execute('SELECT * FROM pesees WHERE id = ?', (record_id,)).fetchone()
            conn.close()

            if record:
                page.client_storage.set("record_to_edit", record)
                page.go("/pesees")
                
        except Exception as ex:
            print(f"Error in edit_record: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Erreur lors de la modification"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
    
    # Charger les données
    load_mobile_data()
    
    # Bouton d'ajout flottant pour mobile
    add_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE,
        on_click=lambda _: page.go("/pesees")
    )
    
    # Créer les champs de recherche
    date_search = ft.TextField()
    product_search = ft.TextField()
    lot_search = ft.TextField()
    
    def do_search(_):
        load_mobile_data(
            date_search.value,
            product_search.value,
            lot_search.value
        )
    
    def reset_search(_):
        date_search.value = ""
        product_search.value = ""
        lot_search.value = ""
        page.update()
        load_mobile_data()

    # Créer la barre de recherche mobile
    search_bar = create_modern_search_bar(
        date_search,
        product_search,
        lot_search,
        do_search,
        reset_search,
        is_mobile=True
    )

    # Créer un conteneur pour la barre de recherche avec animation
    search_container = ft.AnimatedSwitcher(
        content=search_bar,
        visible=False,  # Caché par défaut
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    def toggle_search(_):
        nonlocal search_visible
        search_visible = not search_visible
        search_container.visible = search_visible
        page.update()

    # Bouton de recherche dans l'AppBar
    search_button = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_color=ft.Colors.WHITE,
        tooltip="Rechercher",
        on_click=toggle_search
    )

    # Modifier le return pour inclure le bouton de recherche dans l'AppBar
    return ft.View(
        "/consultation",
        [
            ft.AppBar(
                title=ft.Text("Liste des Pesées"),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: page.go("/")
                ),
                actions=[
                    search_button,  # Ajouter le bouton de recherche
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        on_click=lambda _: load_mobile_data()
                    )
                ]
            ),
            search_container,  # Barre de recherche cachée par défaut
            ft.Container(
                content=records_column,
                expand=True,
                padding=10
            )
        ],
        floating_action_button=add_button,
        scroll=ft.ScrollMode.AUTO
    )

def create_desktop_consultation_view(page: ft.Page):
    # État pour contrôler la visibilité de la barre de recherche
    search_visible = False

    # Création d'un thème cohérent - Fix: use ft.Colors instead of ft.colors
    theme = {
        "primary": ft.Colors.BLUE,
        "primary_container": ft.Colors.BLUE_100,
        "secondary": ft.Colors.GREY_800,
        "surface": ft.Colors.WHITE,
        "background": ft.Colors.GREY_50,
    }

    # Fix: Update all icon references from ft.icons to ft.Icons
    date_search = ft.TextField(
        label="Date",
        hint_text="YYYY-MM-DD",
        prefix_icon=ft.Icons.CALENDAR_TODAY,  # Fix: uppercase Icons
        border_radius=8,
        filled=True,
        expand=True,
        height=48,
    )
    
    product_search = ft.TextField(
        label="Produit",
        hint_text="Rechercher un produit...",
        prefix_icon=ft.Icons.INVENTORY_2,  # Fix: uppercase Icons
        border_radius=8,
        filled=True,
        expand=True,
        height=48,
    )
    
    lot_search = ft.TextField(
        label="N° LOT",
        hint_text="Numéro de lot...",
        prefix_icon=ft.Icons.NUMBERS,  # Fix: uppercase Icons
        border_radius=8,
        filled=True,
        expand=True,
        height=48,
    )

    # Compteur de résultats stylé
    results_counter = ft.Text(
        size=14,
        color=theme["secondary"],
        weight=ft.FontWeight.W_500
    )

    def do_search(_):
        load_data(
            date_search.value,
            product_search.value,
            lot_search.value
        )

    def reset_search(_):
        date_search.value = ""
        product_search.value = ""
        lot_search.value = ""
        page.update()
        load_data()

    # Barre de recherche moderne
    search_bar = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SEARCH, color=theme["primary"]),
                    ft.Text(
                        "Recherche avancée",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=theme["primary"]
                    )
                ], alignment=ft.MainAxisAlignment.START),
                ft.ResponsiveRow([
                    ft.Column([date_search], col={"sm": 12, "md": 4}),
                    ft.Column([product_search], col={"sm": 12, "md": 4}),
                    ft.Column([lot_search], col={"sm": 12, "md": 4}),
                ]),
                ft.Row([
                    results_counter,
                    ft.Row([
                        ft.ElevatedButton(
                            "Rechercher",
                            icon=ft.Icons.SEARCH,
                            on_click=do_search,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=theme["primary"],
                                elevation=0,
                                padding=15,
                            ),
                        ),
                        ft.OutlinedButton(
                            "Réinitialiser",
                            icon=ft.Icons.REFRESH,
                            on_click=reset_search,
                        ),
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=20),
            padding=20,
        ),
        elevation=0,
        color=theme["surface"],
    )

    # Container de recherche avec animation
    search_container = ft.AnimatedSwitcher(
        content=search_bar,
        visible=False,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    def toggle_search(_):
        nonlocal search_visible
        search_visible = not search_visible
        search_container.visible = search_visible
        page.update()

    # Table responsive
    consultation_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Produit", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("N° LOT", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Créé par", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
        ],
        border=ft.border.all(1, theme["primary_container"]),
        border_radius=8,
        vertical_lines=ft.border.BorderSide(1, theme["primary_container"]),
        horizontal_lines=ft.border.BorderSide(1, theme["primary_container"]),
        column_spacing=40,
        heading_row_color=theme["primary_container"],
        heading_row_height=50,
    )

    def load_data(date_filter="", product_filter="", lot_filter=""):
        consultation_table.rows.clear()
        conn = sqlite3.connect('pesees.db')
        c = conn.cursor()
        
        try:
            # Récupérer uniquement les colonnes nécessaires
            query = 'SELECT id, date, produit, n_lot, created_by FROM pesees WHERE 1=1'
            params = []
            
            if date_filter:
                query += ' AND date LIKE ?'
                params.append(f'%{date_filter}%')
            if product_filter:
                query += ' AND produit LIKE ?'
                params.append(f'%{product_filter}%')
            if lot_filter:
                query += ' AND n_lot LIKE ?'
                params.append(f'%{lot_filter}%')
            
            query += ' ORDER BY date DESC'
            
            rows = c.execute(query, params).fetchall()
            
            if not rows:
                consultation_table.rows.append(
                    ft.DataRow(
                        cells=[ft.DataCell(ft.Text("Aucune donnée disponible"))] * 5
                    )
                )
            else:
                for row in rows:
                    record_id = row[0]
                    date = str(row[1]) if row[1] else "-"
                    produit = str(row[2]) if row[2] else "-"
                    n_lot = str(row[3]) if row[3] else "-"
                    created_by = str(row[4]) if row[4] else "N/A"
                    
                    consultation_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(date)),
                                ft.DataCell(ft.Text(produit)),
                                ft.DataCell(ft.Text(n_lot)),
                                ft.DataCell(ft.Text(created_by)),
                                ft.DataCell(
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            icon_color=ft.Colors.BLUE,
                                            tooltip="Modifier",
                                            on_click=lambda e, id=record_id: edit_record(e, id)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color=ft.Colors.RED,
                                            tooltip="Supprimer",
                                            on_click=lambda e, rid=record_id: delete_record(e, rid)
                                        )
                                    ])
                                )
                            ]
                        )
                    )
                    
        except Exception as ex:
            print(f"Error loading data: {ex}")
            consultation_table.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(f"Erreur: {str(ex)}"))] * 5
                )
            )
        finally:
            conn.close()
            page.update()

    def delete_record(e, record_id):
        def confirm_delete(e):
            if e.control.text == "Oui":
                conn = sqlite3.connect('pesees.db')
                c = conn.cursor()
                c.execute('DELETE FROM pesees WHERE id = ?', (record_id,))
                conn.commit()
                conn.close()
                
                load_data()
                
                dialog.open = False
                page.snack_bar = ft.SnackBar(content=ft.Text("Enregistrement supprimé!"))
                page.snack_bar.open = True
                page.update()
            else:
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text("Voulez-vous vraiment supprimer cet enregistrement?"),
            actions=[
                ft.TextButton("Oui", on_click=confirm_delete),
                ft.TextButton("Non", on_click=confirm_delete),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def edit_record(e, record_id):
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            record = c.execute('SELECT * FROM pesees WHERE id = ?', (record_id,)).fetchone()
            conn.close()

            if record:
                page.client_storage.set("record_to_edit", record)
                page.go("/pesees")
                
        except Exception as ex:
            print(f"Error in edit_record: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Erreur lors de la modification"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()

    load_data()
    
    # Boutons d'action modernes
    refresh_button = ft.IconButton(
        icon=ft.Icons.REFRESH,  # Fix: uppercase Icons
        tooltip="Actualiser",
        icon_color=ft.Colors.WHITE,  # Fix: uppercase Colors
        on_click=lambda _: load_data()
    )

    search_toggle_button = ft.IconButton(
        icon=ft.Icons.SEARCH,  # Fix: uppercase Icons
        tooltip="Rechercher",
        icon_color=ft.Colors.WHITE,  # Fix: uppercase Colors
        on_click=toggle_search
    )

    add_button = ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(ft.Icons.ADD), ft.Text("Nouvel enregistrement")],
            spacing=5,
        ),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=theme["primary"],
            elevation=0,
            padding=15,
            animation_duration=200,
        ),
        on_click=lambda _: page.go("/pesees")
    )
    
    # Container principal responsive
    main_content = ft.ResponsiveRow([
        ft.Column(
            [
                search_container,
                ft.Container(
                    content=add_button,
                    alignment=ft.alignment.center_right,
                    padding=10
                ),
                ft.Card(
                    content=consultation_table,
                    elevation=0,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            col={"sm": 12, "md": 12, "xl": 12},
        ),
    ])

    return ft.View(
        "/consultation",
        [
            ft.AppBar(
                title=ft.Text(
                    "Liste des Pesées",
                    color=ft.Colors.WHITE,  # Fix: uppercase Colors
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=theme["primary"],
                actions=[
                    search_toggle_button,
                    refresh_button
                ],
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,  # Fix: uppercase Icons
                    icon_color=ft.Colors.WHITE,  # Fix: uppercase Colors
                    on_click=lambda _: page.go("/")
                ),
            ),
            ft.Container(
                content=main_content,
                padding=20,
                bgcolor=theme["background"],
                expand=True,
            ),
        ],
        bgcolor=theme["background"],
        padding=0,
        spacing=0,
    )