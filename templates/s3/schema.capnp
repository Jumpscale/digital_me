@0xf35b28a27d2d7444;

struct Schema {
    vmDiskSize @0: UInt16;
    vmZerotier @1: Zerotier;
    nodeRobot @2: Text;
    farmerIyoOrg  @3: Text;
    dataShards @4: Int32=1;
    parityShards @5: Int32;
    storageType @6: StorageType;
    storageSize @7: UInt16;
    namespaces @8: List(Text);

    enum StorageType {
     hdd @0;
     ssd @1;
    }

    struct Zerotier {
      id @0: Text;
      ztClient @1: Text;
    }

}

