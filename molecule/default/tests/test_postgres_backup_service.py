import testinfra


def test_backup_script_exists(host):
    """Test if the backup script exists."""
    backup_script = host.file("/usr/local/bin/pg-backup.sh")
    assert backup_script.exists
    assert backup_script.is_file
    assert backup_script.user == "root"
    assert backup_script.group == "root"
    assert backup_script.mode == 0o700
    ""


def test_backup_directory_exists(host):
    """Test if the backup directory exists."""
    backup_dir = host.file("/var/lib/postgresql/backups")
    assert backup_dir.exists
    assert backup_dir.is_directory
    assert backup_dir.user == "root"
    assert backup_dir.group == "root"
    assert backup_dir.mode == 0o700


def test_backup_unit_exists(host):
    """Test if the backup systemd unit exists."""
    backup_unit = host.file("/etc/systemd/system/postgres-backup.service")
    assert backup_unit.exists
    assert backup_unit.is_file
    assert backup_unit.user == "root"
    assert backup_unit.group == "root"
    assert backup_unit.mode == 0o644


def test_backup_timer_exists(host):
    """Test if the backup timer exists."""
    backup_timer = host.file("/etc/systemd/system/postgres-backup.timer")
    assert backup_timer.exists
    assert backup_timer.is_file
    assert backup_timer.user == "root"
    assert backup_timer.group == "root"
    assert backup_timer.mode == 0o644


def test_backup_timer_enabled(host):
    """Test if the backup timer is enabled."""
    backup_timer = host.run("systemctl is-enabled postgres-backup.timer")
    assert backup_timer.rc == 0
    assert "enabled" in backup_timer.stdout
