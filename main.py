import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from android.runnable import run_on_ui_thread
import urllib.parse, json
from search import search_ddg

try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    ANDROID = True
except:
    ANDROID = False

Window.clearcolor = (0.047, 0.047, 0.043, 1)

class DuckBuscaApp(App):
    def build(self):
        if ANDROID:
            request_permissions([Permission.INTERNET])
        self.results = []
        self.webview = None

        root = BoxLayout(orientation='vertical', spacing=0)

        # Topbar
        topbar = BoxLayout(
            size_hint_y=None, height='52dp',
            padding=['8dp', '6dp', '8dp', '6dp'],
            spacing='6dp'
        )
        topbar.canvas.before.clear()
        with topbar.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.082, 0.082, 0.078, 1)
            self.topbar_rect = Rectangle(pos=topbar.pos, size=topbar.size)
        topbar.bind(pos=self._update_topbar, size=self._update_topbar)

        self.search_input = TextInput(
            hint_text='pesquisar...',
            multiline=False,
            background_color=(0.047, 0.047, 0.043, 1),
            foreground_color=(0.886, 0.874, 0.839, 1),
            hint_text_color=(0.42, 0.412, 0.376, 1),
            cursor_color=(0.831, 0.725, 0.416, 1),
            font_name='Roboto',
            font_size='14sp',
            padding=['12dp', '10dp'],
        )
        self.search_input.bind(on_text_validate=lambda x: self.do_search(1))

        btn = Button(
            text='→',
            size_hint_x=None, width='52dp',
            background_color=(0.831, 0.725, 0.416, 1),
            color=(0.047, 0.047, 0.043, 1),
            font_size='18sp',
            bold=True,
        )
        btn.bind(on_press=lambda x: self.do_search(1))

        topbar.add_widget(self.search_input)
        topbar.add_widget(btn)

        # Scroll de resultados
        self.scroll = ScrollView()
        self.results_layout = GridLayout(
            cols=1, spacing=0,
            size_hint_y=None, padding=['12dp', '8dp', '12dp', '8dp']
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.scroll.add_widget(self.results_layout)

        root.add_widget(topbar)
        root.add_widget(self.scroll)
        return root

    def _update_topbar(self, instance, value):
        self.topbar_rect.pos = instance.pos
        self.topbar_rect.size = instance.size

    def do_search(self, page):
        q = self.search_input.text.strip()
        if not q:
            return
        self.results_layout.clear_widgets()
        self._add_label('buscando...', color=(0.831, 0.725, 0.416, 1))
        threading.Thread(target=self._fetch, args=(q, page), daemon=True).start()

    def _fetch(self, q, page):
        try:
            items = search_ddg(q, page)
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._render(items, page))
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._add_label(f'Erro: {e}'))

    def _render(self, items, page):
        self.results_layout.clear_widgets()
        if not items:
            self._add_label('Sem resultados.')
            return
        self._add_label(f'{len(items)} resultados — página {page}',
                       color=(0.42, 0.412, 0.376, 1), size='12sp')
        for x in items:
            self._add_result(x)
        # Paginação
        pag = BoxLayout(size_hint_y=None, height='40dp', spacing='6dp', padding=['0dp','6dp'])
        for n in [page-1, page, page+1, page+2]:
            if n < 1:
                continue
            b = Button(
                text=str(n),
                size_hint_x=None, width='36dp',
                background_color=(0.831, 0.725, 0.416, 1) if n == page else (0.082, 0.082, 0.078, 1),
                color=(0.047, 0.047, 0.043, 1) if n == page else (0.42, 0.412, 0.376, 1),
                font_size='12sp',
            )
            b.bind(on_press=lambda x, p=n: self.do_search(p))
            pag.add_widget(b)
        self.results_layout.add_widget(pag)

    def _add_result(self, x):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=['4dp', '8dp', '4dp', '10dp'],
            spacing='3dp',
        )
        try:
            domain = urllib.parse.urlparse(x['url']).netloc.replace('www.', '')
        except:
            domain = x['url']

        domain_lbl = Label(
            text=domain,
            color=(0.482, 0.749, 0.627, 1),
            font_size='11sp',
            size_hint_y=None, height='16dp',
            halign='left', valign='middle',
            text_size=(Window.width - 24, None),
        )
        title_lbl = Label(
            text=x['title'],
            color=(0.886, 0.874, 0.839, 1),
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            halign='left', valign='top',
            text_size=(Window.width - 24, None),
        )
        title_lbl.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))

        card.add_widget(domain_lbl)
        card.add_widget(title_lbl)

        if x.get('description'):
            desc_lbl = Label(
                text=x['description'],
                color=(0.42, 0.412, 0.376, 1),
                font_size='12sp',
                size_hint_y=None,
                halign='left', valign='top',
                text_size=(Window.width - 24, None),
            )
            desc_lbl.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))
            card.add_widget(desc_lbl)

        actions = BoxLayout(size_hint_y=None, height='30dp', spacing='6dp')
        btn_open = Button(
            text='abrir',
            font_size='11sp',
            size_hint_x=None, width='60dp',
            background_color=(0.082, 0.082, 0.078, 1),
            color=(0.831, 0.725, 0.416, 1),
        )
        btn_open.bind(on_press=lambda x, u=x['url']: self.open_url(u))
        actions.add_widget(btn_open)
        card.add_widget(actions)

        card.bind(minimum_height=card.setter('height'))
        self.results_layout.add_widget(card)

        from kivy.graphics import Color, Line
        with self.results_layout.canvas.after:
            Color(0.145, 0.145, 0.137, 1)

    def _add_label(self, text, color=(0.42, 0.412, 0.376, 1), size='13sp'):
        lbl = Label(
            text=text,
            color=color,
            font_size=size,
            size_hint_y=None, height='40dp',
            halign='center',
        )
        self.results_layout.add_widget(lbl)

    def open_url(self, url):
        if ANDROID:
            self._open_android_webview(url)
        else:
            import webbrowser
            webbrowser.open(url)

    @run_on_ui_thread
    def _open_android_webview(self, url):
        activity = PythonActivity.mActivity
        wv = WebView(activity)
        wv.getSettings().setJavaScriptEnabled(True)
        wv.getSettings().setDomStorageEnabled(True)
        wv.getSettings().setLoadWithOverviewMode(True)
        wv.getSettings().setUseWideViewPort(True)
        wv.getSettings().setBuiltInZoomControls(True)
        wv.getSettings().setDisplayZoomControls(False)
        wv.setWebViewClient(WebViewClient())
        wv.loadUrl(url)
        activity.setContentView(wv)
        self.webview = wv

if __name__ == '__main__':
    DuckBuscaApp().run()
