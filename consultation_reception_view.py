import flet as ft
import sqlite3

def create_consultation_reception_view(page: ft.Page):
    try:
        # Check if mobile view
        def is_mobile():
            return page.width < 850

        def create_data_table():
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Date", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Heure", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Article", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Nature", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("N° LOT", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("DLC", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("DDP", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Quantité", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Conformité", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Référence", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Anomalie", size=14, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Actions", size=14, weight=ft.FontWeight.BOLD))
                ],
                border=ft.border.all(2, ft.Colors.BLUE_100),
                border_radius=8,
                column_spacing=40,
                heading_row_height=60,
                heading_row_color=ft.Colors.BLUE_50,
                data_row_max_height=100,
                data_row_min_height=50,
                show_checkbox_column=False,
            )

        def create_mobile_card(record):
            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.CALENDAR_TODAY),
                            title=ft.Text(f"Date: {record[1]}", weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"Heure: {record[2]}"),
                        ),
                        ft.Divider(height=1),
                        ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Text(f"Article: {record[3]}", size=14),
                                ft.Text(f"Nature: {record[4]}", size=14),
                                ft.Text(f"N° LOT: {record[5]}", size=14),
                                ft.Text(f"DLC: {record[6]}", size=14),
                                ft.Text(f"DDP: {record[7]}", size=14),
                                ft.Text(f"Quantité: {record[8]}", size=14),
                                ft.Text(f"Conformité: {record[9]}", size=14),
                                ft.Text(f"Référence: {record[10]}", size=14),
                                ft.Text(f"Anomalie: {record[11]}", size=14),
                            ]),
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    icon_color=ft.Colors.BLUE,
                                    tooltip="Modifier",
                                    on_click=lambda e, id=record[0]: edit_record(e, id)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED,
                                    tooltip="Supprimer",
                                    on_click=lambda e, id=record[0]: delete_record(e, id)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END
                        )
                    ]),
                    padding=10
                ),
                elevation=2,
                margin=10
            )

        # Create containers for both views
        desktop_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        mobile_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        consultation_table = create_data_table()

        def load_data():
            try:
                mobile = is_mobile()
                if mobile:
                    mobile_view.controls.clear()
                else:
                    consultation_table.rows.clear()

                conn = sqlite3.connect('pesees.db')
                c = conn.cursor()
                rows = c.execute('''
                    SELECT id, date, heure, article, nature_article, n_lot, 
                           dlc, ddp, quantite_receptionnee, conformite, 
                           reference, anomalie 
                    FROM controle_reception 
                    ORDER BY date DESC
                ''').fetchall()

                if not rows:
                    if mobile:
                        mobile_view.controls.append(
                            ft.Text("Aucune donnée disponible", 
                                  style=ft.TextThemeStyle.BODY_LARGE)
                        )
                    else:
                        consultation_table.rows.append(
                            ft.DataRow(
                                cells=[ft.DataCell(ft.Text("Aucune donnée disponible"))] * 12
                            )
                        )
                else:
                    if mobile:
                        for row in rows:
                            mobile_view.controls.append(create_mobile_card(row))
                    else:
                        for row in rows:
                            consultation_table.rows.append(
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(str(row[1]))),
                                        ft.DataCell(ft.Text(str(row[2]))),
                                        ft.DataCell(ft.Text(str(row[3]))),
                                        ft.DataCell(ft.Text(str(row[4]))),
                                        ft.DataCell(ft.Text(str(row[5]))),
                                        ft.DataCell(ft.Text(str(row[6]))),
                                        ft.DataCell(ft.Text(str(row[7]))),
                                        ft.DataCell(ft.Text(str(row[8]))),
                                        ft.DataCell(ft.Text(str(row[9]))),
                                        ft.DataCell(ft.Text(str(row[10]))),
                                        ft.DataCell(ft.Text(str(row[11]))),
                                        ft.DataCell(create_action_buttons(row[0]))
                                    ]
                                )
                            )
            except Exception as ex:
                print(f"Error loading data: {ex}")
            finally:
                if 'conn' in locals():
                    conn.close()
                page.update()

        def create_action_buttons(record_id):
            return ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color=ft.Colors.BLUE,  # Changed from ft.colors.BLUE
                        tooltip="Modifier",
                        on_click=lambda e, id=record_id: edit_record(e, id)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,   # Changed from ft.colors.RED
                        tooltip="Supprimer",
                        on_click=lambda e, id=record_id: delete_record(e, id)
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )

        def edit_record(e, record_id):
            try:
                conn = sqlite3.connect('pesees.db')
                c = conn.cursor()
                record = c.execute('SELECT * FROM controle_reception WHERE id = ?', (record_id,)).fetchone()
                conn.close()

                if record:
                    # Convert tuple to dictionary with all fields
                    record_dict = {
                        "id": record[0],
                        "date": record[1],
                        "heure": record[2],
                        "article": record[3],
                        "nature_article": record[4],
                        "n_lot": record[5],
                        "dlc": record[6],
                        "ddp": record[7],
                        "quantite_receptionnee": record[8],
                        "conformite": record[9],
                        "non_conformite": record[10],
                        "reference": record[11],
                        "anomalie": record[12],
                        "created_by": record[13] if len(record) > 13 else None
                    }
                    
                    # Store dictionary in client storage
                    page.client_storage.set("reception_to_edit", record_dict)
                    print("Stored data for editing:", record_dict)  # Debug print
                    page.go("/reception")
                else:
                    print("Record not found:", record_id)
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Enregistrement non trouvé"),
                        bgcolor=ft.Colors.RED
                    )
                    page.snack_bar.open = True
                    page.update()
                    
            except Exception as ex:
                print(f"Error editing record: {ex}")
                import traceback
                traceback.print_exc()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Erreur lors de la modification: {str(ex)}"),
                    bgcolor=ft.Colors.RED   # Changed from ft.colors.RED
                )
                page.snack_bar.open = True
                page.update()

        def delete_record(e, record_id):
            def confirm_delete(e):
                if e.control.text == "Oui":
                    try:
                        conn = sqlite3.connect('pesees.db')
                        c = conn.cursor()
                        c.execute('DELETE FROM controle_reception WHERE id = ?', (record_id,))
                        conn.commit()
                        conn.close()
                        load_data()
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Enregistrement supprimé avec succès!"),
                            bgcolor=ft.Colors.GREEN
                        )
                        page.snack_bar.open = True
                    except Exception as ex:
                        print(f"Error deleting record: {ex}")
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Erreur lors de la suppression"),
                            bgcolor=ft.Colors.RED
                        )
                        page.snack_bar.open = True
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmer la suppression"),
                content=ft.Text("Voulez-vous vraiment supprimer cet enregistrement?"),
                actions=[
                    ft.TextButton("Oui", on_click=confirm_delete),
                    ft.TextButton("Non", on_click=confirm_delete),
                ],
            )
            page.dialog = dialog
            dialog.open = True
            page.update()

        # Load initial data
        load_data()

        # Create header with title and new button
        header = ft.Row(
            [
                ft.Text(
                    "Consultation des Réceptions",
                    size=30 if not is_mobile() else 20,
                    weight=ft.FontWeight.BOLD
                ),
                ft.ElevatedButton(
                    "Nouvelle Réception",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: page.go("/reception"),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE,   # Changed from ft.colors.BLUE
                        color=ft.Colors.WHITE,    # Changed from ft.colors.WHITE
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        def create_view_content():
            if is_mobile():
                return ft.Column(
                    [header, mobile_view],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                )
            else:
                return ft.Column(
                    [
                        header,
                        ft.Container(
                            content=consultation_table,
                            border=ft.border.all(2, ft.Colors.BLUE_100),
                            border_radius=10,
                            padding=10,
                            expand=True
                        )
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO
                )

        # Handle page resize
        def on_resize(e):
            view_content.content = create_view_content()
            page.update()

        page.on_resize = on_resize
        view_content = ft.Container(
            content=create_view_content(),
            expand=True,
            padding=20
        )

        return ft.View(
            "/consultation-reception",
            [
                ft.Container(
                    content=create_view_content(),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    expand=True
                )
            ],
            padding=0,
            spacing=0
        )

    except Exception as ex:
        print(f"Error creating consultation view: {ex}")
        return ft.View(
            "/consultation-reception",
            [ft.Text(f"Error loading consultation view: {str(ex)}")]
        )