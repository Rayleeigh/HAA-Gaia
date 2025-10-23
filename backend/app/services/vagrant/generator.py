from jinja2 import Template
from typing import Dict, Any, Optional


class VagrantfileGenerator:
    """
    Generate Vagrantfiles from configuration dictionaries.
    Uses Jinja2 templates for flexible generation.
    """

    def __init__(self):
        self.template = self._get_base_template()

    def generate(self, config: Dict[str, Any]) -> str:
        """Generate a Vagrantfile from configuration"""
        return self.template.render(config)

    def _get_base_template(self) -> Template:
        """Get the base Vagrantfile template"""
        template_str = '''# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Base box configuration
  config.vm.box = "{{ box }}"
  {%- if box_version %}
  config.vm.box_version = "{{ box_version }}"
  {%- endif %}
  {%- if box_url %}
  config.vm.box_url = "{{ box_url }}"
  {%- endif %}
  {%- if hostname %}
  config.vm.hostname = "{{ hostname }}"
  {%- endif %}

  {%- if networks %}
  # Network configuration
  {%- for network in networks %}
  {%- if network.type == "private_network" %}
  config.vm.network "private_network", ip: "{{ network.ip }}"
  {%- elif network.type == "public_network" %}
  config.vm.network "public_network"{% if network.bridge %}, bridge: "{{ network.bridge }}"{% endif %}
  {%- elif network.type == "forwarded_port" %}
  config.vm.network "forwarded_port", guest: {{ network.guest_port }}, host: {{ network.host_port }}
  {%- endif %}
  {%- endfor %}
  {%- endif %}

  {%- if synced_folders %}
  # Synced folders
  {%- for folder in synced_folders %}
  config.vm.synced_folder "{{ folder.host_path }}", "{{ folder.guest_path }}"
  {%- if folder.type %}, type: "{{ folder.type }}"{% endif %}
  {%- endfor %}
  {%- endif %}

  # Provider-specific configuration
  config.vm.provider "{{ provider }}" do |{{ provider[:2] }}|
    {%- if cpus %}
    {{ provider[:2] }}.cpus = {{ cpus }}
    {%- endif %}
    {%- if memory %}
    {{ provider[:2] }}.memory = {{ memory }}
    {%- endif %}
    {%- if provider_config %}
    {%- for key, value in provider_config.items() %}
    {{ provider[:2] }}.{{ key }} = {% if value is string %}"{{ value }}"{% else %}{{ value }}{% endif %}
    {%- endfor %}
    {%- endif %}
  end

  {%- if provisioners %}
  # Provisioning
  {%- for provisioner in provisioners %}
  {%- if provisioner.type == "shell" %}
  {%- if provisioner.inline %}
  config.vm.provision "shell", inline: <<-SHELL
    {%- for line in provisioner.inline %}
    {{ line }}
    {%- endfor %}
  SHELL
  {%- elif provisioner.path %}
  config.vm.provision "shell", path: "{{ provisioner.path }}"
  {%- endif %}
  {%- elif provisioner.type == "ansible" %}
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "{{ provisioner.playbook }}"
  end
  {%- endif %}
  {%- endfor %}
  {%- endif %}

  {%- if custom_config %}
  # Custom configuration
  {{ custom_config }}
  {%- endif %}
end
'''
        return Template(template_str)

    def generate_proxmox(self, config: Dict[str, Any]) -> str:
        """Generate a Proxmox-specific Vagrantfile"""
        proxmox_template = '''# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "{{ box }}"
  {%- if hostname %}
  config.vm.hostname = "{{ hostname }}"
  {%- endif %}

  config.vm.provider :proxmox do |proxmox, override|
    proxmox.endpoint = "{{ provider_config.endpoint }}"
    proxmox.user_name = "{{ provider_config.user_name }}"
    proxmox.password = "{{ provider_config.password }}"

    # VM configuration
    proxmox.vm_name = "{{ name }}"
    {%- if provider_config.node %}
    proxmox.node = "{{ provider_config.node }}"
    {%- endif %}
    {%- if cpus %}
    proxmox.vm_cpu_cores = {{ cpus }}
    {%- endif %}
    {%- if memory %}
    proxmox.vm_memory = {{ memory }}
    {%- endif %}
    {%- if provider_config.storage %}
    proxmox.vm_storage = "{{ provider_config.storage }}"
    {%- endif %}
    {%- if provider_config.disk_size %}
    proxmox.vm_disk_size = "{{ provider_config.disk_size }}"
    {%- endif %}

    # Network configuration
    {%- if networks %}
    {%- for network in networks %}
    proxmox.vm_network_bridge = "{{ network.bridge or 'vmbr0' }}"
    {%- endfor %}
    {%- endif %}
  end

  {%- if provisioners %}
  # Provisioning
  {%- for provisioner in provisioners %}
  {%- if provisioner.type == "shell" %}
  {%- if provisioner.inline %}
  config.vm.provision "shell", inline: <<-SHELL
    {%- for line in provisioner.inline %}
    {{ line }}
    {%- endfor %}
  SHELL
  {%- elif provisioner.path %}
  config.vm.provision "shell", path: "{{ provisioner.path }}"
  {%- endif %}
  {%- endif %}
  {%- endfor %}
  {%- endif %}
end
'''
        template = Template(proxmox_template)
        return template.render(config)

    def generate_from_template(self, template_content: str, config: Dict[str, Any]) -> str:
        """Generate a Vagrantfile from a custom template"""
        template = Template(template_content)
        return template.render(config)
