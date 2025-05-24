# Ansible Docker Swarm PostgreSQL Role

> An Ansible role to deploy a PostgreSQL service to a Docker Swarm cluster with support for user management, database creation, pg_dump backups with rclone remote storage, and WAL-G continuous archiving with S3/Backblaze B2 for point-in-time recovery.

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

#### WAL-G Backup Settings

The role uses a custom PostgreSQL Docker image that includes WAL-G, a tool that provides continuous archiving of PostgreSQL WAL (Write-Ahead Logging) files and base backups.

| Variable                                   | Default Value    | Description                                          |
| ------------------------------------------ | ---------------- | ---------------------------------------------------- |
| `postgres_walg_enabled`                    | `false`          | Whether to enable WAL-G backups                      |
| `postgres_walg_s3_prefix`                  | ``               | S3 prefix URL (s3://bucket/path)                     |
| `postgres_walg_compression_method`         | `lz4`            | Compression method (lz4, brotli, zstd, none)         |
| `postgres_walg_compression_level`          | `3`              | Compression level                                    |
| `postgres_walg_base_backup_timer_schedule` | `*-*-* 01:00:00` | When to take full backups (systemd calendar format)  |
| `postgres_walg_retention_timer_schedule`   | `*-*-* 01:30:00` | When to run retention jobs (systemd calendar format) |
| `postgres_walg_backup_retention_count`     | `5`              | How many backups to keep                             |

##### S3 Storage Configuration

| Variable                              | Default Value | Description                                         |
| ------------------------------------- | ------------- | --------------------------------------------------- |
| `postgres_walg_aws_access_key_id`     | ``            | AWS access key ID                                   |
| `postgres_walg_aws_secret_access_key` | ``            | AWS secret access key                               |
| `postgres_walg_aws_region`            | ``            | AWS region                                          |
| `postgres_walg_aws_endpoint`          | ``            | S3-compatible endpoint URL (for Backblaze B2, etc.) |

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

#### Continuous Archiving with WAL-G

WAL-G provides continuous archiving of PostgreSQL's Write-Ahead Log (WAL) files in addition to performing full backups. This enables point-in-time recovery (PITR) capabilities.

##### How WAL-G Backups Work

1. **WAL Archiving**: When `postgres_wal_enabled` is set to `true`, PostgreSQL is configured to archive WAL files using WAL-G.
2. **Base Backups**: WAL-G performs full backups according to the schedule defined in `postgres_walg_base_backup_timer_schedule`.
3. **Continuous Backup**: Between full backups, WAL files are continuously archived, allowing for point-in-time recovery.
4. **Retention Policies**: Old backups are automatically removed based on retention settings. The retention service uses both count-based (`postgres_walg_backup_retention_count`)
##### Prerequisites for WAL-G

- PostgreSQL configuration with WAL archiving enabled (`postgres_wal_enabled: true`)
- Appropriate storage configuration (S3, Azure, GCS, or filesystem)
- Access credentials for the chosen storage provider

##### Example WAL-G Configuration with S3

```yaml
# Enable WAL-G backups with S3 storage
postgres_wal_enabled: true
postgres_archive_mode: "on"
postgres_archive_command: "wal-g wal-push %p"
postgres_walg_enabled: true
postgres_walg_s3_prefix: "s3://my-pg-backups/postgres"
postgres_walg_aws_access_key_id: "YOUR_ACCESS_KEY"
postgres_walg_aws_secret_access_key: "YOUR_SECRET_KEY"
postgres_walg_aws_region: "us-east-1"
postgres_walg_base_backup_timer_schedule: "*-*-* 01:00:00"  # Daily at 1 AM (systemd calendar format)
postgres_walg_retention_timer_schedule: "*-*-* 01:30:00"  # Daily at 1:30 AM (systemd calendar format)
postgres_walg_backup_retention_count: 10
```

##### Example WAL-G Configuration with Backblaze B2

```yaml
# Enable WAL-G backups with Backblaze B2 storage
postgres_wal_enabled: true
postgres_archive_mode: "on"
postgres_archive_command: "wal-g wal-push %p"
postgres_walg_enabled: true
postgres_walg_s3_prefix: "s3://my-bucket/postgres-backups"
postgres_walg_aws_access_key_id: "YOUR_BACKBLAZE_KEY_ID"
postgres_walg_aws_secret_access_key: "YOUR_BACKBLAZE_APPLICATION_KEY"
postgres_walg_aws_region: "us-west-001"
postgres_walg_aws_endpoint: "https://s3.us-west-001.backblazeb2.com"
postgres_walg_base_backup_timer_schedule: "*-*-* 01:00:00"  # Daily at 1 AM (systemd calendar format)
postgres_walg_retention_timer_schedule: "*-*-* 01:30:00"  # Daily at 1:30 AM (systemd calendar format)
postgres_walg_backup_retention_count: 7
```

##### Restoring from WAL-G Backups

The role installs a restore script at `/usr/local/bin/walg-restore.sh` that can be used to restore a database from WAL-G backups.

To restore the latest backup:
```bash
sudo /usr/local/bin/walg-restore.sh --latest
```

To restore a specific backup:
```bash
sudo /usr/local/bin/walg-restore.sh --backup-name base_000000010000000000000007
```

To restore to a specific point in time:
```bash
sudo /usr/local/bin/walg-restore.sh --target-time "2023-06-15 14:30:00"
```

To perform a dry run without actually executing the restore:
```bash
sudo /usr/local/bin/walg-restore.sh --dry-run --latest
```

##### Monitoring WAL-G Backups

The role installs a monitoring script at `/usr/local/bin/walg-monitor.sh` that can be used to check the status and health of your WAL-G backups.

To list all backups:
```bash
sudo /usr/local/bin/walg-monitor.sh --list
```

To show detailed information about backups:
```bash
sudo /usr/local/bin/walg-monitor.sh --detail
```

To check backup status and health:
```bash
sudo /usr/local/bin/walg-monitor.sh --status
```

This monitoring script can be integrated with your monitoring systems like [NTFY](https://ntfy.sh) to ensure your backups are being executed correctly.

##### WAL-G Backup Retention Management

The role implements a dual retention policy system that ensures your backups are managed efficiently:

1. **Count-based retention**: Keeps a fixed number of the most recent backups (`postgres_walg_backup_retention_count`)

The role installs a dedicated retention script at `/usr/local/bin/walg-retention.sh` that handles backup cleanup. The script:

- Applies both retention policies independently (count-based and time-based)
- Provides detailed logging of the retention process
- Continues execution even if one retention policy fails
- Shows a summary of remaining backups after cleanup

The retention service runs on a schedule defined by `postgres_walg_retention_timer_schedule` (default: daily at 1:30 AM) and includes:

- **Resilient execution**: If one retention policy fails, the other will still be applied
- **Error handling**: Failures are logged but won't prevent the service from functioning
- **Auto-recovery**: Includes restart capabilities to handle temporary failures
- **Timeout protection**: Prevents hanging operations with a configurable timeout

You can manually trigger the retention process by running:
```bash
sudo systemctl start walg-retention.service
```

Or run the script directly:
```bash
sudo /usr/local/bin/walg-retention.sh
```

To see the retention status and logs:
```bash
sudo journalctl -u walg-retention.service -n 50
```
````
