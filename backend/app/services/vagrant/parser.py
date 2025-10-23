import re
from typing import Dict, Any, List, Optional


class VagrantfileParser:
    """
    Parse existing Vagrantfiles and extract configuration.

    This is a basic parser that extracts common Vagrant configurations.
    For complex Ruby DSL, this may not capture everything, but handles
    the most common use cases.
    """

    def parse(self, vagrantfile_content: str) -> Dict[str, Any]:
        """Parse a Vagrantfile and extract configuration"""
        config = {
            "box": None,
            "box_version": None,
            "hostname": None,
            "provider": "virtualbox",
            "cpus": None,
            "memory": None,
            "networks": [],
            "synced_folders": [],
            "provisioners": [],
            "provider_config": {}
        }

        # Extract box name
        box_match = re.search(r'config\.vm\.box\s*=\s*["\']([^"\']+)["\']', vagrantfile_content)
        if box_match:
            config["box"] = box_match.group(1)

        # Extract box version
        version_match = re.search(r'config\.vm\.box_version\s*=\s*["\']([^"\']+)["\']', vagrantfile_content)
        if version_match:
            config["box_version"] = version_match.group(1)

        # Extract hostname
        hostname_match = re.search(r'config\.vm\.hostname\s*=\s*["\']([^"\']+)["\']', vagrantfile_content)
        if hostname_match:
            config["hostname"] = hostname_match.group(1)

        # Extract provider (look for config.vm.provider blocks)
        provider_match = re.search(r'config\.vm\.provider\s+["\']?(\w+)["\']?\s+do', vagrantfile_content)
        if provider_match:
            config["provider"] = provider_match.group(1)

        # Extract CPU and memory (VirtualBox syntax)
        cpus_match = re.search(r'vb\.cpus\s*=\s*(\d+)', vagrantfile_content)
        if cpus_match:
            config["cpus"] = int(cpus_match.group(1))

        memory_match = re.search(r'vb\.memory\s*=\s*["\']?(\d+)["\']?', vagrantfile_content)
        if memory_match:
            config["memory"] = int(memory_match.group(1))

        # Extract networks
        network_patterns = [
            r'config\.vm\.network\s+["\']private_network["\'],\s*ip:\s*["\']([^"\']+)["\']',
            r'config\.vm\.network\s+["\']public_network["\'](?:,\s*bridge:\s*["\']([^"\']+)["\'])?',
            r'config\.vm\.network\s+["\']forwarded_port["\'],\s*guest:\s*(\d+),\s*host:\s*(\d+)'
        ]

        for pattern in network_patterns:
            for match in re.finditer(pattern, vagrantfile_content):
                if "private_network" in pattern:
                    config["networks"].append({
                        "type": "private_network",
                        "ip": match.group(1)
                    })
                elif "public_network" in pattern:
                    network = {"type": "public_network"}
                    if match.group(1):
                        network["bridge"] = match.group(1)
                    config["networks"].append(network)
                elif "forwarded_port" in pattern:
                    config["networks"].append({
                        "type": "forwarded_port",
                        "guest_port": int(match.group(1)),
                        "host_port": int(match.group(2))
                    })

        # Extract synced folders
        synced_folder_pattern = r'config\.vm\.synced_folder\s+["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']'
        for match in re.finditer(synced_folder_pattern, vagrantfile_content):
            config["synced_folders"].append({
                "host_path": match.group(1),
                "guest_path": match.group(2)
            })

        # Extract shell provisioners (inline)
        inline_provision_pattern = r'config\.vm\.provision\s+["\']shell["\'],\s*inline:\s*<<-SHELL(.*?)SHELL'
        for match in re.finditer(inline_provision_pattern, vagrantfile_content, re.DOTALL):
            script_content = match.group(1).strip()
            config["provisioners"].append({
                "type": "shell",
                "inline": [line.strip() for line in script_content.split('\n') if line.strip()]
            })

        # Extract shell provisioners (path)
        path_provision_pattern = r'config\.vm\.provision\s+["\']shell["\'],\s*path:\s*["\']([^"\']+)["\']'
        for match in re.finditer(path_provision_pattern, vagrantfile_content):
            config["provisioners"].append({
                "type": "shell",
                "path": match.group(1)
            })

        return config

    def validate(self, vagrantfile_content: str) -> bool:
        """
        Basic validation of Vagrantfile syntax.
        Returns True if basic structure is valid.
        """
        # Check for basic Vagrant.configure block
        if 'Vagrant.configure' not in vagrantfile_content:
            return False

        # Check for balanced do...end blocks
        do_count = len(re.findall(r'\bdo\b', vagrantfile_content))
        end_count = len(re.findall(r'\bend\b', vagrantfile_content))

        if do_count != end_count:
            return False

        # Check for at least a box definition
        if not re.search(r'config\.vm\.box\s*=', vagrantfile_content):
            return False

        return True

    def extract_provider_config(self, vagrantfile_content: str, provider: str) -> Dict[str, Any]:
        """Extract provider-specific configuration"""
        provider_config = {}

        # Find provider block
        provider_block_pattern = rf'config\.vm\.provider\s+["\']?{provider}["\']?\s+do\s*\|(\w+)\|(.*?)end'
        match = re.search(provider_block_pattern, vagrantfile_content, re.DOTALL)

        if match:
            provider_var = match.group(1)
            block_content = match.group(2)

            # Extract key-value assignments
            assignment_pattern = rf'{provider_var}\.(\w+)\s*=\s*["\']?([^"\'\n]+)["\']?'
            for assignment in re.finditer(assignment_pattern, block_content):
                key = assignment.group(1)
                value = assignment.group(2).strip()

                # Try to convert to appropriate type
                try:
                    if value.isdigit():
                        provider_config[key] = int(value)
                    elif value.lower() in ('true', 'false'):
                        provider_config[key] = value.lower() == 'true'
                    else:
                        provider_config[key] = value
                except:
                    provider_config[key] = value

        return provider_config
