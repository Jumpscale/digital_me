@0xf35b28a27d2d7444;

struct Schema {
    vmDiskSize @0: UInt16;
    vmZerotier @1: Zerotier;
    nodeRobot @2: Text;
    struct Zerotier {
      id @0: Text;
      ztClient @1: Text;
    }
}

