import os
import subprocess
import sys
import argparse

global updated_services
updated_services = {"updated_services" : [],
                    "not_updated_services" :[]}


def run_update_in_subdirs(dir_path):
    if not os.path.isdir(dir_path):
        print(f"Fehler: Verzeichnis '{dir_path}' existiert nicht.", file=sys.stderr)
        return 1

    try:
        subdirs = [os.path.join(dir_path, d) for d in os.listdir(dir_path)
                    if os.path.isdir(os.path.join(dir_path, d))]
    except Exception as e:
        print(f"Fehler beim Durchsuchen von '{dir_path}': {e}", file=sys.stderr)
        return 1

    for subdir in subdirs:
        docker_compose = os.path.join(subdir, "docker-compose.yaml")
        update_file = os.path.join(subdir, "update")
        if os.path.isfile(docker_compose) and os.path.isfile(update_file) and os.access(update_file, os.X_OK):
            execute_update(subdir)


def execute_update(subdir):


    try:

        subprocess.run(['docker', 'compose', 'pull'], cwd=subdir, check=True)
        # subprocess.run(['docker compose down'], cwd=subdir, check=True)
        subprocess.run(['docker', 'compose', 'down'], cwd=subdir, check=True)
        subprocess.run(['docker', 'compose', 'up', '-d'], cwd=subdir, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von docker Befehlen")
        updated_services["not_updated_services"].append(subdir)
        print(f"Fehler: {e}", file=sys.stderr)
        return

    print(f"Erfolgreich ausgeführt: '{subdir}/update.sh'")

    updated_services["updated_services"].append(subdir)


def main():
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('filename')
    args = parser.parse_args()
    run_update_in_subdirs(args.filename)


if __name__ == '__main__':
    main()