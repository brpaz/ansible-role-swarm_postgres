# Contributing to ansible-role-swarm-postgres

First off, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to this Ansible role. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents

- [Contributing to ansible-role-swarm-postgres](#contributing-to-ansible-role-swarm-postgres)
  - [Table of Contents](#table-of-contents)
  - [Development Environment Setup](#development-environment-setup)
    - [Prerequisites](#prerequisites)
    - [Setting Up with Nix, devenv, and direnv](#setting-up-with-nix-devenv-and-direnv)
    - [Alternative Setup](#alternative-setup)
  - [Development Workflow](#development-workflow)
    - [GitHub Flow](#github-flow)
    - [Pull Request Process](#pull-request-process)
  - [Code Style and Standards](#code-style-and-standards)
  - [Running Tests](#running-tests)
  - [Release Process](#release-process)
    - [Release Drafter](#release-drafter)
  - [Thank You!](#thank-you)

## Development Environment Setup

### Prerequisites

To contribute to this project, you'll need:

- [Git](https://git-scm.com/)
- [Nix package manager](https://nixos.org/download.html)
- [direnv](https://direnv.net/docs/installation.html)
- [devenv](https://devenv.sh/getting-started/)

### Setting Up with Nix, devenv, and direnv

1. Clone the repository:
   ```bash
   git clone https://github.com/brpaz/ansible-role-swarm.git
   cd ansible-role-swarm
   ```

2. Setup direnv:

   The project includes a `.envrc` file that direnv uses to automatically activate the dev environment. When you enter the directory, direnv will prompt you to allow the `.envrc` file:

   ```bash
   direnv allow
   ```

   This will initiate the environment setup using Nix and devenv.

3. First-time initialization:

   If this is your first time setting up a Nix development environment, it might take a few minutes as Nix downloads and builds the required packages.

4. Verify the setup:

   Once the environment is ready, you should have access to all the development tools. You can verify with:

   ```bash
   ansible --version
   molecule --version
   ```

### Alternative Setup

If you prefer not to use Nix and devenv, you can manually install the required dependencies:

1. Install dependencies:
   ```bash
   pip install ansible ansible-lint molecule molecule-docker pytest-testinfra
   ```

2. Install Docker (required for Molecule tests)

3. Install Task runner:
   ```bash
   # On macOS
   brew install go-task

   # On Linux
   sh -c "$(curl -ssL https://taskfile.dev/install.sh)" -- -d -b ~/.local/bin
   ```

## Development Workflow

We follow the GitHub Flow branching model for development.

### GitHub Flow

1. **Create a branch**: Branch from `main` using a descriptive name:
   ```bash
   git checkout -b feature/new-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make changes**: Implement your changes, following the project's code style.

3. **Commit your changes**: Use descriptive commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) standard:
   ```bash
   git commit -m "feat: add support for feature X"
   git commit -m "fix: resolve issue with Y"
   ```

4. **Push your branch**: Upload your branch to GitHub:
   ```bash
   git push -u origin feature/new-feature
   ```

5. **Open a Pull Request**: Create a PR against the `main` branch.

6. **Address feedback**: Make any necessary changes based on code review.

7. **Merge**: Once approved, your PR will be merged into `main`.

### Pull Request Process

1. Ensure your code meets the project's style guidelines and passes all tests.
2. Update documentation if necessary.
3. Include tests for new functionality.
4. Update the README.md with details of changes if applicable.
5. The PR will be merged once you have the sign-off of at least one maintainer.

## Code Style and Standards

This project follows Ansible best practices:

- Use YAML files with `.yml` extension
- Use 2 spaces for indentation
- Follow naming conventions in the [Ansible Style Guide](https://docs.ansible.com/ansible/latest/dev_guide/style_guide/index.html)
- Run linting checks before submitting: `task lint`

## Running Tests

We use Molecule for testing the role. To run the tests:

```bash
# Run the complete test sequence
task test

# Run only the lint check
task lint
```

## Release Process

We use Semantic Versioning for releases.

### Release Drafter

This project uses [Release Drafter](https://github.com/release-drafter/release-drafter) to automatically draft release notes based on merged pull requests.

1. Pull requests are automatically categorized based on their labels and commit messages.
2. When PRs are merged to the `main` branch, Release Drafter updates the draft release.
3. When ready to create a new release, the maintainer will:
   - Review and edit the draft release notes
   - Set the appropriate version number
   - Publish the release

The version is determined by the labels applied to the PRs merged since the last release:
- `breaking`: Major version bump
- `feature` or `enhancement`: Minor version bump
- `bug` or `fix`: Patch version bump

## Thank You!

Your contributions are appreciated and help make this project better for everyone!
