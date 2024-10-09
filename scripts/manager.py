import os
import subprocess
import tempfile
from pydantic import BaseModel, Field, validator
from typing import List


class ServiceConfig(BaseModel):
    service_name: str = Field(..., description="The name of the systemd service.")
    command: str = Field(..., description="The command to execute.")
    parameters: List[str] = Field(default=[], description="List of parameters for the command.")
    schedule: str = Field(..., description="Schedule for the service (OnCalendar format).")

    @validator('service_name')
    def validate_service_name(cls, v):
        if not v.isidentifier():
            raise ValueError('Service name must be a valid identifier (no spaces, special characters).')
        return v


class SystemDServiceManager:
    def __init__(self):
        self.systemd_path = "/etc/systemd/system"

    def create_service(self, config: ServiceConfig):
        # Create the service content
        print(config.service_name)
        service_content = f"""[Unit]
Description={config.service_name}

[Service]
ExecStart={config.command} {' '.join(config.parameters)}

[Install]
WantedBy=multi-user.target
"""
        timer_content = f"""[Unit]
Description=Timer for {config.service_name}

[Timer]
OnCalendar={config.schedule}
Persistent=true

[Install]
WantedBy=timers.target
"""

        # Write to a temp file first for review
        temp_dir = tempfile.mkdtemp()
        temp_service_file = os.path.join(temp_dir, f"{config.service_name}.service")
        temp_timer_file = os.path.join(temp_dir, f"{config.service_name}.timer")

        with open(temp_service_file, 'w') as service_file:
            service_file.write(service_content)

        with open(temp_timer_file, 'w') as timer_file:
            timer_file.write(timer_content)

        print(f"Temporary service file created at: {temp_service_file}")
        print(f"Temporary timer file created at: {temp_timer_file}")
        print("Please review the content before moving to the systemd directory.")

        # The user can manually inspect the files at this point
        input("Press Enter to move the files to systemd folder and enable the service...")

        # Move the files to /etc/systemd/system using sudo
        self.move_to_systemd_folder(temp_service_file, f"{config.service_name}.service")
        self.move_to_systemd_folder(temp_timer_file, f"{config.service_name}.timer")

        # Reload systemd and enable the service and timer
        self.reload_systemd()
        print(f"- sudo systemctl enable {config.service_name}")
        subprocess.run(['sudo', 'systemctl', 'enable', config.service_name])
        print(f"- sudo systemctl enable {config.service_name}.timer")
        subprocess.run(['sudo', 'systemctl', 'enable', f"{config.service_name}.timer"])

    def move_to_systemd_folder(self, temp_file: str, systemd_file_name: str):
        systemd_file_path = os.path.join(self.systemd_path, systemd_file_name)
        print(f"- sudo mv {temp_file} {systemd_file_path}")
        subprocess.run(['sudo', 'mv', temp_file, systemd_file_path])
        print(f"Moved {systemd_file_name} to {systemd_file_path}")

    def reload_systemd(self):
        print("- sudo systemctl daemon-reload")
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])

    def read_service(self, service_name: str) -> ServiceConfig:
        # Paths to service and timer files
        service_file_path = os.path.join(self.systemd_path, f"{service_name}.service")
        timer_file_path = os.path.join(self.systemd_path, f"{service_name}.timer")

        if not os.path.exists(service_file_path):
            raise FileNotFoundError(f"Service file {service_file_path} does not exist.")

        if not os.path.exists(timer_file_path):
            raise FileNotFoundError(f"Timer file {timer_file_path} does not exist.")

        # Read the service file content
        command = ""
        parameters = []

        with open(service_file_path) as f:
            for line in f:
                if line.startswith("ExecStart="):
                    command_line = line.split('=', 1)[1].strip()
                    command_parts = command_line.split()
                    command = command_parts[0]
                    parameters = command_parts[1:]

        # Read the timer file content
        schedule = ""
        with open(timer_file_path, 'r') as f:
            for line in f:
                if line.startswith("OnCalendar="):
                    schedule = line.split('=', 1)[1].strip()
                    break

        return ServiceConfig(service_name=service_name, command=command, parameters=parameters, schedule=schedule)

    def remove_service(self, service_name: str):
        # Construct timer name
        timer_name = f"{service_name}.timer"

        # Stop and disable the service
        print(f"Stopping and disabling service: {service_name}")
        try:
            print(f"sudo systemctl stop {service_name}")
            subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop service {service_name}: {e}")

        try:
            print(f"sudo systemctl disable {service_name}")
            subprocess.run(['sudo', 'systemctl', 'disable', service_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to disable service {service_name}: {e}")

        # Now handle the timer
        print(f"Attempting to stop and disable timer: {timer_name}")
        try:
            # Check if the timer is active
            subprocess.run(['systemctl', 'is-active', timer_name], check=True)
            # If the timer is active, stop and disable it
            print(f"sudo systemctl stop {timer_name}")
            subprocess.run(['sudo', 'systemctl', 'stop', timer_name], check=True)
            print(f"sudo systemctl disable {timer_name}")
            subprocess.run(['sudo', 'systemctl', 'disable', timer_name], check=True)
        except subprocess.CalledProcessError:
            # If the timer is not loaded or not active, inform the user
            print(f"Timer {timer_name} is not loaded or not active. Skipping stop and disable.")

        # Remove the service and timer files
        service_file_path = os.path.join(self.systemd_path, f"{service_name}.service")
        timer_file_path = os.path.join(self.systemd_path, f"{timer_name}")

        if os.path.exists(service_file_path):
            print(f"Removing service file: {service_file_path}")
            print(f"sudo rm {service_file_path}")
            subprocess.run(['sudo', 'rm', service_file_path])
            print(f"Removed service file: {service_file_path}")
        else:
            print(f"Service file {service_file_path} does not exist.")

        if os.path.exists(timer_file_path):
            print(f"Removing timer file: {timer_file_path}")
            print(f"sudo rm {timer_file_path}")
            subprocess.run(['sudo', 'rm', timer_file_path])
            print(f"Removed timer file: {timer_file_path}")
        else:
            print(f"Timer file {timer_file_path} does not exist.")

        # Reload systemd to apply changes
        self.reload_systemd()
