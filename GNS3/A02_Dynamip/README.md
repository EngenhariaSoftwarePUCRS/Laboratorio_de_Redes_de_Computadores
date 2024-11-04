Based on [GNS3 Docs - Your First Cisco Topology](https://docs.gns3.com/docs/getting-started/your-first-cisco-topology)

Step-by-step guide (after having followed the [global guide](../README.md)):
1. Drag two routers from the left pane to the workspace
2. Click on the "add a link" button
3. Click on each router and select the interface "FastEthernet0/0" for both
4. Click on the "play" button to start the routers
5. Click on the "console" button (next to play) to open the console of each router
6. Configure the routers:
   Obs:
   - The IP addresses are just examples. Use the ones that fit your network.
   - For router 1 we will be using the full commands, while for router 2 we will be using the short versions.
   - We will be using `ospf` as the routing protocol.
   1. Router 1:
    ```bash
        enable
        configure terminal
        interface FastEthernet0/0
        ip address 10.1.1.1 255.255.255.0
        no shutdown
        interface Loopback0
        ip address 1.1.1.1 255.255.255.255
        end
        show ip interface brief
        ping 10.1.1.2
        configure terminal
        router ospf 1
        router-id 1.1.1.1
        network 0.0.0.0 255.255.255.255 area 0
        end
        show ip ospf neighbor
        show ip route
        copy running-config startup-config
    ```
    2. Router 2:
    ```bash
        en
        conf t
        int f0/0
        ip address 10.1.1.2 255.255.255.0
        no shut
        int loop0
        ip address 2.2.2.2 255.255.255.255
        end
        sh ip int br
        ping 10.1.1.1
        conf t
        router ospf 1
        router-id 2.2.2.2
        network 0.0.0.0 255.255.255.255 area 0
        end
        sh ip ospf neigh
        sh ip route
        wr
    ```
