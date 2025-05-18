# Ansible Docker Swarm PostgreSQL Role

> An Ansible role to deploy a PostgreSQL service to a Docker Swarm cluster with support for user management, database creation, and pg_dump backups with rclone remote storage.

## Requirements

- Docker installed on the target machine
- Docker Swarm initialized on the target machine
- An overlay network for the swarm services

## Installation

### Using Ansible Galaxy

You can install this role directly from Ansible Galaxy:

```bash
ansible-galaxy install brpaz.swarm_postgres
```

### Using requirements.yml

For version-controlled, repeatable role installations, add to your `requirements.yml`:

```yaml
---
roles:
  - name: brpaz.swarm_postgres
    version: v1.0.0  # Specify the version you want

collections:
  - name: community.docker
  - name: community.postgresql
```

Then install with:

```bash
ansible-galaxy install -r requirements.yml
```

### Manual Installation

Alternatively, you can clone the repository directly:

```bash
# Create a roles directory if it doesn't exist
mkdir -p ~/.ansible/roles
# Clone the repository
git clone https://github.com/brpaz/ansible-role-swarm-postgres.git ~/.ansible/roles/brpaz.swarm_postgres
```

## Role Variables

This role includes the following variables for configuration:

### Core PostgreSQL Configuration

| Variable                      | Default Value          | Description                            |
| ----------------------------- | ---------------------- | -------------------------------------- |
| `postgres_service_name`       | `postgres`             | Name of the PostgreSQL service         |
| `postgres_image`              | `postgres`             | PostgreSQL Docker image                |
| `postgres_version`            | `17.4`                 | PostgreSQL version to use              |
| `postgres_port`               | `5432`                 | Port PostgreSQL will listen on         |
| `postgres_cpu_reservation`    | `0.2`                  | CPU reservation for the container      |
| `postgres_cpu_limit`          | `1`                    | CPU limit for the container            |
| `postgres_memory_reservation` | `128M`                 | Memory reservation for the container   |
| `postgres_memory_limit`       | `1G`                   | Memory limit for the container         |
| `postgres_networks`           | `[]`                   | List of networks to attach to          |
| `postgres_environment`        | `[]`                   | Additional environment variables       |
| `postgres_client_package`     | `postgresql-client-17` | PostgreSQL client package to install   |
| `postgres_root_password`      | `postgres`             | PostgreSQL root user password          |
| `postgres_max_connections`    | `100`                  | Maximum number of database connections |
| `postgres_shared_buffers`     | `128MB`                | Shared buffers configuration           |
| `postgres_custom_conf`        | `{}`                   | Custom PostgreSQL configuration        |

### WAL Settings

| Variable                   | Default Value | Description                       |
| -------------------------- | ------------- | --------------------------------- |
| `postgres_wal_enabled`     | `false`       | Whether to enable WAL archiving   |
| `postgres_wal_level`       | `replica`     | WAL level                         |
| `postgres_wal_min_size`    | `80MB`        | Minimum WAL size                  |
| `postgres_wal_max_size`    | `1GB`         | Maximum WAL size                  |
| `postgres_archive_command` | `""`          | Archive command for WAL archiving |
| `postgres_archive_mode`    | `on`          | Archive mode                      |
| `postgres_archive_timeout` | `60s`         | Archive timeout                   |

### User and Database Management

| Variable             | Default Value | Description                                      |
| -------------------- | ------------- | ------------------------------------------------ |
| `postgres_databases` | `[]`          | List of databases to create                      |
| `postgres_users`     | `[]`          | List of users to create with optional privileges |

Example database format:
```yaml
postgres_databases:
  - name: app_db
    owner: app_user  # Optional
    encoding: UTF8    # Optional
    lc_collate: en_US.UTF-8  # Optional
    lc_ctype: en_US.UTF-8  # Optional
    template: template0  # Optional
```

Example user format:
```yaml
postgres_users:
  - name: app_user
    password: secure_password
    roles: ["CREATEDB", "LOGIN"]  # Optional
    privileges:  # Optional
      - database: app_db
        type: schema
        objs: public
        privileges: ALL
```

### Backup Configuration

#### pg_dump Backup Settings

| Variable                         | Default Value           | Description                                   |
| -------------------------------- | ----------------------- | --------------------------------------------- |
| `postgres_backup_enabled`        | `false`                 | Whether to enable pg_dump backups             |
| `postgres_backup_dir`            | `/var/backups/postgres` | Directory for backups                         |
| `postgres_backup_keep_days`      | `7`                     | Days to keep backups                          |
| `postgres_backup_hour`           | `02`                    | Hour to run backup (24-hour format)           |
| `postgres_backup_minute`         | `00`                    | Minute to run backup                          |
| `postgres_backup_format`         | `custom`                | Backup format (plain, custom, directory, tar) |
| `postgres_backup_compress`       | `true`                  | Whether to compress backups                   |
| `postgres_backup_databases`      | `[]`                    | List of databases to backup (empty = all)     |
| `postgres_backup_rclone_enabled` | `false`                 | Whether to use rclone for remote backups      |
| `postgres_backup_rclone_remote`  | ``                      | Rclone remote destination                     |
| `postgres_backup_rclone_args`    | `--progress`            | Additional arguments for rclone command       |
| `postgres_backup_prune_enabled`  | `true`                  | Whether to enable pruning of old backups      |

#### Remote Backups with Rclone

This role supports backing up PostgreSQL databases to remote storage using rclone.

##### How It Works

1. Local backups are created using pg_dump in the configured format
2. If rclone is enabled, all backups are uploaded to the specified remote destination
3. After successful upload, local backup files are removed to save disk space
4. If the upload fails, local backups are preserved

##### Prerequisites

- Rclone must be installed on the target machine
- Rclone remote must be configured outside of this role (using `rclone config`)

##### Backup and Retention Process

When rclone is enabled:
- Local backups are created for all databases
- All backups are synchronized to the remote destination
- Local files are deleted after successful upload
- Retention policies are handled by the remote storage

When rclone is disabled:
- Local backups are created for all databases
- A separate pruning process removes backups older than the configured retention period

##### Example Rclone Backup Configuration

```yaml
# Enable backups with rclone remote storage
postgres_backup_enabled: true
postgres_backup_dir: "/opt/backups/postgres"
postgres_backup_format: "custom"
postgres_backup_rclone_enabled: true
postgres_backup_rclone_remote: "s3:my-postgres-backups/dailies"
postgres_backup_rclone_args: "--s3-storage-class=STANDARD_IA --progress"
```

##### Restoring from Rclone Backups

To restore a database from a remote backup:

1. Download the backup file from the remote storage:
   ```
   rclone copy <remote>:<path-to-backup> /local/path/
   ```

2. Restore using the appropriate pg_restore command:
   ```
   # For custom format
   pg_restore -h localhost -p 5432 -U postgres -d dbname /local/path/filename.dump

   # For plain SQL
   psql -h localhost -p 5432 -U postgres -d dbname -f /local/path/filename.sql
   ```

## Example Playbook

```yaml
- hosts: postgres_servers
  vars:
    postgres_version: "17.4"
    postgres_root_password: "supersecurepassword"
    postgres_max_connections: 200
    postgres_shared_buffers: "512MB"
    postgres_custom_conf:
      max_worker_processes: 8
      work_mem: "8MB"

    # Database and user creation
    postgres_databases:
      - name: myapp_db
        owner: myapp_user
        encoding: UTF8
      - name: analytics_db

    postgres_users:
      - name: myapp_user
        password: "app_password"
        roles: ["CREATEDB", "LOGIN"]
        privileges:
          - database: myapp_db
            schema: public
            type: ALL
            privileges: ALL
      - name: readonly_user
        password: "read_password"
        privileges:
          - database: myapp_db
            schema: public
            type: TABLE
            privileges: SELECT

    # Enable pg_dump backups
    postgres_backup_enabled: true
    postgres_backup_dir: "/opt/backups/postgres"
    postgres_backup_keep_days: 14
    postgres_backup_hour: "03"
    postgres_backup_minute: "30"
    postgres_backup_prune_enabled: true

    # Enable rclone remote backups (optional)
    postgres_backup_rclone_enabled: true
    postgres_backup_rclone_remote: "remote:postgres_backups"
    postgres_backup_rclone_args: "--progress"

  roles:
    - brpaz.swarm_postgres
```

## Role Dependencies

- [community.docker](https://docs.ansible.com/ansible/latest/collections/community/docker/index.html) collection
- [community.postgresql](https://docs.ansible.com/ansible/latest/collections/community/postgresql/index.html) collection

## Contribute

All contributions are welcome. Please check [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 🫶 Support

If you find this project helpful and would like to support its development, there are a few ways you can contribute:

[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-%23db61a2.svg?&logo=github&logoColor=red&&style=for-the-badge&labelColor=white)](https://github.com/sponsors/brpaz)

<a href="https://www.buymeacoffee.com/Z1Bu6asGV" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

## License

This project is MIT Licensed [LICENSE](LICENSE)

## 📩 Contact

✉️ **Email** - [oss@brunopaz.dev](oss@brunopaz.dev)

🖇️ **Source code**: [https://github.com/brpaz/ansible-role-swarm-postgres](https://github.com/brpaz/ansible-role-swarm-postgres)
