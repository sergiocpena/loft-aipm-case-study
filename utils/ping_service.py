import os
import time
import threading
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ping_service')

class PingService:
    def __init__(self, url, interval_minutes=10):
        """
        Initialize the ping service
        
        Args:
            url (str): The URL to ping
            interval_minutes (int): How often to ping the URL in minutes
        """
        self.url = url
        self.interval_minutes = interval_minutes
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start the ping service in a background thread"""
        if self.is_running:
            logger.info("Ping service is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._ping_loop)
        self.thread.daemon = True  # Thread will exit when main program exits
        self.thread.start()
        logger.info(f"Ping service started. Will ping {self.url} every {self.interval_minutes} minutes")
    
    def stop(self):
        """Stop the ping service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Ping service stopped")
    
    def _ping_loop(self):
        """Main ping loop that runs in the background thread"""
        while self.is_running:
            try:
                response = requests.get(self.url, timeout=10)
                logger.info(f"Pinged {self.url} - Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to ping {self.url}: {str(e)}")
            
            # Sleep for the specified interval
            for _ in range(self.interval_minutes * 60):
                if not self.is_running:
                    break
                time.sleep(1)

# Singleton instance
_ping_service = None

def init_ping_service(url=None, interval_minutes=10):
    """
    Initialize and start the ping service
    
    Args:
        url (str): The URL to ping. If None, will use APP_URL environment variable
        interval_minutes (int): How often to ping the URL in minutes
    
    Returns:
        PingService: The ping service instance
    """
    global _ping_service
    
    if _ping_service is not None:
        return _ping_service
    
    # Get URL from environment variable if not provided
    if url is None:
        url = os.environ.get('APP_URL')
        if not url:
            logger.warning("No URL provided and APP_URL environment variable not set. Ping service not started.")
            return None
    
    _ping_service = PingService(url, interval_minutes)
    _ping_service.start()
    return _ping_service

def get_ping_service():
    """Get the ping service instance"""
    return _ping_service 