import hashlib
import os
import yaml


def get_file_sha1(path):
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def main():
    path = "app/database/cubes"
    cubes = next(os.walk(path))[1]

    for cube in cubes:
        cube_path = os.path.join(path, cube)
        cube_meta = os.path.join(cube_path, "metadata.yaml")
        cube_manifest = os.path.join(cube_path, "mlcube.yaml")
        with open(cube_meta, "r") as f:
            meta = yaml.full_load(f)

        meta["sha1"] = get_file_sha1(cube_manifest)
        print(f"{cube_manifest}: {get_file_sha1(cube_manifest)}")
        with open(cube_meta, "w") as f:
            yaml.dump(meta, f)


if __name__ == "__main__":
    main()
