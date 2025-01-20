import json
import subprocess

# PRE-REQUIREMENTS:
# * anypoint-cli-v4 must be installed and configure to get information from runtime manager in the required environments
# * you have to update the list of environments in the "environments" variable
# * you have to update the list of runtimes and latest versions in the "runtimes" variable
# 
# OUTPUT:
# List of apps that require your attention (JSON format)

# List of environments to check
environments = ["Production", "DisasterRecovery", "UAT", "Development"]

# Runtimes mapping, based on https://docs.mulesoft.com/release-notes/runtime-fabric/runtime-fabric-runtimes-release-notes#runtime-fabric-release-monthly-cadence
runtimes = [
    {"4.3.0": "4.3.0:20240619-4"},
    {"4.4.0": "4.4.0-20241210-2"},
    {"4.5.0": "4.5.4:2e"},
    {"4.6.0": "4.6.10-4-java8"},
    {"4.7.0": "4.7.3:2e-java8"},
    {"4.8.0": "4.8.2-3e-java8"}
]

# Convert runtimes to a more accessible format
runtimes_dict = {list(rt.keys())[0]: list(rt.values())[0] for rt in runtimes}

def fetch_environment_files(environments):
    for env in environments:
        output_file = f"{env}.json"
        command = [
            "anypoint-cli-v4", "runtime-mgr", "application", "list",
            f"--environment={env}", "--output=json"
        ]
        try:
            subprocess.run(command, check=True, stdout=open(output_file, 'w'))
        except subprocess.CalledProcessError as e:
            print(f"Failed to fetch data for environment {env}: {e}")

def check_runtime_versions(environments, runtimes_dict):
    mismatched_records = []

    for env in environments:
        file_name = f"{env}.json"
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                
                for record in data:
                    current_version = record.get("currentRuntimeVersion", "")
                    application_status = record.get("application", {}).get("status", "UNKNOWN")
                    for runtime_key, runtime_value in runtimes_dict.items():
                        if current_version.startswith(runtime_key):
                            if current_version != runtime_value:
                                mismatched_records.append({
                                    "environment": env,
                                    "name": record.get("name"),
                                    "currentVersion": current_version,
                                    "expectedVersion": runtime_value,
                                    "status": application_status
                                })
        except FileNotFoundError:
            print(f"File not found: {file_name}")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in file: {file_name}")

    return mismatched_records

# Fetch environment files
fetch_environment_files(environments)

# Check for mismatched runtime versions
mismatched_records = check_runtime_versions(environments, runtimes_dict)

# Output the mismatched records as valid JSON
output = {
    "mismatched_records": mismatched_records
}
print(json.dumps(output, indent=2))
