"""
Minimal FastAPI server for testing.
"""

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
except ImportError:
    print("FastAPI not available, using basic HTTP server")
    import http.server
    import socketserver
    import json
    
    class SimpleHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"message": "Agentic Workflow System API", "status": "running"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    if __name__ == "__main__":
        PORT = 8000
        with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
            print(f"✅ Simple HTTP server running on http://localhost:{PORT}")
            httpd.serve_forever()

else:
    app = FastAPI(
        title="Agentic Workflow System",
        description="Dynamic, JSON-configurable agentic workflow executor",
        version="1.0.0"
    )

    @app.get("/")
    async def root():
        return {
            "message": "Agentic Workflow System API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    if __name__ == "__main__":
        import uvicorn
        print("✅ FastAPI server starting...")
        uvicorn.run(app, host="0.0.0.0", port=8000)