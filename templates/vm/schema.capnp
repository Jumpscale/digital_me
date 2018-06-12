@0x82a66cb45b1e9ace; 



struct Schema {
    memory @0: UInt16 = 128; # Amount of memory in MiB
    cpu @1: UInt16 = 1; # Number of virtual CPUs
    zerotier @2: Zerotier; # zerotier nic to attach to the vm
    image @3: Text;
    disks @4: List(Disk); # list of disks to attach to the vm
    configs @5: List(Config); # list of config
    ztIdentity @6: Text; # VM zerotier ID
    nodeId @7: Text;

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
   }

    enum DiskType{
        hdd @0;
        ssd @1;
    }

   struct Zerotier {
      id @0: Text;
      ztClient @1: Text;
   }
}
