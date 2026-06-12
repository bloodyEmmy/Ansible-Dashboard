import os
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from werkzeug.utils import secure_filename
import database

app = Flask(__name__)

def bootstrap_system():
    db_exists = os.path.exists('ansible_runs.db')
    playbooks_exist = os.path.exists('playbooks')

    if db_exists and playbooks_exist:
        return

    database.init_db()
    os.makedirs('playbooks', exist_ok=True)

    playbooks_data = {
        "01_nginx_advanced.yml": "---\n- name: Advanced Nginx Setup\n  hosts: webservers\n  become: yes\n  tasks:\n    - name: Ensure Nginx is installed\n      apt:\n        name: nginx\n        state: latest",
        "02_docker_stack.yml": "---\n- name: Deploy Docker Stack\n  hosts: all\n  become: yes\n  tasks:\n    - name: Install Docker CE\n      apt:\n        name: docker-ce\n        state: present",
        "03_k8s_workers.yml": "---\n- name: Join K8s Workers\n  hosts: workers\n  become: yes\n  tasks:\n    - name: Check node status\n      stat:\n        path: /etc/kubernetes/kubelet.conf",
        "04_database_backup.yml": "---\n- name: DB Backup\n  hosts: db_servers\n  become: yes\n  tasks:\n    - name: Create backup dir\n      file:\n        path: /var/backups/postgres\n        state: directory",
        "05_secure_ssh.yml": "---\n- name: Harden SSH\n  hosts: all\n  become: yes\n  tasks:\n    - name: Disable empty passwords\n      lineinfile:\n        path: /etc/ssh/sshd_config\n        regexp: '^#?PermitEmptyPasswords'\n        line: 'PermitEmptyPasswords no'",
        "06_create_users.yml": "---\n- name: Provision Users\n  hosts: all\n  become: yes\n  tasks:\n    - name: Ensure users exist\n      user:\n        name: '{{ item.name }}'\n        state: present",
        "07_setup_firewall.yml": "---\n- name: Configure UFW\n  hosts: all\n  become: yes\n  tasks:\n    - name: Allow SSH\n      ufw:\n        rule: allow\n        port: '22'\n        proto: tcp",
        "08_ssl_renewal.yml": "---\n- name: Renew SSL\n  hosts: webservers\n  become: yes\n  tasks:\n    - name: Run certbot\n      command: certbot renew --quiet",
        "09_nodejs_deploy.yml": "---\n- name: Deploy Node.js\n  hosts: app_servers\n  become: yes\n  tasks:\n    - name: Install Node.js\n      apt:\n        name: nodejs\n        state: present",
        "10_log_rotation.yml": "---\n- name: Configure Logrotate\n  hosts: all\n  become: yes\n  tasks:\n    - name: Deploy config\n      copy:\n        src: files/custom_app.logrotate\n        dest: /etc/logrotate.d/custom_app",
        "11_configure_swap.yml": "---\n- name: Setup Swap\n  hosts: all\n  become: yes\n  tasks:\n    - name: Create swap file\n      command: fallocate -l 2G /swapfile",
        "12_install_zabbix_agent.yml": "---\n- name: Deploy Zabbix\n  hosts: all\n  become: yes\n  tasks:\n    - name: Install zabbix-agent\n      apt:\n        name: zabbix-agent\n        state: present"
    }

    playbooks = []
    for filename, content in playbooks_data.items():
        filepath = os.path.join('playbooks', filename)
        with open(filepath, 'w') as f:
            f.write(content)
        playbooks.append(filename)

    complexity_fail_rates = {
        '03_k8s_workers.yml': 85,
        '08_ssl_renewal.yml': 80,
        '04_database_backup.yml': 75,
        '07_setup_firewall.yml': 70,
        '02_docker_stack.yml': 65,
        '09_nodejs_deploy.yml': 60,
        '12_install_zabbix_agent.yml': 55,
        '01_nginx_advanced.yml': 50,
        '11_configure_swap.yml': 45,
        '10_log_rotation.yml': 40,
        '05_secure_ssh.yml': 35,
        '06_create_users.yml': 30
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
        p_book = random.choice(playbooks)
        user = random.choice(list(users.keys()))
        
        base_fail_rate = complexity_fail_rates.get(p_book, 50)
        final_fail_rate = max(min(base_fail_rate * users[user], 90), 25) 
        
        if random.uniform(0, 100) < final_fail_rate:
            status = 'FAILED'
        else:
            status = 'SUCCESS'
        
        start_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
        end_time = start_time + timedelta(minutes=random.randint(1, 15), seconds=random.randint(0, 59))
        
        cursor.execute('''
            INSERT INTO runs (playbook_name, user, status, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (p_book, user, status, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

bootstrap_system()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def api_history():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user = request.args.get('user')
    playbook = request.args.get('playbook')
    
    try:
        runs = database.get_runs(start_date, end_date, user, playbook)
        return jsonify({"status": "success", "count": len(runs), "data": runs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/playbook/<filename>', methods=['GET'])
def get_playbook(filename):
    safe_name = secure_filename(filename)
    filepath = os.path.join('playbooks', safe_name)
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({"status": "success", "content": content}), 200
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)