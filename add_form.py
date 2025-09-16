import flet as ft
import sqlite3
from datetime import datetime

def create_add_view(page: ft.Page, record_to_edit=None):
    # Utiliser la largeur actuelle de la fenêtre ou la largeur de page
    window_width = page.window_width if hasattr(page, "window_width") else page.width
    is_mobile = window_width < 768 if window_width else False
    
    # Pour les tests en mode développement
    print(f"Window width: {window_width}, Is mobile: {is_mobile}")

    def create_input_field(label, value="", multiline=False):
        # Calculer la largeur adaptative
        field_width = window_width - 40 if is_mobile else min(300, window_width/2.5 if window_width else 300)
        
        return ft.TextField(
            label=label,
            value=value,
            width=field_width,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            text_size=14 if is_mobile else 16
        )

    # Création des champs avec la fonction helper
    date_input = create_input_field(
        "Date",
        record_to_edit[1] if record_to_edit else datetime.now().strftime("%Y-%m-%d")
    )
    produit_input = create_input_field(
        "Produit",
        record_to_edit[2] if record_to_edit else ""
    )
    lot_input = create_input_field(
        "N LOT",
        record_to_edit[3] if record_to_edit else ""
    )
    ddf_input = create_input_field(
        "DDF",
        record_to_edit[4] if record_to_edit else ""
    )
    ddp_input = create_input_field(
        "DDP",
        record_to_edit[5] if record_to_edit else ""
    )
    nb_caisses_input = create_input_field(
        "Nombre des caisses pesées",
        str(record_to_edit[6]) if record_to_edit else ""
    )
    intervalle_input = create_input_field(
        "Intervalle de la pesée",
        record_to_edit[7] if record_to_edit else ""
    )
    nb_conformes_input = create_input_field(
        "Nombre des caisses conformes",
        str(record_to_edit[8]) if record_to_edit else ""
    )
    nb_non_conformes_input = create_input_field(
        "Nombre des caisses non conforme",
        str(record_to_edit[9]) if record_to_edit else ""
    )
    numero_non_conforme_input = create_input_field(
        "Numéro de la caisse non-conforme",
        record_to_edit[10] if record_to_edit else ""
    )
    anomalie_input = create_input_field(
        "Anomalie observée",
        record_to_edit[11] if record_to_edit else "",
        multiline=True
    )

    def save_record(e):
        try:
            # Validation
            if not all([
                date_input.value,
                produit_input.value,
                lot_input.value
            ]):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Veuillez remplir au moins les champs obligatoires!"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
                return

            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            # Récupérer le nom d'utilisateur connecté
            try:
                username = page.client_storage.get("username")
                if username is None:
                    username = "Inconnu"
            except:
                username = "Inconnu"
            
            if record_to_edit:
                # Update existing record
                c.execute('''UPDATE pesees 
                            SET date=?, produit=?, n_lot=?, ddf=?, ddp=?,
                                nb_caisses_pesees=?, intervalle_pesee=?,
                                nb_caisses_conformes=?, nb_caisses_non_conformes=?,
                                numero_caisse_non_conforme=?, anomalie_observee=?,
                                created_by=?
                            WHERE id=?''',
                         (date_input.value, produit_input.value, lot_input.value,
                          ddf_input.value, ddp_input.value, nb_caisses_input.value,
                          intervalle_input.value, nb_conformes_input.value,
                          nb_non_conformes_input.value, numero_non_conforme_input.value,
                          anomalie_input.value, username, record_to_edit[0]))
            else:
                # Insert new record - ASSUREZ-VOUS QUE TOUTES LES COLONNES SONT SPÉCIFIÉES
                c.execute('''INSERT INTO pesees 
                            (date, produit, n_lot, ddf, ddp, nb_caisses_pesees,
                             intervalle_pesee, nb_caisses_conformes, nb_caisses_non_conformes,
                             numero_caisse_non_conforme, anomalie_observee, created_by)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (date_input.value, produit_input.value, lot_input.value,
                          ddf_input.value, ddp_input.value, nb_caisses_input.value,
                          intervalle_input.value, nb_conformes_input.value,
                          nb_non_conformes_input.value, numero_non_conforme_input.value,
                          anomalie_input.value, username))

            conn.commit()
            conn.close()

            # Show success message
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Enregistrement sauvegardé avec succès!"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
            page.go("/consultation")  # Rediriger vers la consultation après sauvegarde
            
        except Exception as ex:
            print(f"Error saving record: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erreur lors de la sauvegarde: {str(ex)}"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()

    # Créer un container responsive pour le formulaire
    def create_form_container():
        nonlocal is_mobile
        # Recalculer si on est en mode mobile
        window_width = page.window_width if hasattr(page, "window_width") else page.width
        is_mobile = window_width < 768 if window_width else False
        
        # Disposition responsive
        if is_mobile:
            return ft.Column(
                [
                    date_input, produit_input, lot_input,
                    ddf_input, ddp_input, nb_caisses_input,
                    intervalle_input, nb_conformes_input,
                    nb_non_conformes_input, numero_non_conforme_input,
                    anomalie_input
                ],
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            )
        else:
            return ft.Row(
                [
                    ft.Column(
                        [date_input, produit_input, lot_input,
                         ddf_input, ddp_input, nb_caisses_input],
                        spacing=10
                    ),
                    ft.Column(
                        [intervalle_input, nb_conformes_input,
                         nb_non_conformes_input, numero_non_conforme_input,
                         anomalie_input],
                        spacing=10
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )

    # Créer le contenu initial
    form_container = create_form_container()

    # Fonction pour gérer le redimensionnement
    def on_resize(e):
        nonlocal form_container
        # Recréer le conteneur du formulaire
        new_form_container = create_form_container()
        # Remplacer l'ancien conteneur
        page_content.controls[1] = new_form_container
        form_container = new_form_container
        page.update()

    # Créer le contenu principal de la page
    page_content = ft.Column(
        [
            ft.Text(
                "Gestion des Pesées",
                size=22 if is_mobile else 30,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            form_container,
            ft.Row(
                [
                    ft.ElevatedButton(
                        text="Sauvegarder",
                        on_click=save_record,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE,
                            padding=15
                        ),
                        width=window_width/2 - 30 if is_mobile else None
                    ),
                    ft.ElevatedButton(
                        text="Consulter",
                        on_click=lambda _: page.go("/consultation"),
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN,
                            padding=15
                        ),
                        width=window_width/2 - 30 if is_mobile else None
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10 if is_mobile else 20
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    # Enregistrer l'événement de redimensionnement
    page.on_resize = on_resize

    return ft.View(
        "/",
        [
            ft.Container(
                content=page_content,
                padding=10 if is_mobile else 20,
                expand=True
            )
        ],
        scroll=ft.ScrollMode.AUTO
    )