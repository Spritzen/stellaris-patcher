# The image the check workflow runs in, built weekly by .github/workflows/ci-image.yml
# (decision 38). The packages are what `make check` needs: keep them in step with
# .devcontainer/Dockerfile.

ARG BASE=archlinux:latest
FROM ${BASE}

# Links the image to the repo, so the repo's workflows can pull it with their own token.
LABEL org.opencontainers.image.source=https://github.com/Spritzen/stellaris-patcher

RUN pacman -Syu --noconfirm --needed \
        git make python \
        python-msgspec python-xxhash \
        python-pytest ruff mypy \
    && pacman -Scc --noconfirm
