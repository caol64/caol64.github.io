---
author: caol64
title: Exporting Save Files From a PS2 Memory Card
slug: exporting-file-from-ps2-memcard
description: Dive into the exciting world of PS2 memory card filesystems and learn how to extract specific game saves using Python. Fully executable code provided. Step into our in-depth analysis!
date: 2023-09-29 17:49:16
draft: false
ShowToc: true
TocOpen: true
tags:
  - Open Source
  - Reverse Engineering
  - Tutorial
  - PS2
categories:
  - Reverse Engineering
---
In the previous article, we analyzed the file system of the PS2 memory card. This time, we'll dive straight into practice and write Python code to export specific game saves. The complete code for this article can be found at: [ps2mc-browser](https://github.com/caol64/ps2mc-browser).

## 01 Parsing the `SuperBlock
`
The structure of the `SuperBlock` is as follows, with a size of 340 bytes:

```c++
struct SuperBlock {
    char magic[28];
    char version[12];
    uint16 page_size;
    uint16 pages_per_cluster;
    uint16 pages_per_block;
    uint16 unknown; // ignore
    uint32 clusters_per_card;
    uint32 alloc_offset;
    uint32 alloc_end;
    uint32 rootdir_cluster;
    uint32 backup_block1; // ignore
    uint32 backup_block2; // ignore
    uint32 unknown[2]; // ignore
    uint32 ifc_list[32];
    uint32 bad_block_list[32]; // ignore
    byte card_type;
    byte card_flags;
    byte unknown; // ignore
    byte unknown; // ignore
};
```

Use `struct.unpack()` to unpack:

```python
struct.Struct("<28s12sHHH2xLLLL4x4x8x128s128xbbxx").unpack(byte_val)
```

Obtain `page_size` and `pages_per_cluster`.

## 02 Reading `page` and `cluster`

Calculate the sizes of `page` and `cluster` using the formula:

```python
self.spare_size = (self.page_size // 128) * 4  # Size of spare area in bytes
self.raw_page_size = self.page_size + self.spare_size  # Total size of page including spare area in bytes
self.cluster_size = self.page_size * self.pages_per_cluster  # Size of cluster in bytes
```

Read `page` and `cluster`, discarding the contents of the `spare area`:

```python
def read_page(self, n):  # n is the page number
    offset = self.raw_page_size * n
    return self.byte_val[offset: offset + self.page_size]

def read_cluster(self, n):  # n is the cluster number
    page_index = n * self.pages_per_cluster
    byte_buffer = bytearray()
    for i in range(self.pages_per_cluster):
        byte_buffer += self.read_page(page_index + i)
    return bytes(byte_buffer)
```

## 03 Constructing the `FAT` Matrix

From the previous article, we know the construction method of the `FAT` matrix as follows:

![](imgs/posts/2023-09-29-exporting-file-from-ps2-memcard/%E5%AD%98%E5%82%A8%E5%8D%A1-FAT2.jpg)

```python
def __build_fat_matrix(self):
    # Build the indirect FAT from ifc_list
    indirect_fat_matrix = self.__build_matrix(self.ifc_list)
    # Indirect FAT is a one-dimensional array
    indirect_fat_matrix = indirect_fat_matrix.reshape(indirect_fat_matrix.size)
    # Exclude unallocated values like 0xFFFFFFFF
    indirect_fat_matrix = [x for x in indirect_fat_matrix if x != Fat.UNALLOCATED]
    # Build the direct FAT from the indirect FAT
    fat_matrix = self.__build_matrix(indirect_fat_matrix)
    return fat_matrix

def __build_matrix(self, cluster_list):
    # Initialize the matrix
    matrix = np.zeros((len(cluster_list), self.fat_per_cluster), np.uint32)
    # Iterate through clusters
    for index, v in enumerate(cluster_list):
        # Read out 256 FAT values for each cluster
        cluster_value = self.read_cluster(v)
        cluster_value_unpacked = np.frombuffer(cluster_value, np.uint32)
        for index0, v0 in enumerate(cluster_value_unpacked):
            # Assign values to the matrix
            matrix[index, index0] = v0
    return matrix

# Given a cluster number n, find its corresponding FAT value
def get_fat_value(self, n):
    value = self.fat_matrix[(n // self.fat_per_cluster) % self.fat_per_cluster,
                            n % self.fat_per_cluster]
    # The highest bit being 8 represents an allocated cluster, other values represent unallocated clusters,
    # when the highest bit is 8, the integer value of the lower 31 bits is taken
    return value ^ Fat.ALLOCATED_BIT if value & Fat.ALLOCATED_BIT > 0 else value
```

## 04 Entry Data Structure

An entry serves as metadata for all files and directories. The data structure of an entry is as follows:

```c++
struct Entry {
    uint16 mode;
    uint16 unknown; // ignore
    uint32 length;
    char created[8];
    uint32 cluster;
    uint32 dir_entry; // ignore
    char modified[8];
    uint32 attr; // ignore
    char padding[28]; // ignore
    char name[32];
    char padding[416]; // ignore
};
```

Using `struct.unpack()` to unpack:

```python
struct.Struct("<H2xL8sL4x8s4x28x32s416x").unpack(byte_val)
```

Each entry is 512 bytes in size. The most important field in an entry is `cluster`, which identifies the cluster number corresponding to the file or directory of that entry. If the entry represents a directory, the cluster number corresponds to the "entry cluster"; if the entry represents a file, the cluster number corresponds to the "file cluster". Another important field is `length`, which represents the number of entries in a directory if the entry represents a directory, or the number of bytes in a file if the entry represents a file.

## 05 Parsing "Entry Cluster" and "Data Cluster"

```python
# Read entry, where each entry is 512 bytes and multiple entries can be contained in one cluster
def read_entry_cluster(self, cluster_offset):
    cluster_value = self.read_cluster(cluster_offset + self.alloc_offset)
    return Entry.build(cluster_value)

# Read data, starting from the first cluster until the end of the file
def read_data_cluster(self, entry):
    byte_buffer = bytearray()
    chain_start = entry.cluster
    bytes_read = 0
    while chain_start != Fat.CHAIN_END:
        to_read = min(entry.length - bytes_read, self.cluster_size)
        byte_buffer += self.read_cluster(chain_start + self.alloc_offset)[:to_read]
        bytes_read += to_read
        chain_start = self.get_fat_value(chain_start)
    return bytes(byte_buffer)

def build(byte_val):
    entry_count = len(byte_val) // Entry.__size
    entries = []
    for i in range(entry_count):
        entries.append(Entry(byte_val[i * Entry.__size:
                                      i * Entry.__size + Entry.__size]))
    return entries
```

## 06 Reading all files from the memory card

As mentioned in the previous article, the root directory does not have entries. Its first "entry cluster" is specified in the `rootdir_cluster` field of the superblock, and the number of entries it contains is specified in the `.` entry.

To read all files from the memory card, the first step is to parse all entries in the root directory and then parse all files under those entries. Therefore, all you need to do is loop through the following method:

```python
def find_sub_entries(self, parent_entry):
    chain_start = parent_entry.cluster
    sub_entries = []
    while chain_start != Fat.CHAIN_END:
        entries = self.read_entry_cluster(chain_start)
        for e in entries:
            if len(sub_entries) < parent_entry.length:
                sub_entries.append(e.unpack())
        chain_start = self.get_fat_value(chain_start)
    return [x for x in sub_entries if not x.name.startswith('.')]
```

The result is as follows:

```
BISCPS-15119sv01
    GameData
    BISCPS-15119sv01
    icon00.ico
    icon.sys
BISCPS-15116sv01
    GameData
    BISCPS-15116sv01
    icon00.ico
    icon.sys
BASLUS-21441DBZT2
    icon.sys
    dbzsn.ico
    BASLUS-21441DBZT2
...
```

## 07 Exporting Game Saves

Now that all file entries have been read, all we need to do is write a method that can export all files in a directory based on the input game name.

```python
def export(self, name, dest):
    dir_path = dest + os.sep + name
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    entries = self.lookup_entry_by_name(name)
    for e in entries:
        if e.is_file():
            with open(dir_path + os.sep + e.name, 'wb') as f:
                f.write(self.ps2mc.read_data_cluster(e))
```

## 08 Conclusion

Now, we can successfully export a game's save files from the memory card. If you have a Python runtime environment, you can directly run the code provided in the GitHub link provided at the beginning of the article.

In the next article, we will analyze the `icon.sys` and `xxx.ico` files in each save file. These two files contain the data for the 3D effects in the save files.

## 09 References

- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)
- [Florian Märkl - mymcplus](https://git.sr.ht/~thestr4ng3r/mymcplus)
