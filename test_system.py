#!/usr/bin/env python3
"""
🌞 TEST DEL SISTEMA HELIOBIO-SOCIAL - Versión Autónoma
"""
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HelioBioHandler(BaseHTTPRequestHandler):
    """Manejador HTTP simple para pruebas"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "🌞 HelioBio-Social v1.0.0 - Sistema de Prueba",
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "version": "test-1.0",
                "components": ["solar_simulator", "social_analyzer", "chizhevsky_engine"]
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/solar/current':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "sunspots": 45,
                "solar_flux": 72.5,
                "flare_activity": 2,
                "interpretation": "Actividad solar moderada",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Endpoint not found')
    
    def log_message(self, format, *args):
        print(f"🌐 {datetime.now().isoformat()} - {format % args}")

def run_test_server():
    """Ejecutar servidor de prueba"""
    print("🎆 INICIANDO SISTEMA HELIOBIO-SOCIAL (Servidor de Prueba)")
    print("📍 Servidor disponible en: http://localhost:8080")
    print("📡 Endpoints:")
    print("   /              - Portal principal")
    print("   /health        - Estado del sistema") 
    print("   /api/solar/current - Actividad solar")
    print("")
    print("🛑 Presiona Ctrl+C para detener")
    
    server = HTTPServer(('localhost', 8080), HelioBioHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
        server.shutdown()

if __name__ == "__main__":
    run_test_server()
