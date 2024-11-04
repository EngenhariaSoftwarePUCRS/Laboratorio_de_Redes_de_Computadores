Step-by-step guide for genral GNS3 usage:

1. Download and install GNS3 from [GNS3 website](https://www.gns3.com/software/download)
2. Download a Cisco IOS image from [Cisco website](https://software.cisco.com/download/home)
3. Go to GNS3 > Edit > Preferences > Dynamips > IOS routers > New
4. Browse to the downloaded IOS image
   1. Next
   2. 256MiB RAM > Next
   3. Configure slots:
      1. 0: GT96100-FE
      2. 1: NM-1FE-TX
      3. 2: NM-4T
      4. Next
   4. Configure wit modules:
      1. 0: WIC-1T
      2. 1: WIC-1T
      3. Next
   5. If there is no Idle-PC value, click on the finder and wait for the value to appear
   6. Finish

[GNS3 Docs - Your First Cisco Topology](https://docs.gns3.com/docs/getting-started/your-first-cisco-topology)

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
