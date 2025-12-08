# Kubernetes ngIRCd Deployment Installer

This script automates the process of setting up an **ngIRCd** server deployment on a Kubernetes cluster. It handles downloading the necessary YAML manifests from a GitHub repository, checking for required dependencies, and applying the resources to your cluster in a defined order.

## 🚀 Getting Started

### Prerequisites

* **Python 3**
* **kubectl** command-line tool installed and configured to connect to your Kubernetes cluster.
* **Required Python Libraries:**
    * `yaspin`
    * `fsspec`

You can install the required Python libraries using `pip`:

```bash
pip install yaspin fsspec
```

Alternatively you can use `requirements.txt` for the installation. For example,

```
pip install -r requirements.txt
```

## Usage

Run the script to perform the installation:

```
python3 install-ngIRCd.py
```

## Example Commands

### Installation With Cleanup

This command runs the installation and then deletes the local `./kube` directory.

```
python3 install-ngIRCd.py --clean-up
```

### Dry Run Simulation

This command shows what would be installed without making any changes to the cluster, then cleans up the downloaded files.

```
python3 install-ngIRCd.py --dry-run --clean-up
```

## Cleanup Local Files

If you only want to delete the local YAML files (the `./kube` directory) without running the full installer, you can manually call the cleanup function by modifying and running the script with the `--clean-up` option in combination with `--dry-run` or by executing a specific function within a Python session, or simply by deleting the directory:

```
rm -rf ./kube
```

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit), please see the LICENSE file for details.

The MIT License is a permissive open-source license that allows for for-profit and non-profit use, redistribution, and modification of the software. By contributing to this project, you agree to the terms of the MIT License.
