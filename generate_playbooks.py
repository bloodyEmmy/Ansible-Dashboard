import os

playbooks_data = {
    "01_nginx_advanced.yml": """---
- name: Advanced Nginx Setup with Handlers
  hosts: webservers
  become: yes
  vars:
    nginx_port: 8080
    app_user: www-data
  tasks:
    - name: Ensure Nginx is installed
      apt:
        name: nginx
        state: latest
    - name: Deploy custom nginx.conf
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx
    - name: Ensure Nginx is running
      service:
        name: nginx
        state: started
        enabled: yes
  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
""",
    "02_docker_stack.yml": """---
- name: Deploy Docker and Docker Compose
  hosts: all
  become: yes
  tasks:
    - name: Install dependencies for Docker
      apt:
        name: "{{ item }}"
        state: present
      loop:
        - apt-transport-https
        - ca-certificates
        - curl
        - gnupg-agent
    - name: Add Docker GPG key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present
    - name: Install Docker CE
      apt:
        name: docker-ce
        state: present
    - name: Add current user to docker group
      user:
        name: "{{ ansible_user }}"
        groups: docker
        append: yes
""",
    "03_k8s_workers.yml": """---
- name: Join Kubernetes Worker Nodes
  hosts: workers
  become: yes
  vars:
    master_ip: "10.0.0.50"
    join_token: "abcdef.1234567890abcdef"
  tasks:
    - name: Check if node is already in cluster
      stat:
        path: /etc/kubernetes/kubelet.conf
      register: kubelet_conf
    - name: Join the cluster
      command: kubeadm join {{ master_ip }}:6443 --token {{ join_token }} --discovery-token-unsafe-skip-ca-verification
      when: not kubelet_conf.stat.exists
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
        mode: '0700'
        owner: postgres
    - name: Execute pg_dump
      command: pg_dumpall > /var/backups/postgres/dump_{{ ansible_date_time.date }}.sql
      become_user: postgres
    - name: Archive the dump
      archive:
        path: /var/backups/postgres/dump_{{ ansible_date_time.date }}.sql
        dest: /var/backups/postgres/dump_{{ ansible_date_time.date }}.gz
        remove: yes
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
      notify: reload sshd
    - name: Change default SSH port
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?Port 22'
        line: 'Port 2222'
      notify: reload sshd
  handlers:
    - name: reload sshd
      service:
        name: sshd
        state: reloaded
""",
    "06_create_users.yml": """---
- name: Provision System Users
  hosts: all
  become: yes
  vars:
    sys_users:
      - { name: 'dev_intern', shell: '/bin/bash' }
      - { name: 'audit_admin', shell: '/bin/sh' }
  tasks:
    - name: Ensure users exist
      user:
        name: "{{ item.name }}"
        shell: "{{ item.shell }}"
        state: present
      loop: "{{ sys_users }}"
"""
}

os.makedirs('playbooks', exist_ok=True)
for filename, content in playbooks_data.items():
    with open(os.path.join('playbooks', filename), 'w') as f:
        f.write(content)
print("Сложные плейбуки сгенерированы.")