Step-by-step guide:

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
