from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, Static
from textual.screen import Screen
from textual.binding import Binding
import httpx
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

API_URL = "http://localhost:8001"
AUTH_PAGE = "http://localhost:8001/auth"

class AuthHandler(BaseHTTPRequestHandler):
    token_data = None

    def do_POST(self):
        if self.path == '/callback':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            AuthHandler.token_data = data

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🔐 Autenticación requerida", classes="title"),
            Static(""),
            Static("Haz clic en el botón para abrir el navegador y autenticarte", classes="info"),
            Static(""),
            Button("Abrir navegador para login", variant="primary", id="login_btn"),
            Static(""),
            Label("", id="status"),
            classes="login-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_btn":
            self.authenticate()

    def authenticate(self):
        status_label = self.query_one("#status", Label)
        status_label.update("Iniciando servidor de autenticación...")

        # Iniciar servidor HTTP temporal en un thread
        callback_port = 8888
        server = HTTPServer(('localhost', callback_port), AuthHandler)

        def run_server():
            server.handle_request()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

        # Abrir navegador
        auth_url = f"{API_URL}/../auth_page.html?callback_port={callback_port}"
        # Construir ruta al archivo HTML local
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api', 'auth_page.html')
        webbrowser.open(f'file://{html_path}?callback_port={callback_port}')

        status_label.update("Navegador abierto. Esperando autenticación...")

        # Esperar token
        def check_token():
            import time
            timeout = 120  # 2 minutos
            start_time = time.time()

            while AuthHandler.token_data is None:
                time.sleep(0.5)
                if time.time() - start_time > timeout:
                    self.app.call_from_thread(status_label.update, "Timeout: Inténtalo de nuevo")
                    return

            # Token recibido
            self.app.token = AuthHandler.token_data['token']
            self.app.username = AuthHandler.token_data['username']
            self.app.call_from_thread(self.app.pop_screen)

        token_thread = threading.Thread(target=check_token, daemon=True)
        token_thread.start()


class ItemForm(Screen):
    def __init__(self, item=None, on_save=None):
        super().__init__()
        self.item = item
        self.on_save_callback = on_save

    def compose(self) -> ComposeResult:
        title = "Editar Item" if self.item else "Nuevo Item"
        yield Header()
        yield Container(
            Static(f"📝 {title}", classes="title"),
            Static(""),
            Label("Nombre:"),
            Input(placeholder="Nombre del item", id="name_input",
                  value=self.item.get('name', '') if self.item else ''),
            Static(""),
            Label("Descripción:"),
            Input(placeholder="Descripción del item", id="desc_input",
                  value=self.item.get('description', '') if self.item else ''),
            Static(""),
            Label("Precio:"),
            Input(placeholder="Precio", id="price_input",
                  value=str(self.item.get('price', '')) if self.item else ''),
            Static(""),
            Horizontal(
                Button("Guardar", variant="primary", id="save_btn"),
                Button("Cancelar", variant="default", id="cancel_btn"),
            ),
            Static(""),
            Label("", id="form_status"),
            classes="form-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_btn":
            self.save_item()
        elif event.button.id == "cancel_btn":
            self.app.pop_screen()

    async def save_item(self):
        name = self.query_one("#name_input", Input).value
        description = self.query_one("#desc_input", Input).value
        price_str = self.query_one("#price_input", Input).value
        status_label = self.query_one("#form_status", Label)

        try:
            price = float(price_str)
        except ValueError:
            status_label.update("Error: Precio inválido")
            return

        if not name or not description:
            status_label.update("Error: Completa todos los campos")
            return

        data = {
            "name": name,
            "description": description,
            "price": price
        }

        headers = {"Authorization": f"Bearer {self.app.token}"}

        try:
            async with httpx.AsyncClient() as client:
                if self.item:
                    # Actualizar
                    response = await client.put(
                        f"{API_URL}/items/{self.item['id']}",
                        json=data,
                        headers=headers
                    )
                else:
                    # Crear
                    response = await client.post(
                        f"{API_URL}/items",
                        json=data,
                        headers=headers
                    )

                if response.status_code in [200, 201]:
                    if self.on_save_callback:
                        self.on_save_callback()
                    self.app.pop_screen()
                else:
                    status_label.update(f"Error: {response.text}")
        except Exception as e:
            status_label.update(f"Error de conexión: {str(e)}")


class CRUDApp(App):
    CSS = """
    .login-container, .form-container {
        width: 60;
        height: auto;
        margin: 2 4;
        padding: 2;
        border: solid $primary;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $accent;
    }

    .info {
        text-align: center;
        color: $text-muted;
    }

    DataTable {
        height: 1fr;
    }

    #actions {
        height: auto;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }

    Input {
        margin: 0 1;
    }

    #form_status, #status {
        text-align: center;
        color: $warning;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Salir"),
        Binding("r", "refresh", "Actualizar"),
        Binding("n", "new", "Nuevo"),
    ]

    def __init__(self):
        super().__init__()
        self.token = None
        self.username = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            DataTable(id="items_table"),
            Horizontal(
                Button("Nuevo", variant="success", id="new_btn"),
                Button("Editar", variant="primary", id="edit_btn"),
                Button("Eliminar", variant="error", id="delete_btn"),
                Button("Actualizar", variant="default", id="refresh_btn"),
                id="actions"
            ),
            Static("", id="main_status"),
        )
        yield Footer()

    def on_mount(self) -> None:
        if not self.token:
            self.push_screen(LoginScreen())
        else:
            self.load_items()

    def on_screen_resume(self) -> None:
        if self.token:
            self.load_items()

    async def load_items(self):
        table = self.query_one("#items_table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Nombre", "Descripción", "Precio")

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/items", headers=headers)

                if response.status_code == 200:
                    items = response.json()
                    for item in items:
                        table.add_row(
                            str(item['id']),
                            item['name'],
                            item['description'],
                            f"${item['price']:.2f}"
                        )
                    self.query_one("#main_status", Static).update(
                        f"✓ {len(items)} items cargados | Usuario: {self.username}"
                    )
                else:
                    self.query_one("#main_status", Static).update(
                        f"Error al cargar items: {response.status_code}"
                    )
        except Exception as e:
            self.query_one("#main_status", Static).update(f"Error: {str(e)}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new_btn":
            self.action_new()
        elif event.button.id == "edit_btn":
            self.edit_selected()
        elif event.button.id == "delete_btn":
            self.delete_selected()
        elif event.button.id == "refresh_btn":
            self.action_refresh()

    def action_new(self) -> None:
        self.push_screen(ItemForm(on_save=lambda: None))

    def action_refresh(self) -> None:
        self.load_items()

    async def edit_selected(self):
        table = self.query_one("#items_table", DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            item_id = row[0]

            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/items/{item_id}", headers=headers)
                if response.status_code == 200:
                    item = response.json()
                    self.push_screen(ItemForm(item=item, on_save=lambda: None))

    async def delete_selected(self):
        table = self.query_one("#items_table", DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            item_id = row[0]

            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{API_URL}/items/{item_id}", headers=headers)
                if response.status_code == 200:
                    self.load_items()
                    self.query_one("#main_status", Static).update(f"✓ Item {item_id} eliminado")

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = CRUDApp()
    app.run()
