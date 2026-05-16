import socket
import logging
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from typing import Optional

logger = logging.getLogger(__name__)

class DiscoveryService:
    """
    Handles mDNS (Zeroconf) service broadcasting.
    Follows Single Responsibility Principle (SRP) by focusing only on discovery logic.
    """
    
    def __init__(self):
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None

    def get_local_ip(self) -> str:
        """
        Retrieves the local IP address used to connect to the internet.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def start(self, port: int, service_name: str = "LeafCloud-Server"):
        """
        Starts the Zeroconf service broadcast.
        """
        if self.zeroconf:
            logger.warning("Zeroconf service already started.")
            return

        local_ip = self.get_local_ip()
        service_type = "_leafcloud._tcp.local."
        registration_name = f"{service_name}.{service_type}"

        self.service_info = ServiceInfo(
            type_=service_type,
            name=registration_name,
            addresses=[socket.inet_aton(local_ip)],
            port=port,
            properties={'version': '2.0'},
            server=f"{service_name.lower()}.local.",
        )

        self.zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
        self.zeroconf.register_service(self.service_info)
        
        logger.info(f"Zeroconf service registered: {registration_name} at {local_ip}:{port}")

    def stop(self):
        """
        Unregisters the service and closes the Zeroconf instance.
        """
        if self.zeroconf:
            if self.service_info:
                self.zeroconf.unregister_service(self.service_info)
            self.zeroconf.close()
            self.zeroconf = None
            self.service_info = None
            logger.info("Zeroconf service unregistered and closed.")

# Singleton instance for global access within the app
discovery_service = DiscoveryService()
