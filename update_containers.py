from calendar import c
import os
from pdb import run
import subprocess
import sys
import argparse


global services
services = {"updated_services" : [],
            "going_to_be_updated" : [],
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
        run_update_file = os.path.join(subdir, "run_update")

        if os.path.isfile(docker_compose) and os.access(update_script, os.X_OK) and os.path.isfile(run_update_file):
            services["going_to_be_updated"].append(subdir)
        else:
            print(f"Überspringe '{subdir}': Fehlende 'docker-compose.yaml', 'update.sh' oder 'run_update' Datei.")
            services["not_updated_services"].append(subdir)
            continue
    print(f"Gefundene Verzeichnisse mit 'docker-compose.yaml', 'update.sh' und 'run_update': {services['going_to_be_updated']}")
    for subdir in services["going_to_be_updated"]:
        
        execute_update(subdir)


def execute_update(subdir):
    try:
        subprocess.run(['docker', 'compose', 'pull'], cwd=subdir, check=True)
        subprocess.run(['docker', 'compose', 'up', '-d'], cwd=subdir, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von docker Befehlen in dem Verzeichnis '{subdir}': {e}", file=sys.stderr)
        services["not_updated_services"].append(subdir)
        return

    print(f"Erfolgreich ausgeführt: ' update of docker compose: {subdir}'")
    services["going_to_be_updated"].remove(subdir) if subdir in services["going_to_be_updated"] else None
    services["updated_services"].append(subdir)


def main():
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')
    parser.add_argument('filename')
    args = parser.parse_args()
    run_update_in_subdirs(args.filename)
    
    if len(services["updated_services"])>0:
        print("Updated services:")
        for service in services["updated_services"]:
            print(f" - {service}")
        print("----------------------------")
    print("Services not updated (errors occurred):")
    for service in services["not_updated_services"]:
        print(f" - {service}")


if __name__ == '__main__':
    main()