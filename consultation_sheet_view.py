import flet as ft
import sqlite3

def create_consultation_sheet_view(page: ft.Page):
    # Table pour afficher les données
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Produit")),
            ft.DataColumn(ft.Text("Lot")),
            ft.DataColumn(ft.Text("Quantité")),
            ft.DataColumn(ft.Text("Anomalie")),
            ft.DataColumn(ft.Text("Action Corrective")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[]
    )

    def load_data():
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            c.execute('SELECT * FROM sheet ORDER BY date DESC')
            records = c.fetchall()
            conn.close()

            data_table.rows.clear()
            
            for record in records:
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(record[1])),  # Date
                            ft.DataCell(ft.Text(record[2])),  # Produit
                            ft.DataCell(ft.Text(record[3])),  # Lot
                            ft.DataCell(ft.Text(str(record[4]))),  # Quantité
                            ft.DataCell(ft.Text(record[5] or "")),  # Anomalie
                            ft.DataCell(ft.Text(record[6] or "")),  # Action Corrective
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            tooltip="Modifier",
                                            on_click=lambda e, id=record[0]: edit_record(e, id)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            tooltip="Supprimer",
                                            on_click=lambda e, id=record[0]: delete_record(e, id)
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                )
            
            page.update()
            
        except Exception as e:
            print(f"Error loading data: {e}")

    def edit_record(e, id):
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            c.execute('SELECT * FROM sheet WHERE id = ?', (id,))
            record = c.fetchone()
            conn.close()

            page.client_storage.set("sheet_to_edit", record)
            page.go("/sheet")
            
        except Exception as e:
            print(f"Error editing record: {e}")

    def delete_record(e, id):
        try:
            conn = sqlite3.connect('pesees.db')
            c = conn.cursor()
            c.execute('DELETE FROM sheet WHERE id = ?', (id,))
            conn.commit()
            conn.close()

            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Enregistrement supprimé avec succès!"),
                    bgcolor=ft.Colors.GREEN
                )
            )
            load_data()
            
        except Exception as e:
            print(f"Error deleting record: {e}")
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Erreur lors de la suppression!"),
                    bgcolor=ft.Colors.RED
                )
            )

    # Charger les données initiales
    load_data()

    return ft.View(
        "/consultation-sheet",
        [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Consultation des Sheets", 
                                       size=30, 
                                       weight=ft.FontWeight.BOLD),
                                ft.ElevatedButton(
                                    "Nouveau Sheet",
                                    on_click=lambda _: page.go("/sheet")
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        # Wrap the data table in a Column instead of Container
                        ft.Column(
                            [data_table],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True
                        )
                    ]
                ),
                padding=20
            )
        ],
        scroll=ft.ScrollMode.AUTO  # Move scroll property to View
    )