#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys
import shutil
import time
import fsspec
from yaspin import yaspin
from pathlib import Path

YAML_DIR = "./kube"

DEPLOYMENT_ORDER = [
    "ngircd-namespace.yml",
    "ngircd-deployment.yml",
    "ngircd-service.yml"
]

def create_kube_directory():
    if not os.path.exists(YAML_DIR):
        os.makedirs(YAML_DIR)

def download_dependencies():
    """ Downloads the dependencies from GitHub. """
    cwd = Path.cwd() / 'kube'
    fs = fsspec.filesystem("github", org="jremes-foss", repo="kube-ngircd")
    with yaspin(text="Downloading manifests ...", color="cyan") as sp:
        fs.get(fs.ls("kube/"), cwd.as_posix())
        sp.ok("✔")

def check_dependencies():
    print("[+] Checking dependencies ...")
    try:
        subprocess.run(["kubectl", "version", "--client"], check=True, stdout=subprocess.DEVNULL)
        print("[!] kubectl is installed.")

        try:
            current_context = subprocess.check_output(["kubectl", "config", "current-context"], text=True).strip()
            print(f"[+] Kubernetes context is set to: {current_context}")
        except subprocess.CalledProcessError:
            print("[!] No Kubernetes context is set. Please run 'kubectl config use <context-name>' and try again.")
            sys.exit(1)

    except FileNotFoundError:
        print("[!] kubectl command not found. Please ensure it is installed and in your PATH.")
        sys.exit(1)
    print("[+] Dependency check complete!")
    print("\n")

def clean_kube_manifests():
    """ Deletes the YAML files from local hard drive. """
    shutil.rmtree("./kube", ignore_errors=False, onerror=None)

def install_deployment():
    """Applies all YAML files in the specified directory."""
    print("[+] Starting Kubernetes deployment ...")

    if not os.path.isdir(YAML_DIR):
        print(f"[!] Error: The directory '{YAML_DIR}' does not exist.")
        sys.exit(1)

    files_to_deploy = []

    if DEPLOYMENT_ORDER:
        print("[+] Applying files in a predefined order.")
        for filename in DEPLOYMENT_ORDER:
            filepath = os.path.join(YAML_DIR, filename)
            if os.path.isfile(filepath):
                files_to_deploy.append(filepath)
            else:
                print(f"[!] Warning: Predefined file '{filename}' not found. Skipping.")
    else:
        print("[!] No predefined order. Applying all YAMLs found.")
        for filename in os.listdir(YAML_DIR):
            if filename.endswith((".yaml", ".yml")):
                files_to_deploy.append(os.path.join(YAML_DIR, filename))

    if not files_to_deploy:
        print("[!] No YAML files found to deploy.")
        sys.exit(1)

    for i, yaml_file in enumerate(files_to_deploy):
        print(f"[+] Applying {os.path.basename(yaml_file)}...")
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", yaml_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"[+] Successfully applied {os.path.basename(yaml_file)}")
        except subprocess.CalledProcessError as e:
            print("[!] Error applying {os.path.basename(yaml_file)}:")
            print(e.stderr)
            sys.exit(1)

        if i < len(files_to_deploy) - 1:
            with yaspin(text="Pending ...") as sp:
                time.sleep(2)
                sp.ok("✔")
            print()

    print("[✔] Kubernetes deployment complete!")

def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(description="A script to install ngIRCd K8s deployment.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the installation without making changes."
    )
    parser.add_argument(
        "--clean-up",
        action="store_true",
        help="Clean up the YML files after installation or dry run."
    )
    args = parser.parse_args()

    create_kube_directory()
    download_dependencies()

    if args.dry_run:
        print("--- Dry Run Mode ---")
        print("This script would check dependencies and attempt to apply the following files:")
        
        if os.path.isdir(YAML_DIR):
            files = []
            if DEPLOYMENT_ORDER:
                for filename in DEPLOYMENT_ORDER:
                    if os.path.isfile(os.path.join(YAML_DIR, filename)):
                        files.append(filename)
            else:
                files = [f for f in os.listdir(YAML_DIR) if f.endswith((".yaml", ".yml"))]
            
            for f in files:
                print(f"- {f}")
        else:
            print(f"The specified directory '{YAML_DIR}' does not exist.")
        
        if args.clean_up:
            clean_kube_manifests()
            print("[+] Resources deleted.")
        
        print("\n--- End of Dry Run ---")
        
        return

    check_dependencies()
    install_deployment()

    if args.clean_up:
        clean_kube_manifests()
        print("[+] Resources deleted.")

if __name__ == "__main__":
    main()
