import sys
import os
import zlib
import hashlib
def read_binary_object(sha):
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "rb") as f:
        data = zlib.decompress(f.read())
        header, content = data.split(b"\0", 1)
        return content
def create_blob_entry(path, write=True):
    with open(path, "rb") as f:
        data = f.read()
        header = f"blob {len(data)}\0".encode("utf-8")
        store = header + data
        sha = hashlib.sha1(store).hexdigest()
        if write:
            os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
            with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
                f.write(zlib.compress(store))
    return sha
def write_tree(path: str):
    if os.path.isfile(path):
        return create_blob_entry(path)
    contents = sorted(
        os.listdir(path),
        key=lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/",
    )
    s = b""
    for item in contents:
        if item == ".git":
            continue
        full = os.path.join(path, item)
        if os.path.isfile(full):
            s += f"100644 {item}\0".encode()
        else:
            s += f"40000 {item}\0".encode()
        sha1 = int.to_bytes(int(write_tree(full), base=16), length=20, byteorder="big")
        s += sha1
    s = f"tree {len(s)}\0".encode() + s
    sha1 = hashlib.sha1(s).hexdigest()
    os.makedirs(f".git/objects/{sha1[:2]}", exist_ok=True)
    with open(f".git/objects/{sha1[:2]}/{sha1[2:]}", "wb") as f:
        f.write(zlib.compress(s))
    return sha1
def main():
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        # We don't care about the options yet, but we need to extract them anyway
        if sys.argv[2] == "-p":
            hash = sys.argv[3]
            content = read_binary_object(hash)
            print(content.decode("utf-8"), end="")
    elif command == "hash-object":
        if sys.argv[2] == "-w":
            file = sys.argv[3]
            with open(file, "rb") as f:
                data = f.read()
                header = f"blob {len(data)}\0".encode("utf-8")
                store = header + data
                sha = hashlib.sha1(store).hexdigest()
                os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
                with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
                    f.write(zlib.compress(store))
                print(sha)
    elif command == "ls-tree":
        param, hash = sys.argv[2], sys.argv[3]
        if param == "--name-only":
            binary_data = read_binary_object(hash)
            while binary_data:
                mode, binary_data = binary_data.split(b"\0", 1)
                _, name = mode.split()
                binary_data = binary_data[20:]
                print(name.decode("utf-8"))
    elif command == "write-tree":
        print(write_tree("./"))
    else:
        raise RuntimeError(f"Unknown command #{command}")
if __name__ == "__main__":
    main()