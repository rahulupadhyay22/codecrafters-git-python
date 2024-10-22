import sys
import os
import zlib
import hashlib
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")
    # Uncomment this block to pass the first stage
    #
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        object_hash = sys.argv[3]
        with open(f".git/objects/{object_hash[:2]}/{object_hash[2:]}", "rb") as file:
            data = zlib.decompress(file.read())
            print(data.split(b"\0")[1].decode("utf-8"), end="")
    elif command == "hash-object":
        file_name = sys.argv[3]
        with open(file_name, "rb") as f:
            content = f.read()
            header = f"blob {len(content)}\0".encode()
            content = header + content
            hash_values = hashlib.sha1(content).hexdigest()
            os.makedirs(f".git/objects/{hash_values[:2]}")
            with open(f".git/objects/{hash_values[:2]}/{hash_values[2:]}", "wb") as f:
                f.write(zlib.compress(content))
            print(hash_values)
    elif command == "ls-tree":
        hash_value = sys.argv[3]
        with open(f".git/objects/{hash_value[:2]}/{hash_value[2:]}", "rb") as f:
            data = zlib.decompress(f.read())
            _, binary_data = data.split(b"\x00", maxsplit=1)
            while binary_data:
                mode, binary_data = binary_data.split(b"\x00", maxsplit=1)
                _, name = mode.split()
                binary_data = binary_data[20:]
                print(name.decode("utf-8"))
    else:
        raise RuntimeError(f"Unknown command #{command}")
if __name__ == "__main__":
    main()