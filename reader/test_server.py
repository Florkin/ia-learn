"""Checks for the web reader: what it serves, what it refuses, how it renders. Run: python3 -m unittest

One check compares the renderer with markdown-it-py on every file of the course. It is skipped when
that library is missing: uv run --with markdown-it-py python -m unittest
"""

import re
import threading
import unittest
import unittest.mock
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import server

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None


def get(path):
    status, _, body = server.respond(path)
    return status, body.decode("utf-8")


class Catalogue(unittest.TestCase):
    def test_modules_follow_the_readme_table(self):
        modules = server.load_modules()
        on_disk = sorted(d.name for d in server.MODULES.iterdir() if (d / "LESSON.md").exists())
        self.assertEqual([m.slug for m in modules], on_disk)
        first = modules[0]
        self.assertEqual((first.number, first.title, first.duration, first.group), ("01", "Premier appel", "30 min", "Parler à un modèle"))
        self.assertEqual(modules[-1].group, "Entraîner")

    def test_a_folder_missing_from_the_table_is_still_listed(self):
        table = "| | **Bloc** | | |\n| 01 | [Premier appel](modules/01-first-call/LESSON.md) | Résumé | 30 min |\n"
        modules = server.load_modules(table)
        self.assertEqual(len(modules), len(server.load_modules()))
        self.assertEqual(modules[0].group, "Bloc")
        extra = modules[1]
        self.assertEqual((extra.slug, extra.title, extra.group), ("02-generation-settings", "Régler la génération", "Autres modules"))


class Pages(unittest.TestCase):
    def test_index_lists_every_module_under_its_group(self):
        status, page = get("/")
        self.assertEqual(status, 200)
        self.assertEqual(re.findall(r'href="/modules/([\w-]+)"', page), [m.slug for m in server.load_modules()])
        for expected in ("<h2>Parler à un modèle</h2>", "<h2>Entraîner</h2>", "<b>Premier appel</b>", "30 min", 'href="/guide"'):
            self.assertIn(expected, page)

    def test_lesson_page_has_title_sections_and_navigation(self):
        status, page = get("/modules/02-generation-settings")
        self.assertEqual(status, 200)
        self.assertIn("<h1>02 · Régler la génération</h1>", page)
        self.assertIn("<title>02 · Régler la génération · IA Learn</title>", page)
        self.assertIn("<h2>Objectif</h2>", page)
        self.assertIn("Durée : 35 min", page)
        self.assertIn("<pre><code>0    The Cozy Beanery", page)
        for link in ('href="/"', 'href="/modules/01-first-call"', 'href="/modules/03-structured-output"', 'href="/modules/02-generation-settings/deeper"'):
            self.assertIn(link, page)

    def test_trailing_slash_and_query_string_are_accepted(self):
        self.assertEqual(get("/modules/02-generation-settings/")[0], 200)
        self.assertEqual(get("/modules/02-generation-settings?from=dashboard")[0], 200)

    def test_first_module_has_no_previous_and_last_has_no_next(self):
        modules = server.load_modules()
        first, last = get(f"/modules/{modules[0].slug}")[1], get(f"/modules/{modules[-1].slug}")[1]
        self.assertIn(f'href="/modules/{modules[1].slug}"', first)
        self.assertIn(f'href="/modules/{modules[-2].slug}"', last)
        self.assertEqual((first.count('aria-disabled="true"'), last.count('aria-disabled="true"')), (1, 1))

    def test_deeper_page_links_back_to_its_lesson(self):
        status, page = get("/modules/04-embeddings/deeper")
        self.assertEqual(status, 200)
        self.assertIn("<h1>04 · Pour aller plus loin</h1>", page)
        self.assertIn('href="/modules/04-embeddings"', page)

    def test_guide_is_the_readme_with_links_pointing_at_the_site(self):
        status, page = get("/guide")
        self.assertEqual(status, 200)
        self.assertIn("<h2>Installation</h2>", page)
        self.assertIn('href="/modules/01-first-call"', page)
        self.assertNotIn('href="modules/', page)

    def test_unknown_module_gets_a_page_that_leads_back(self):
        for path in ("/modules/nope", "/modules/01-first-call/check.py", "/modules/01-first-call/deeper/extra", "/modules/"):
            status, page = get(path)
            self.assertEqual(status, 404, path)
            self.assertIn('href="/"', page)

    def test_dashboard_link_only_shows_when_configured(self):
        self.assertNotIn('class="back"', get("/")[1])
        with unittest.mock.patch.object(server, "DASHBOARD_URL", "https://home.example"):
            self.assertIn('<a class="back" href="https://home.example">‹ Tableau de bord</a>', get("/")[1])


class Markdown(unittest.TestCase):
    def test_raw_html_is_escaped(self):
        page = server.render("<script>alert(1)</script>\n\n**ok** <img src=x onerror=alert(1)>")
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("<strong>ok</strong>", page)

    def test_links_keep_safe_targets_only(self):
        page = server.render("[a](https://example.org/x) [b](javascript:alert(1)) [c](modules/01-first-call/LESSON.md)")
        self.assertIn('<a href="https://example.org/x">a</a>', page)
        self.assertIn('<a href="/modules/01-first-call">c</a>', page)
        self.assertNotIn("<a href=\"javascript", page)

    def test_code_keeps_its_text_whatever_it_contains(self):
        page = server.render("```php\nif ($a < 2 && $b) { echo \"**x**\"; }\n# not a heading\n```\n\nInline `a < b` and `` `tick` ``.")
        self.assertIn('<pre><code class="language-php">if ($a &lt; 2 &amp;&amp; $b) { echo &quot;**x**&quot;; }\n# not a heading\n</code></pre>', page)
        self.assertIn("<code>a &lt; b</code>", page)
        self.assertIn("<code>`tick`</code>", page)

    def test_lists_wrap_and_restart_where_the_source_does(self):
        page = server.render("1. one\n   still one\n2. two\n\n```\ncode\n```\n\n3. three\n\n- a\n  still a\n- b")
        self.assertIn("<ol>\n<li>one\nstill one</li>\n<li>two</li>\n</ol>", page)
        self.assertIn('<ol start="3">\n<li>three</li>\n</ol>', page)
        self.assertIn("<ul>\n<li>a\nstill a</li>\n<li>b</li>\n</ul>", page)

    def test_tables_scroll_inside_their_own_container(self):
        page = server.render("| a | b |\n|---|---|\n| 1 | `2` |")
        self.assertIn('<div class="table"><table>', page)
        self.assertIn("<th>a</th>", page)
        self.assertIn("<td><code>2</code></td>", page)

    @unittest.skipUnless(MarkdownIt, "markdown-it-py is not installed")
    def test_every_course_file_renders_like_the_reference_implementation(self):
        reference = MarkdownIt("commonmark", {"html": False}).enable("table")

        def normalise(page):
            page = re.sub(r'</?div[^>]*>|</?thead>|</?tbody>| style="[^"]*"', "", page)
            page = re.sub(r'href="[^"]*"', 'href=""', page)  # the reader rewrites links to its own pages
            return re.sub(r"\s+", " ", re.sub(r">\s+<", "><", page)).strip()

        files = sorted(server.MODULES.glob("*/*.md")) + [server.ROOT / "README.md"]
        self.assertGreater(len(files), 28)
        for path in files:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path.relative_to(server.ROOT))):
                self.assertEqual(normalise(server.render(text)), normalise(reference.render(text)))


class Serving(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def fetch(self, path, method="GET"):
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + path, method=method)) as response:
                return response.status, response.headers, response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            with error:
                return error.code, error.headers, error.read().decode("utf-8", "replace")

    def test_pages_carry_the_security_headers(self):
        status, headers, body = self.fetch("/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(headers["Content-Security-Policy"], "default-src 'self'")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("Régler la génération", body)

    def test_health_stylesheet_and_icon_are_served(self):
        self.assertEqual(self.fetch("/health")[::2], (200, "ok"))
        status, headers, css = self.fetch("/style.css")
        self.assertEqual((status, headers["Content-Type"]), (200, "text/css"))
        self.assertIn("--bg: #f3f1ec", css)
        self.assertIn("safe-area-inset-bottom", css)
        self.assertEqual(self.fetch("/icon.svg")[0], 200)

    def test_nothing_else_of_the_repository_is_reachable(self):
        hostile = [
            "/.env", "/.env.example", "/.git/config", "/README.md", "/assistant/config.py", "/server.py",
            "/modules/../.env", "/modules/01-first-call/../../.env.example", "/modules/%2e%2e/%2e%2e/.env.example",
            "/../.env.example", "/%2e%2e/.env.example", "/..%2f.env.example", "//etc/passwd", "/static/../server.py",
            "/modules/01-first-call/exercise.py", "/",
        ]  # fmt: skip
        for path in hostile[:-1]:
            status, _, body = self.fetch(path)
            self.assertEqual(status, 404, path)
            self.assertNotIn("LEARNER", body, path)
            self.assertNotIn("def ", body, path)

    def test_only_reading_is_allowed(self):
        for method in ("POST", "PUT", "DELETE"):
            self.assertIn(self.fetch("/modules/01-first-call", method)[0], (405, 501), method)

    def test_folders_are_never_listed(self):
        self.assertEqual(self.fetch("/modules")[0], 404)


if __name__ == "__main__":
    unittest.main()
