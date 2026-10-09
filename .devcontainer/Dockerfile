FROM archlinux:latest

# The container user mirrors the host user (name, uid, home) so that every
# host path -- Steam library, Paradox user data, this workspace -- is mounted
# at the SAME absolute path inside. Playsets and .mod descriptors hold host
# paths; keeping them identical means a patch mod built in here loads the same
# way in the host-side launcher.
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=1000

# Base toolchain.
#   base-devel/git/github-cli  build + VCS
#   nodejs/npm                 VS Code extensions, Claude Code fallback install
#   sqlite                     inspect launcher-v2.sqlite (mod registry + playsets)
#   librsvg                    rsvg-convert: render data/patch-icon.svg to thumbnail.png
RUN pacman -Syu --noconfirm --needed \
        base-devel \
        git \
        github-cli \
        openssh \
        sudo \
        which \
        less \
        file \
        zip \
        unzip \
        ripgrep \
        jq \
        sqlite \
        fish \
        nodejs \
        npm \
        python \
        librsvg \
    && pacman -Scc --noconfirm

# Application stack: Python, all from Arch's official repos -- no venv, no pip.
#   Runtime:
#     python-msgspec         typed structs, JSON and msgpack
#     python-xxhash          fast content hashing for change detection
#   Dev only:
#     python-pytest          tests
#     ruff                   lint + format
#     mypy                   type checking
# -Syu, not -S: the layer above may come from the build cache with an old
# package database, and mirrors drop old package versions (404 on download).
RUN pacman -Syu --noconfirm --needed \
        python-msgspec \
        python-xxhash \
        python-pytest \
        ruff \
        mypy \
    && pacman -Scc --noconfirm

RUN groupadd --gid "${USER_GID}" "${USERNAME}" \
    && useradd --uid "${USER_UID}" --gid "${USER_GID}" --create-home --shell /bin/bash "${USERNAME}" \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${USERNAME}" \
    && chmod 0440 "/etc/sudoers.d/${USERNAME}"

# Mount points for binds that land inside $HOME. Created up front so ownership
# is the user's, not root's.
RUN mkdir -p \
        "/home/${USERNAME}/.claude" \
        "/home/${USERNAME}/.config/gh" \
        "/home/${USERNAME}/.local/share/Steam" \
        "/home/${USERNAME}/.local/share/Paradox Interactive" \
        "/home/${USERNAME}/.local/share/cold-steel" \
        "/home/${USERNAME}/.local/share/stellaris-patcher" \
        "/home/${USERNAME}/.config/cold-steel" \
    && chown -R "${USER_UID}:${USER_GID}" "/home/${USERNAME}"

USER ${USERNAME}
