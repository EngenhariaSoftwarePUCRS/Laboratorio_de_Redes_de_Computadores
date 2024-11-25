<h2>Table of Contents</h2>

- [Goal](#goal)
- [Description](#description)
- [Technical Specifications](#technical-specifications)
  - [More About Docker](#more-about-docker)
- [How to Run](#how-to-run)
- [Cheat Sheet](#cheat-sheet)
  - [Docker Actions](#docker-actions)
  - [Attacking Container Actions](#attacking-container-actions)
  - [Victim Container Actions](#victim-container-actions)
  - [Gateway Container Actions](#gateway-container-actions)
- [Authors](#authors)

## Goal

This project involves developing a man-in-the-middle attack to capture the web browsing history of a remote target computer. The project is divided into three main stages:

Host Discovery: Develop a tool to identify active hosts in the network by performing a scan similar to a ping sweep, mapping the connected devices.

Execution of the Attack: After identifying the target host, execute an ARP Spoofing attack with man-in-the-middle using the arpspoof tool, inserting the attacker into the communication flow between the target and the router.

Traffic Monitoring: Create an application to monitor the web browsing traffic of the target host, capturing HTTP and DNS packets to track the browsing history.

The goal is to intercept and analyze network traffic to capture the target’s web activity.

## Description

This project involves using a sniffer program like Wireshark to monitor the entire network traffic of a host and analyze its content. By inspecting DNS and HTTP packets, it’s possible to reconstruct the web browsing history of a device. However, this typically requires physical access to the host. To remotely monitor other devices on a local network, a man-in-the-middle attack can be employed, exploiting common vulnerabilities in local networks.

In this project, ARP Spoofing will be used to intercept network traffic and monitor the web browsing history of the target hosts. The implementation is divided into three main stages:

Development of the Scanning Application: Create a tool to identify active hosts in the local network (Annex I).

Execution of ARP Spoofing with Man-in-the-Middle: Set up an attack that places the attacker between the target host and the router (Annex II).

Development of Traffic Analysis Application: Create a tool to capture and analyze the web browsing history of the attacked hosts (Annex III).

The objective is to intercept and analyze the network traffic to reconstruct the target’s web browsing history.

For more specific business rules and project description, please refer to the [full document](T2_20242.pdf).

## Technical Specifications

This project was developed using [Python](https://www.python.org/) with [Docker](#docker) containers.

### More About [Docker](https://www.docker.com/)

Docker is used to create containers for the application and the database. It is used to create a development environment that is as close as possible to the production environment.
It is highly recommended to use Docker to run the application.

We have a [`Dockerfile`](Dockerfile) that contains the configuration for the application container and a [`docker-compose`](docker-compose.yml) file which builds three instances of the application.

For some useful Docker commands, [click here](#docker-actions).

## How to Run

Now that you have all the necessary tools installed, you can run the application.
To start the application with Docker, simply run the following command:

```bash
$ docker compose up --build -d
```

That's it! You should now have three instances of the application running on your machine, on ports 8080, 8081, and 8082.

To access the application machines, simply go to `http://localhost:8080`, `http://localhost:8081`, and `http://localhost:8082`.

To check which hosts are active in the network, you can run the following command:

```bash
$ python host_discovery.py <rede/mascara> <timeout_ms>
```

## Cheat Sheet

### Docker Actions

```bash
# Build the containers
$ docker compose up --build

# List all containers
$ docker ps

# Access the container
$ docker exect -it {{container_id}} sh
```

### Attacking Container Actions

```bash
# Enter into the attacking container
$ scripts/docker-exec.sh {{attacker_container_id}}
# Attack the target
$ arpspoof -i eth0 -t {{target_ip}} {{gateway_ip}}
# Attack the gateway
$ arpspoof -i eth0 -t {{gateway_ip}} {{target_ip}}
```

### Victim Container Actions

```bash
# Enter into the gateway container
$ scripts/docker-exec.sh {{gateway_container_id}}
# Ping gateway (to generate traffic)
$ ping {{gateway_ip}}
# Check the ARP table
$ arp -n
```

### Gateway Container Actions

```bash
# Enter into the gateway container
$ scripts/docker-exec.sh {{gateway_container_id}}
# Check the ARP table
$ arp -n
```

## Authors

- [Carolina Ferreira](https://github.com/carolmicfer)
- [Felipe Freitas Silva](https://github.com/felipefreitassilva)
- [Luiza Heller Kroeff Plá](https://github.com/LuHellerKP)
- [Mateus Campos Caçabuena](https://github.com/mateuscacabuena)
