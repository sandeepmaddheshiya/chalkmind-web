"""Local preview with the same URLs as the live site (nginx):
/guides -> guides.html, /for/teachers -> for/teachers.html, /guides/ -> 301 /guides,
unknown pages -> 404.html.   Run:  python3 tools/serve.py   (http://localhost:8000)
"""
import http.server
import os
import sys

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=PUBLIC, **kw)

    def do_GET(self):
        path, _, query = self.path.partition('?')
        if len(path) > 1 and path.endswith('/'):
            self.send_response(301)
            self.send_header('Location', path.rstrip('/') + ('?' + query if query else ''))
            self.end_headers()
            return
        fs = os.path.join(PUBLIC, path.lstrip('/'))
        if path != '/' and not os.path.isfile(fs):
            if os.path.isfile(fs + '.html'):
                self.path = path + '.html' + ('?' + query if query else '')
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(open(os.path.join(PUBLIC, '404.html'), 'rb').read())
                return
        return super().do_GET()

    def list_directory(self, path):  # never show folder listings
        self.send_error(404)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f'Preview: http://localhost:{port}')
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
