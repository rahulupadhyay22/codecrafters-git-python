import sys
import os
import zlib
import hashlib
def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/master\n")
    print("Initialized git directory")
def cat_file(object_type, sha):
    current_directory = os.getcwd()
    path = f"{current_directory}/.git/objects/{sha[0:2]}/{sha[2:]}"
    with open(path, "rb") as file:
        file_contents = file.read()
    decompressed_file = zlib.decompress(file_contents)
    first_space = decompressed_file.find(b" ")
    object_type = str(decompressed_file[0:first_space])
    decompressed_file = decompressed_file[first_space + 1 :]
    null_value = decompressed_file.find(b"\x00")
    size_of_blob = str(decompressed_file[0:null_value])
    content = decompressed_file[null_value + 1 :].decode("ascii")
    print(content, end="")
def hash_object(object_type, file_name):
    with open(file_name, "rb") as file:
        file_content = file.read()
    #sha = hashlib.sha1(file_content).hexdigest()
    header = f"blob {len(file_content)}\x00"
    store = header.encode("ascii") + file_content
    sha = hashlib.sha1(store).hexdigest()
    git_path = os.path.join(os.getcwd(), ".git/objects")
    os.mkdir(os.path.join(git_path, sha[0:2]))
    with open(os.path.join(git_path, sha[0:2], sha[2:]), "wb") as file:
        file.write(zlib.compress(store))
    #print(sha)
    print(sha, end="")
def main():
    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        if len(sys.argv) != 4:
            print("usage: git cat-file <type> <object>", file=sys.stderr)
            exit()
        object_type = sys.argv[2]
        sha = sys.argv[3]
        cat_file(object_type, sha)
    elif command == "hash-object":
        if len(sys.argv) != 4:
            print("usage: hash-object -w <file>", file=sys.stderr)
            exit()
        object_type = sys.argv[2]
        file_name = sys.argv[3]
        hash_object(object_type, file_name)
    else:
        raise RuntimeError(f"Unknown command #{command}")
if __name__ == "__main__":
    main()