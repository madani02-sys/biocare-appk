import flet as ft
import sqlite3
from datetime import datetime

def create_reception_view(page: ft.Page):
    # Get editing data from client storage
    editing_data = page.client_storage.get("reception_to_edit")
    print("Retrieved editing data:", editing_data)  # Debug print
    
    # Déterminer la largeur disponible
    def get_width():
        if hasattr(page, "window_width") and page.window_width:
            return page.window_width
        elif page.width:
            return page.width
        else:
            return 1200  # Valeur par défaut pour desktop
    
    # Déterminer si on est en mode mobile
    def is_mobile():
        width = get_width()
        return width < 768
    
    mobile = is_mobile()
    
    # Fonction helper pour créer des champs de saisie
    def create_field(label, value="", multiline=False, input_filter=None):
        field_width = get_width() - 40 if mobile else min(300, get_width()/2.5)
        
        return ft.TextField(
            label=label,
            value=value,
            width=field_width,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            input_filter=input_filter
        )
    
    # Input fields avec création responsive
    date_input = create_field(
        "Date",
        value=editing_data.get("date", datetime.now().strftime("%Y-%m-%d")) if editing_data else datetime.now().strftime("%Y-%m-%d")
    )
    heure_input = create_field(
        "Heure",
        value=editing_data.get("heure", datetime.now().strftime("%H:%M")) if editing_data else datetime.now().strftime("%H:%M")
    )
    article_input = create_field(
        "Article réceptionné",
        value=editing_data.get("article", "") if editing_data else ""
    )
    nature_input = create_field(
        "Nature d'article (MP/ADC/ADC/I/consommable)",
        value=editing_data.get("nature_article", "") if editing_data else ""
    )
    lot_input = create_field(
        "N° LOT",
        value=editing_data.get("n_lot", "") if editing_data else ""
    )
    dlc_input = create_field(
        "DLC",
        value=editing_data.get("dlc", "") if editing_data else ""
    )
    ddp_input = create_field(
        "DDP",
        value=editing_data.get("ddp", "") if editing_data else ""
    )
    quantite_input = create_field(
        "QTE réceptionnée",
        value=str(editing_data.get("quantite_receptionnee", "")) if editing_data else "",
        input_filter=ft.NumbersOnlyInputFilter()
    )
    
    # Dropdown responsive
    conformite_dropdown = ft.Dropdown(
        label="État de la réception",
        width=get_width() - 40 if mobile else min(300, get_width()/2.5),
        options=[
            ft.dropdown.Option("conforme"),
            ft.dropdown.Option("non conforme")
        ],
        value=editing_data.get("conformite", None) if editing_data else None
    )
    
    reference_input = create_field(
        "Référence",
        value=editing_data.get("reference", "") if editing_data else ""
    )
    anomalie_input = create_field(
        "Anomalie ou non-conformité",
        value=editing_data.get("anomalie", "") if editing_data else "",
        multiline=True
    )

    # Update page to show loaded values
    if editing_data:
        page.update()

    def save_record(e):
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            if editing_data and "id" in editing_data:
                # Update existing record with all fields
                c.execute('''
                    UPDATE controle_reception 
                    SET date=?, heure=?, article=?, nature_article=?, n_lot=?,
                        dlc=?, ddp=?, quantite_receptionnee=?, conformite=?,
                        non_conformite=?, reference=?, anomalie=?
                    WHERE id=?
                ''', (
                    date_input.value,
                    heure_input.value,
                    article_input.value,
                    nature_input.value,
                    lot_input.value,
                    dlc_input.value,
                    ddp_input.value,
                    quantite_input.value,
                    conformite_dropdown.value,
                    None,  # non_conformite
                    reference_input.value,
                    anomalie_input.value,
                    editing_data["id"]
                ))
            else:
                # Insert new record with all fields
                c.execute('''
                    INSERT INTO controle_reception 
                    (date, heure, article, nature_article, n_lot, dlc, ddp,
                     quantite_receptionnee, conformite, non_conformite,
                     reference, anomalie, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date_input.value,
                    heure_input.value,
                    article_input.value,
                    nature_input.value,
                    lot_input.value,
                    dlc_input.value,
                    ddp_input.value,
                    quantite_input.value,
                    conformite_dropdown.value,
                    None,  # non_conformite
                    reference_input.value,
                    anomalie_input.value,
                    page.client_storage.get("username", "Unknown")
                ))

            conn.commit()
            conn.close()

            # Clear editing data
            page.client_storage.remove("reception_to_edit")

            # Show success message and return to consultation view
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Enregistrement sauvegardé avec succès!")
            )
            page.snack_bar.open = True
            page.go("/consultation-reception")
            
        except Exception as ex:
            print(f"Error saving data: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erreur: {str(ex)}"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()

    # Créer la mise en page responsive
    def create_layout():
        nonlocal mobile
        mobile = is_mobile()
        
        if mobile:
            # Mise en page mobile (une seule colonne)
            return ft.Column(
                [
                    date_input, heure_input, article_input, nature_input,
                    lot_input, dlc_input, ddp_input, quantite_input,
                    conformite_dropdown, reference_input, anomalie_input
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        else:
            # Mise en page desktop (deux colonnes)
            return ft.Row(
                [
                    ft.Column(
                        [date_input, heure_input, article_input,
                         nature_input, lot_input, dlc_input],
                        spacing=10
                    ),
                    ft.Column(
                        [ddp_input, quantite_input, conformite_dropdown,
                         reference_input, anomalie_input],
                        spacing=10
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
    
    form_layout = create_layout()
    
    # Créer les boutons d'action responsive
    def create_buttons():
        nonlocal mobile
        button_width = (get_width() - 60) / 2 if mobile else None
        
        return ft.Row(
            [
                ft.ElevatedButton(
                    text="Sauvegarder",
                    on_click=save_record,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE,
                        padding=15
                    ),
                    width=button_width
                ),
                ft.ElevatedButton(
                    text="Consulter",
                    on_click=lambda _: page.go("/consultation-reception"),
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN,
                        padding=15
                    ),
                    width=button_width
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10 if mobile else 20
        )
    
    buttons_row = create_buttons()
    
    # Gestionnaire de redimensionnement
    def on_resize(e):
        nonlocal form_layout, buttons_row
        
        # Recréer la mise en page
        new_form_layout = create_layout()
        new_buttons_row = create_buttons()
        
        # Mettre à jour le titre
        content_column.controls[0].size = 24 if is_mobile() else 30
        
        # Remplacer les éléments dans la colonne principale
        content_column.controls[1] = new_form_layout
        content_column.controls[2] = new_buttons_row
        
        form_layout = new_form_layout
        buttons_row = new_buttons_row
        
        # Mettre à jour le padding du container
        main_container.padding = 10 if is_mobile() else 20
        
        page.update()
    
    # Enregistrer le gestionnaire de redimensionnement
    page.on_resize = on_resize
    
    # Créer la colonne de contenu principale
    content_column = ft.Column(
        [
            ft.Text(
                "Contrôle de Réception",
                size=24 if mobile else 30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            form_layout,
            buttons_row
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )
    
    main_container = ft.Container(
        content=content_column,
        padding=10 if mobile else 20,
        expand=True
    )
    
    return ft.View(
        "/reception",
        [main_container],
        scroll=ft.ScrollMode.AUTO
    )