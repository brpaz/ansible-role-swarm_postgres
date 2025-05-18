import testinfra


def test_postgres_service_running(host):
    cmd = host.run(
        "docker service ls --filter name=postgres --format '{{.Name}} {{.Replicas}}'"
    )
    assert cmd.rc == 0
    assert "postgres" in cmd.stdout
    assert "1/1" in cmd.stdout


def test_postgres_container_healthy(host):
    cmd = host.run("docker ps --filter name=postgres --format '{{.Names}}'")
    assert cmd.rc == 0
    container_name = cmd.stdout.strip()
    assert container_name != ""

    inspect = host.run(
        f"docker inspect --format='{{{{.State.Health.Status}}}}' {container_name}"
    )

    assert inspect.stdout.strip() == "healthy"


def test_postgres_is_listening(host):
    """Test if Postgres is listening on the expected ports."""
    assert host.socket("tcp://127.0.0.1:5432").is_listening
