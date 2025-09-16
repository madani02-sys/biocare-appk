import flet as ft
import sqlite3
from datetime import datetime

def create_sheet_view(page: ft.Page, record_to_edit=None):
    # Input fields
    date_input = ft.TextField(
        label="Date",
        value=record_to_edit[1] if record_to_edit else datetime.now().strftime("%Y-%m-%d"),
        width=300
    )
    
    produit_input = ft.TextField(
        label="Produit",
        value=record_to_edit[2] if record_to_edit else "",
        width=300
    )
    
    lot_input = ft.TextField(
        label="Lot",
        value=record_to_edit[3] if record_to_edit else "",
        width=300
    )
    
    qte_input = ft.TextField(
        label="Quantité pesée caisse",
        value=str(record_to_edit[4]) if record_to_edit else "",
        width=300
    )
    
    anomalie_input = ft.TextField(
        label="Anomalie",
        value=record_to_edit[5] if record_to_edit else "",
        width=300,
        multiline=True
    )
    
    action_input = ft.TextField(
        label="Action corrective",
        value=record_to_edit[6] if record_to_edit else "",
        width=300,
        multiline=True
    )

    def save_sheet(e):
        try:
            if not all([date_input.value, produit_input.value, lot_input.value, qte_input.value]):
                page.show_snack_bar(ft.SnackBar(
                    content=ft.Text("Veuillez remplir tous les champs obligatoires!"),
                    bgcolor=ft.Colors.RED
                ))
                return

            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            
            if record_to_edit:
                c.execute('''UPDATE sheet 
                           SET date=?, produit=?, lot=?, qte_pesee_caisse=?,
                               anomalie=?, action_corrective=?
                           WHERE id=?''',
                         (date_input.value, produit_input.value, lot_input.value,
                          qte_input.value, anomalie_input.value, action_input.value,
                          record_to_edit[0]))
            else:
                c.execute('''INSERT INTO sheet 
                           (date, produit, lot, qte_pesee_caisse,
                            anomalie, action_corrective, created_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (date_input.value, produit_input.value, lot_input.value,
                          qte_input.value, anomalie_input.value, action_input.value,
                          page.client_storage.get("username")))

            conn.commit()
            conn.close()

            page.show_snack_bar(ft.SnackBar(
                content=ft.Text("Enregistrement réussi!"),
                bgcolor=ft.Colors.GREEN
            ))
            page.go("/consultation-sheet")  # Redirection vers la consultation
            
        except Exception as ex:
            print(f"Error saving sheet: {ex}")
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text("Erreur lors de l'enregistrement!"),
                bgcolor=ft.Colors.RED
            ))

    return ft.View(
        "/sheet",
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Formulaire Sheet", size=30, weight=ft.FontWeight.BOLD),
                        date_input,
                        produit_input,
                        lot_input,
                        qte_input,
                        anomalie_input,
                        action_input,
                        # Row avec les deux boutons côte à côte
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="Enregistrer",
                                    on_click=save_sheet,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.BLUE
                                    )
                                ),
                                ft.ElevatedButton(
                                    text="Consulter",
                                    on_click=lambda _: page.go("/consultation-sheet"),
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN
                                    )
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20
                        )
                    ],
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=50
            )
        ]
    )