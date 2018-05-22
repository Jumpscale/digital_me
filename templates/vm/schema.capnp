@0x89a3426611f2d4e6; 


struct Schema {
    memory @0: UInt16 = 128; # Amount of memory in MiB
    cpu @1: UInt16 = 1; # Number of virtual CPUs
    zerotier @2: Zerotier; # zerotier nic to attach to the vm
    image @3: Text;
    ports @4:List(Port); # List of portforwards from node to vm
    disks @5: List(Disk); # list of disks to attach to the vm
    configs @6: List(Config); # list of config
    ztIdentity @7: Text; # VM zerotier ID
    nodeRobot @8: Text;
    nodeVm @9: Text;

   struct Port {
        source @0: Int32;
        target @1: Int32;
        name @2: Text;
   }
   struct Config {
        path @0: Text;
        content @1: Text;
        name @2: Text;
   }

   enum FsType {
        btrfs @0;
        ext4 @1;
        ext3 @2;
        ext2 @3;
   }

   struct Disk {
      diskType @0: DiskType;
      size @1: UInt16;
      mountPoint @2: Text;
      filesystem @3: FsType;
      name @4: Text;
      vdisk @5: Text;
   }

    enum DiskType{
        hdd @0;
        ssd @1;
    }


   struct Zerotier {
      id @0: Text;
      ztClient @1: Text;
   }

   enum NicType {
      default @0;
      vlan @1;
      vxlan @2;
      bridge @3;
      zerotier @4;
   }
}
