import flet as ft

def create_home_view(page: ft.Page):
    username = page.client_storage.get("username")
    
    # Pour le mode desktop, nous devons utiliser page.window_width
    # Pour le mode web, nous utilisons page.width
    def get_width():
        if hasattr(page, "window_width") and page.window_width:
            return page.window_width
        elif page.width:
            return page.width
        else:
            return 1000  # Valeur par défaut pour desktop
    
    def is_mobile():
        width = get_width()
        return width < 768
    
    # Fonction pour créer une carte de menu responsive
    def create_card(icon, title, description, route, color, bg_color):
        mobile = is_mobile()
        card_width = get_width() - 40 if mobile else 300
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        name=icon,
                        size=40 if mobile else 50,
                        color=color
                    ),
                    ft.Text(
                        title,
                        size=18 if mobile else 20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        description,
                        size=14,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.ElevatedButton(
                        "Accéder",
                        on_click=lambda _, r=route: page.go(r),
                        style=ft.ButtonStyle(
                            padding=15,
                            bgcolor=color
                        ),
                        width=card_width - 40 if mobile else None
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10 if mobile else 15
            ),
            padding=15 if mobile else 20,
            bgcolor=bg_color,
            border_radius=10,
            width=card_width,
            margin=ft.margin.only(bottom=10) if mobile else ft.margin.all(10)
        )
    
    # Création des cartes
    pesees_card = create_card(
        ft.Icons.SCALE,
        "Gestion des Pesées",
        "Gérer les pesées et consultations",
        "/pesees",
        ft.Colors.BLUE,
        ft.Colors.BLUE_50
    )
    
    reception_card = create_card(
        ft.Icons.RECEIPT_LONG,
        "Contrôle de Réception",
        "Gérer les contrôles de réception",
        "/reception",
        ft.Colors.GREEN,
        ft.Colors.GREEN_50
    )
    
    sheet_card = create_card(
        ft.Icons.ASSIGNMENT,
        "Sheet",
        "Gérer les sheets",
        "/sheet",
        ft.Colors.ORANGE,
        ft.Colors.ORANGE_50
    )
    
    # Créer le layout en fonction de la taille
    mobile = is_mobile()
    
    if mobile:
        cards_layout = ft.Column(
            [
                pesees_card,
                reception_card,
                sheet_card
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    else:
        cards_layout = ft.Row(
            [
                pesees_card,
                reception_card,
                sheet_card
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            wrap=True
        )
    
    # Gérer le redimensionnement pour le mode desktop
    def on_resize(e):
        nonlocal cards_layout
        # Redétecter si on est en mode mobile
        mobile = is_mobile()
        
        # Recréer les cartes
        new_pesees_card = create_card(
            ft.Icons.SCALE,
            "Gestion des Pesées",
            "Gérer les pesées et consultations",
            "/pesees",
            ft.Colors.BLUE,
            ft.Colors.BLUE_50
        )
        
        new_reception_card = create_card(
            ft.Icons.RECEIPT_LONG,
            "Contrôle de Réception",
            "Gérer les contrôles de réception",
            "/reception",
            ft.Colors.GREEN,
            ft.Colors.GREEN_50
        )
        
        new_sheet_card = create_card(
            ft.Icons.ASSIGNMENT,
            "Sheet",
            "Gérer les sheets",
            "/sheet",
            ft.Colors.ORANGE,
            ft.Colors.ORANGE_50
        )
        
        # Créer le nouveau layout
        if mobile:
            new_layout = ft.Column(
                [
                    new_pesees_card,
                    new_reception_card,
                    new_sheet_card
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
        else:
            new_layout = ft.Row(
                [
                    new_pesees_card,
                    new_reception_card,
                    new_sheet_card
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                wrap=True
            )
        
        # Mettre à jour le layout et le titre
        content_column.controls[1] = new_layout
        content_column.controls[0].size = 24 if mobile else 32
        content_column.controls[0].update()
        cards_layout = new_layout
        
        # Mettre à jour le padding du container
        main_container.padding = 15 if mobile else 50
        main_container.update()
        
        page.update()
    
    # Enregistrer le gestionnaire de redimensionnement pour desktop
    page.on_resize = on_resize
    
    # Créer le contenu principal
    content_column = ft.Column(
        [
            ft.Text(
                f"Bienvenue {username}",
                size=24 if mobile else 32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            cards_layout
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )
    
    main_container = ft.Container(
        content=content_column,
        padding=15 if mobile else 50,
        expand=True
    )
    
    return ft.View(
        "/home",
        [
            main_container
        ],
        scroll=ft.ScrollMode.AUTO
    )