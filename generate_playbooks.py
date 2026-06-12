import os

playbooks_data = {
    "01_nginx_advanced.yml": """---
- name: Advanced Nginx Setup with Handlers
  hosts: webservers
  become: yes
  tasks:
    - name: Ensure Nginx is installed
      apt:
        name: nginx
        state: latest
""",
    "02_docker_stack.yml": """---
- name: Deploy Docker and Docker Compose
  hosts: all
  become: yes
  tasks:
    - name: Install Docker CE
      apt:
        name: docker-ce
        state: present
""",
    "03_k8s_workers.yml": """---
- name: Join Kubernetes Worker Nodes
  hosts: workers
  become: yes
  tasks:
    - name: Check if node is already in cluster
      stat:
        path: /etc/kubernetes/kubelet.conf
""",
    "04_database_backup.yml": """---
- name: Automated Database Backup
  hosts: db_servers
  become: yes
  tasks:
    - name: Create backup directory
      file:
        path: /var/backups/postgres
        state: directory
""",
    "05_secure_ssh.yml": """---
- name: Hardening SSH Daemon
  hosts: all
  become: yes
  tasks:
    - name: Disable empty passwords
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitEmptyPasswords'
        line: 'PermitEmptyPasswords no'
""",
    "06_create_users.yml": """---
- name: Provision System Users
  hosts: all
  become: yes
  tasks:
    - name: Ensure users exist
      user:
        name: "{{ item.name }}"
        state: present
""",
    "07_setup_firewall.yml": """---
- name: Configure UFW Firewall
  hosts: all
  become: yes
  tasks:
    - name: Allow SSH
      ufw:
        rule: allow
        port: '22'
        proto: tcp
    - name: Enable UFW
      ufw:
        state: enabled
""",
    "08_ssl_renewal.yml": """---
- name: Renew Let's Encrypt Certificates
  hosts: webservers
  become: yes
  tasks:
    - name: Run certbot renew
      command: certbot renew --quiet
      register: certbot_output
""",
    "09_nodejs_deploy.yml": """---
- name: Deploy Node.js Application
  hosts: app_servers
  become: yes
  tasks:
    - name: Install Node.js
      apt:
        name: nodejs
        state: present
    - name: Install PM2 globally
      npm:
        name: pm2
        global: yes
""",
    "10_log_rotation.yml": """---
- name: Configure Logrotate
  hosts: all
  become: yes
  tasks:
    - name: Deploy custom logrotate config
      copy:
        src: files/custom_app.logrotate
        dest: /etc/logrotate.d/custom_app
        mode: '0644'
""",
    "11_configure_swap.yml": """---
- name: Setup Swap Space
  hosts: all
  become: yes
  tasks:
    - name: Create swap file
      command: fallocate -l 2G /swapfile
      args:
        creates: /swapfile
    - name: Make swap file executable
      command: mkswap /swapfile
""",
    "12_install_zabbix_agent.yml": """---
- name: Deploy Zabbix Agent
  hosts: all
  become: yes
  tasks:
    - name: Install zabbix-agent
      apt:
        name: zabbix-agent
        state: present
    - name: Start Zabbix service
      service:
        name: zabbix-agent
        state: started
        enabled: yes
"""
}

os.makedirs('playbooks', exist_ok=True)
for filename, content in playbooks_data.items():
    with open(os.path.join('playbooks', filename), 'w') as f:
        f.write(content)
print("Сложные плейбуки сгенерированы.")