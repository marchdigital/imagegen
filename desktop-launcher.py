# desktop.py
import webview
import threading
import uvicorn
import sys
import time
import requests
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DesktopApp:
    def __init__(self, dev_mode=False):
        self.dev_mode = dev_mode
        self.host = "127.0.0.1"
        self.port = 8000
        self.server_thread = None
        self.window = None
        
    def start_server(self):
        """Start the FastAPI server in a separate thread"""
        def run():
            logger.info(f"Starting FastAPI server on {self.host}:{self.port}")
            uvicorn.run(
                "backend.main:app",
                host=self.host,
                port=self.port,
                reload=self.dev_mode,
                log_level="info" if self.dev_mode else "warning"
            )
        
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        self.wait_for_server()
    
    def wait_for_server(self, timeout=30):
        """Wait for the server to be ready"""
        logger.info("Waiting for server to start...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://{self.host}:{self.port}/health")
                if response.status_code == 200:
                    logger.info("Server is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.5)
        
        logger.error("Server failed to start within timeout")
        return False
    
    def create_window(self):
        """Create the desktop window"""
        # Window configuration
        window_config = {
            "title": "AI Image Generator",
            "url": f"http://{self.host}:{self.port}",
            "width": 1400,
            "height": 900,
            "min_size": (1200, 700),
            "resizable": True,
            "fullscreen": False,
            "confirm_close": True,
            "background_color": "#1a1a1a"
        }
        
        # Add debug tools in dev mode
        if self.dev_mode:
            window_config["debug"] = True
        
        # Create window
        self.window = webview.create_window(**window_config)
        
        # Window event handlers
        self.window.events.loaded += self.on_loaded
        self.window.events.closed += self.on_closed
    
    def on_loaded(self):
        """Called when the window is loaded"""
        logger.info("Window loaded successfully")
        
        # Inject custom CSS for better desktop experience
        css = """
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        ::-webkit-scrollbar-track {
            background: #2a2a2a;
        }
        ::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 6px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
        
        /* Prevent text selection on UI elements */
        .button, .tab, .toolbar, .sidebar {
            -webkit-user-select: none;
            user-select: none;
        }
        
        /* Native-like context menus */
        .context-menu {
            -webkit-app-region: no-drag;
        }
        """
        self.window.evaluate_js(f"""
            const style = document.createElement('style');
            style.textContent = `{css}`;
            document.head.appendChild(style);
        """)
    
    def on_closed(self):
        """Called when the window is closed"""
        logger.info("Window closed, shutting down...")
        sys.exit(0)
    
    def expose_api(self):
        """Expose Python functions to JavaScript"""
        class API:
            @staticmethod
            def open_folder(path):
                """Open a folder in the system file explorer"""
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Windows":
                    subprocess.run(["explorer", path])
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", path])
                else:  # Linux
                    subprocess.run(["xdg-open", path])
            
            @staticmethod
            def get_system_info():
                """Get system information"""
                import platform
                return {
                    "platform": platform.system(),
                    "architecture": platform.machine(),
                    "python_version": platform.python_version()
                }
            
            @staticmethod
            def save_file_dialog(default_name="image.png"):
                """Show save file dialog"""
                result = self.window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=default_name,
                    file_types=('Image Files (*.png;*.jpg;*.webp)', '*.png;*.jpg;*.webp')
                )
                return result[0] if result else None
            
            @staticmethod
            def open_file_dialog():
                """Show open file dialog"""
                result = self.window.create_file_dialog(
                    webview.OPEN_DIALOG,
                    allow_multiple=False,
                    file_types=('Image Files (*.png;*.jpg;*.webp)', '*.png;*.jpg;*.webp')
                )
                return result[0] if result else None
        
        # Make API available to JavaScript
        if self.window:
            self.window.expose(API())
    
    def run(self):
        """Run the desktop application"""
        try:
            # Start the server
            self.start_server()
            
            # Create and configure window
            self.create_window()
            
            # Start the GUI
            logger.info("Starting desktop application...")
            webview.start(
                func=self.expose_api,
                debug=self.dev_mode,
                http_server=False  # We're using our own server
            )
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            logger.info("Application shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Image Generator Desktop App")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with debug tools"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on"
    )
    
    args = parser.parse_args()
    
    # Check if running from source or compiled
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = Path(sys.executable).parent
    else:
        # Running from source
        application_path = Path(__file__).parent
    
    # Change to application directory
    os.chdir(application_path)
    
    # Create and run app
    app = DesktopApp(dev_mode=args.dev)
    if args.port:
        app.port = args.port
    
    app.run()


if __name__ == "__main__":
    main()