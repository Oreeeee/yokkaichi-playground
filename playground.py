import os
import random
import shutil
import subprocess
import sys
import uuid
from ipaddress import ip_address

import requests

START_IP_INDEX = 1
END_IP_INDEX = 2
PORTS_LIST_INDEX = 3

CFG_BIND_INDEX = 3
CFG_MOTD_INDEX = 4
CFG_PLAYERS_INDEX = 5


def print_usage():
    print(
        "Usage: python3 playground.py START_IP END_IP PORTS\nOr start the script with no arguments and provide values interactively"
    )
    exit(1)


def calc_server_amount(start_ip, end_ip, ports):
    return (int(ip_address(end_ip)) - int(ip_address(start_ip)) + 1) * len(ports)


def create_servers(start_ip, end_ip, ports, base_cfg):
    # Create container directory for servers if needed
    if not os.path.isdir("servers"):
        os.mkdir("servers")

    # Generate a list of IPs
    ips = []
    for i in range(int(ip_address(start_ip)), int(ip_address(end_ip)) + 1):
        ips.append(str(ip_address(i)))

    # Spawn the servers
    uuids = []
    servers = []
    for ip in ips:
        for port in ports:
            dir_uuid = uuid.uuid4()  # Generate a random UUID for the server
            uuids.append(dir_uuid)  # Add the UUID to the list
            os.mkdir(f"servers/{dir_uuid}")  # Create a directory for the server
            shutil.copy(
                "velocity.jar", f"servers/{dir_uuid}/"
            )  # Copy the Velocity JAR to the target dir
            open(
                f"servers/{dir_uuid}/forwarding.secret", "w"
            ).close()  # Create an empty forwarding.secret file (Velocity won't start without it)

            with open(
                f"servers/{dir_uuid}/velocity.toml", "w"
            ) as f:  # Write the config for the server
                server_cfg = base_cfg.copy()
                server_cfg[CFG_BIND_INDEX] = base_cfg[CFG_BIND_INDEX].replace(
                    "CHANGEME_IP", f"{ip}:{port}"
                )
                server_cfg[CFG_MOTD_INDEX] = base_cfg[CFG_MOTD_INDEX].replace(
                    "CHANGEME_MOTD", f"{dir_uuid}"
                )
                server_cfg[CFG_PLAYERS_INDEX] = base_cfg[CFG_PLAYERS_INDEX].replace(
                    "6969", f"{random.randint(1, 30000)}"
                )
                f.writelines(server_cfg)

            # Spawn the server and add it to the server list
            server = subprocess.Popen(
                ["java", "-Xms64M", "-Xmx64M", "-jar", "velocity.jar"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=f"servers/{dir_uuid}/",
            )
            servers.append(server)

    print("Servers created! Press Control-C to exit safely.")
    running = True
    while running:
        try:
            input()
        except KeyboardInterrupt:
            cleanup(servers)
            exit()


def cleanup(servers):
    print("Killing all of the servers...")
    for server in servers:
        server.kill()
    print("Removing all of the files...")
    shutil.rmtree("servers/")
    print("Done!")


def get_user_input():
    start_ip = input("Start IP [127.0.0.1]: ")
    end_ip = input("End IP [127.0.0.5]: ")
    ports = input("Ports (separated by commas) [25565,25566]: ").split(",")

    # Set defaults
    if start_ip == "":
        start_ip = "127.0.0.1"

    if end_ip == "":
        end_ip = "127.0.0.5"

    if ports == []:
        ports = ["25565", "25566"]

    return start_ip, end_ip, ports


def main():
    # Check is Velocity downloaded
    if not os.path.exists("velocity.jar"):
        print("Downloading Velocity...")
        with open("velocity.jar", "wb") as f:
            f.write(
                requests.get(
                    "https://api.papermc.io/v2/projects/velocity/versions/3.2.0-SNAPSHOT/builds/260/downloads/velocity-3.2.0-SNAPSHOT-260.jar"
                ).content
            )

    # Check lenght of argv
    if len(sys.argv) == 1:
        # Ask the user for manual input
        start_ip, end_ip, ports = get_user_input()
    elif len(sys.argv) == 4:
        # Get values from argv
        start_ip = sys.argv[START_IP_INDEX]
        end_ip = sys.argv[END_IP_INDEX]
        ports = sys.argv[PORTS_LIST_INDEX].split(",")
    else:
        print_usage()

    # Check are the IPs provided localhost ones
    if start_ip[:3] != "127" or end_ip[:3] != "127":
        print("IP addresses must be local!")
        exit(1)

    # Load base config config for Velocity
    with open("base_velocity_cfg.toml", "r") as f:
        base_cfg = f.readlines()

    print(f"Creating {calc_server_amount(start_ip, end_ip, ports)} servers...")
    create_servers(start_ip, end_ip, ports, base_cfg)


if __name__ == "__main__":
    main()
