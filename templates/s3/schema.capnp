@0xf35b28a27d2d7444;

struct Schema {
    vmDiskSize @0: UInt16;
    vmZerotier @1: Zerotier;
    farmerIyoOrg  @2: Text;
    dataShards @3: Int32=1;
    parityShards @4: Int32;
    storageType @5: StorageType;
    storageSize @6: UInt16;
    namespaces @7: List(Namespace);
    minioLogin @8: Text;
    minioPassword @9: Text;
    minioUrl @10: Text;

    enum StorageType {
     hdd @0;
     ssd @1;
    }

    struct Zerotier {
      id @0: Text;
      ztClient @1: Text;
    }

    struct Namespace {
    name @0: Text;
    node @1: Text;
    url @2: Text;

}

