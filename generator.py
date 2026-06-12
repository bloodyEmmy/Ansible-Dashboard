import os
import random
from datetime import datetime, timedelta
import database

PLAYBOOKS_DATA = {
    "01_docker_production.yml": """---
- name: Install and Configure Docker CE
  hosts: all
  become: true
  tasks:
    - name: Install required dependencies
      apt:
        name: ['apt-transport-https', 'ca-certificates', 'curl', 'gnupg', 'lsb-release']
        state: present
        update_cache: true
    - name: Add Docker GPG apt Key
      apt_key:
        url: https://download.docker.com/linux/ubuntu/gpg
        state: present
    - name: Add Docker Repository
      apt_repository:
        repo: deb https://download.docker.com/linux/ubuntu focal stable
        state: present
    - name: Install Docker Engine
      apt:
        name: ['docker-ce', 'docker-ce-cli', 'containerd.io']
        state: present
    - name: Ensure Docker service is running and enabled
      systemd:
        name: docker
        state: started
        enabled: true""",

    "02_nginx_ssl_deploy.yml": """---
- name: Deploy Nginx with Let's Encrypt
  hosts: webservers
  become: true
  tasks:
    - name: Install Nginx and Certbot
      apt:
        name: ['nginx', 'certbot', 'python3-certbot-nginx']
        state: present
    - name: Copy Nginx site configuration
      template:
        src: templates/site.conf.j2
        dest: /etc/nginx/sites-available/my_site
      notify: Reload Nginx
    - name: Enable site
      file:
        src: /etc/nginx/sites-available/my_site
        dest: /etc/nginx/sites-enabled/my_site
        state: link
      notify: Reload Nginx
  handlers:
    - name: Reload Nginx
      service:
        name: nginx
        state: reloaded""",

    "03_ssh_hardening.yml": """---
- name: Hardening SSH Server (CIS Benchmarks)
  hosts: all
  become: true
  tasks:
    - name: Disable Root Login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PermitRootLogin'
        line: 'PermitRootLogin no'
      notify: Restart SSH
    - name: Disable Password Authentication
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?PasswordAuthentication'
        line: 'PasswordAuthentication no'
      notify: Restart SSH
    - name: Set SSH Idle Timeout Interval
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^#?ClientAliveInterval'
        line: 'ClientAliveInterval 300'
      notify: Restart SSH
  handlers:
    - name: Restart SSH
      service:
        name: sshd
        state: restarted""",

    "04_user_provisioning.yml": """---
- name: Provision System Administrators
  hosts: all
  become: true
  vars:
    admin_users:
      - v.proskuryakov
      - a.ivanov
      - devops_deploy
  tasks:
    - name: Ensure admin group exists
      group:
        name: sysadmins
        state: present
    - name: Create user accounts
      user:
        name: "{{ item }}"
        groups: sysadmins
        shell: /bin/bash
        append: true
      loop: "{{ admin_users }}"
    - name: Add authorized SSH keys
      authorized_key:
        user: "{{ item }}"
        state: present
        key: "https://github.com/{{ item }}.keys"
      loop: "{{ admin_users }}"
    - name: Allow sysadmins to use sudo without password
      copy:
        dest: /etc/sudoers.d/sysadmins
        content: "%sysadmins ALL=(ALL) NOPASSWD: ALL"
        validate: /usr/sbin/visudo -cf %s""",

    "05_postgresql_setup.yml": """---
- name: Setup PostgreSQL Database Server
  hosts: db_servers
  become: true
  vars:
    db_name: app_database
    db_user: app_user
    db_password: "SuperSecretPassword123!"
  tasks:
    - name: Install PostgreSQL and dependencies
      apt:
        name: ['postgresql', 'postgresql-contrib', 'python3-psycopg2']
        state: present
    - name: Ensure PostgreSQL is running
      service:
        name: postgresql
        state: started
        enabled: true
    - name: Create application database
      postgresql_db:
        name: "{{ db_name }}"
        state: present
      become_user: postgres
    - name: Create database user
      postgresql_user:
        db: "{{ db_name }}"
        name: "{{ db_user }}"
        password: "{{ db_password }}"
        priv: "ALL"
      become_user: postgres""",

    "06_ufw_firewall.yml": """---
- name: Configure UFW Firewall
  hosts: all
  become: true
  tasks:
    - name: Install UFW
      apt:
        name: ufw
        state: present
    - name: Set default deny incoming
      ufw:
        default: deny
        direction: incoming
    - name: Set default allow outgoing
      ufw:
        default: allow
        direction: outgoing
    - name: Allow SSH, HTTP, and HTTPS
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - '22'
        - '80'
        - '443'
    - name: Enable UFW
      ufw:
        state: enabled
        logging: 'on'""",

    "07_system_updates_reboot.yml": """---
- name: Patch Management and Reboot
  hosts: all
  become: true
  tasks:
    - name: Update apt repo and cache
      apt:
        update_cache: true
        force_apt_get: true
        cache_valid_time: 3600
    - name: Upgrade all packages
      apt:
        upgrade: dist
        force_apt_get: true
    - name: Check if a reboot is required
      stat:
        path: /var/run/reboot-required
      register: reboot_required_file
    - name: Reboot server if necessary
      reboot:
        msg: "Reboot initiated by Ansible after system updates"
        connect_timeout: 5
        reboot_timeout: 300
        pre_reboot_delay: 0
        post_reboot_delay: 30
      when: reboot_required_file.stat.exists""",

    "08_prometheus_node_exporter.yml": """---
- name: Deploy Prometheus Node Exporter
  hosts: all
  become: true
  vars:
    exporter_version: "1.6.1"
  tasks:
    - name: Create node_exporter system group
      group:
        name: node_exporter
        system: true
    - name: Create node_exporter system user
      user:
        name: node_exporter
        system: true
        group: node_exporter
        shell: /usr/sbin/nologin
    - name: Download Node Exporter
      unarchive:
        src: "https://github.com/prometheus/node_exporter/releases/download/v{{ exporter_version }}/node_exporter-{{ exporter_version }}.linux-amd64.tar.gz"
        dest: /tmp
        remote_src: true
    - name: Move binary to /usr/local/bin
      copy:
        src: "/tmp/node_exporter-{{ exporter_version }}.linux-amd64/node_exporter"
        dest: /usr/local/bin/node_exporter
        owner: node_exporter
        group: node_exporter
        mode: '0755'
        remote_src: true""",

    "09_k8s_kubelet_deploy.yml": """---
- name: Deploy Kubernetes Kubelet
  hosts: k8s_nodes
  become: true
  tasks:
    - name: Disable Swap (Required for K8s)
      command: swapoff -a
      when: ansible_swaptotal_mb > 0
    - name: Remove Swap from fstab
      mount:
        name: "{{ item }}"
        fstype: swap
        state: absent
      loop:
        - none
        - swap
    - name: Add Kubernetes GPG key
      apt_key:
        url: https://packages.cloud.google.com/apt/doc/apt-key.gpg
        state: present
    - name: Install kubelet, kubeadm and kubectl
      apt:
        name: ['kubelet', 'kubeadm', 'kubectl']
        state: present
        update_cache: true""",

    "10_logrotate_custom.yml": """---
- name: Configure Log Rotation for App
  hosts: all
  become: true
  tasks:
    - name: Ensure log directory exists
      file:
        path: /var/log/my_app
        state: directory
        owner: root
        group: syslog
        mode: '0755'
    - name: Deploy custom logrotate configuration
      blockinfile:
        path: /etc/logrotate.d/my_app
        create: true
        block: |
          /var/log/my_app/*.log {
              daily
              missingok
              rotate 14
              compress
              delaycompress
              notifempty
              create 0640 root syslog
              sharedscripts
              postrotate
                  systemctl reload my_app > /dev/null 2>/dev/null || true
              endscript
          }"""
}

def bootstrap_system():
    db_exists = os.path.exists('ansible_runs.db')
    playbooks_exist = os.path.exists('playbooks')

    if db_exists and playbooks_exist:
        print("База данных и плейбуки уже существуют. Генерация пропущена.")
        return

    print("Генерация новых тестовых данных...")
    database.init_db()
    os.makedirs('playbooks', exist_ok=True)
    
    playbook_names = []
    for filename, content in PLAYBOOKS_DATA.items():
        filepath = os.path.join('playbooks', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        playbook_names.append(filename)

    complexity_fail_rates = {
        '09_k8s_kubelet_deploy.yml': 70,
        '05_postgresql_setup.yml': 55,
        '02_nginx_ssl_deploy.yml': 45,
        '01_docker_production.yml': 30,
        '03_ssh_hardening.yml': 25,
        '08_prometheus_node_exporter.yml': 20,
        '04_user_provisioning.yml': 15,
        '07_system_updates_reboot.yml': 10,
        '06_ufw_firewall.yml': 5,
        '10_logrotate_custom.yml': 2
    }

    users = {
        'v.proskuryakov': 1.0, 'd.yaguzhinsky': 0.7, 't.bessoltsev': 1.5, 's.rastorguev': 0.8,
        'a.lebedev': 1.2, 'm.sokolov': 0.9, 'k.orlov': 1.1, 'e.volkova': 0.6,
        'n.makarov': 1.3, 'p.morozov': 0.8, 'r.fomin': 1.4, 'o.zaytseva': 0.7,
        'gitlab-runner': 0.3, 'jenkins-agent': 0.3, 'ansible-tower': 0.2, 'cron-daemon': 0.4
    }

    conn = database.get_connection()
    cursor = conn.cursor()
    now = datetime.now()

    for _ in range(150):
        p_book = random.choice(playbook_names)
        user = random.choice(list(users.keys()))
        
        base_fail_rate = complexity_fail_rates.get(p_book, 50)
        final_fail_rate = max(min(base_fail_rate * users[user], 90), 5) 
        
        status = 'FAILED' if random.uniform(0, 100) < final_fail_rate else 'SUCCESS'
        
        start_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
        end_time = start_time + timedelta(minutes=random.randint(1, 15), seconds=random.randint(0, 59))
        
        cursor.execute('''
            INSERT INTO runs (playbook_name, user, status, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (p_book, user, status, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()
    print("Генерация завершена успешно!")

if __name__ == '__main__':
    bootstrap_system()