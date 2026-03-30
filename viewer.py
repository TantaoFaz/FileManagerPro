import subprocess, os

webview_proc = None

def open_webview(url):
    global webview_proc
    if webview_proc and webview_proc.poll() is None:
        with open(os.path.expanduser('~/.duckbusca_nav'), 'w') as f:
            f.write(url)
        return
    script = """
import gi, os
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, WebKit, GLib

NAV_FILE = os.path.expanduser('~/.duckbusca_nav')
webview = None

def check_nav():
    global webview
    if os.path.exists(NAV_FILE):
        with open(NAV_FILE) as f:
            url = f.read().strip()
        os.remove(NAV_FILE)
        if url and webview:
            GLib.idle_add(webview.load_uri, url)
    return True

def on_activate(app):
    global webview
    win = Gtk.ApplicationWindow(application=app)
    win.set_title('DuckBusca')
    win.set_default_size(1100, 780)
    webview = WebKit.WebView()
    webview.load_uri('__URL__')
    win.set_child(webview)
    win.present()
    GLib.timeout_add(500, check_nav)

app = Gtk.Application(application_id='com.duckbusca.viewer')
app.connect('activate', on_activate)
app.run()
""".replace('__URL__', url)
    env = {**os.environ, 'DISPLAY': ':0'}
    webview_proc = subprocess.Popen(['python3', '-c', script], env=env)
