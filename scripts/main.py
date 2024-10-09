from manager import SystemDServiceManager
from services import ServiceConfig

if __name__ == "__main__":
    manager = SystemDServiceManager()

    service_config = ServiceConfig(
        service_name="my_example_service",
        command="/usr/bin/python3",
        parameters=["/path/to/script.py", "--arg1", "value1"],
        schedule="* * * * *"  # Every minute for demonstration purposes
    )

    # Create service and timer
    print(service_config.service_name)
    manager.create_service(service_config)

    # Read service details
    config = manager.read_service(service_config.service_name)
    print("Service Config:", config)

    # Update service
    service_config.schedule = "*/5 * * * *"  # Change to every 5 minutes
    # manager.update_service(service_config)

    # Delete service
    manager.remove_service(service_config.service_name)
