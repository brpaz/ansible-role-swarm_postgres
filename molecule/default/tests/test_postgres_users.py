import testinfra


def get_postgres_container_name(host):
    """Get the name of the Postgres container."""
    cmd = host.run("docker ps --filter name=postgres --format '{{.Names}}'")
    assert cmd.rc == 0
    container_name = cmd.stdout.strip()
    assert container_name != ""
    return container_name


def test_postgres_database_exists(host):
    """Test if the Postgres database exists."""
    container_name = get_postgres_container_name(host)

    cmd = host.run(
        f"docker exec {container_name} psql -U postgres -c '\\l' | grep test_db"
    )

    assert cmd.rc == 0
    assert "test_db" in cmd.stdout


def test_postgres_user_exists(host):
    """Test if the Postgres user exists."""
    container_name = get_postgres_container_name(host)
    cmd = host.run(
        f'docker exec {container_name} psql -U postgres -c "SELECT usename FROM pg_user;"'
    )
    assert cmd.rc == 0
    assert "app_user" in cmd.stdout


def test_user_can_connect(host):
    """Test if the Postgres user can connect to the database."""
    container_name = get_postgres_container_name(host)
    cmd = host.run(
        f'docker exec -e PGPASSWORD=test {container_name} psql -U app_user -d test_db -c "SELECT 1;"'
    )
    assert cmd.rc == 0
    assert "1" in cmd.stdout
