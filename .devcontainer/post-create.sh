#!/usr/bin/env bash
# Runs once when the container is created or rebuilt.
set -euo pipefail

say() { printf '\n\033[1;36m==> %s\033[0m\n' "$1"; }
ok()  { printf '    \033[32m✓\033[0m %s\n' "$1"; }
bad() { printf '    \033[31m✗\033[0m %s\n' "$1"; }
warn(){ printf '    \033[33m!\033[0m %s\n' "$1"; }

say "Installing Claude Code CLI"
if command -v claude >/dev/null 2>&1; then
	ok "already present: $(claude --version 2>/dev/null || echo unknown)"
elif curl -fsSL https://claude.ai/install.sh | bash >/dev/null 2>&1 \
	|| sudo npm install -g @anthropic-ai/claude-code >/dev/null 2>&1; then
	export PATH="$HOME/.local/bin:$PATH"
	ok "installed $(claude --version 2>/dev/null || echo '')"
else
	bad "install failed — run: curl -fsSL https://claude.ai/install.sh | bash"
fi

say "GitHub CLI"
if gh auth status >/dev/null 2>&1; then
	gh auth setup-git >/dev/null 2>&1 || true
	ok "authenticated as $(gh api user --jq .login 2>/dev/null || echo '?')"
else
	warn "not logged in — run: gh auth login && gh auth setup-git"
fi

say "Git identity"
# The host's ~/.gitconfig is mounted at ~/.gitconfig-host (see devcontainer.json).
# Include it, so commits use the host's name and email. Added once only.
if [ -r "$HOME/.gitconfig-host" ]; then
	git config --global --get-all include.path | grep -qx '~/.gitconfig-host' \
		|| git config --global --add include.path '~/.gitconfig-host'
fi
if name=$(git config user.name) && git config user.email >/dev/null; then
	ok "commits as $name"
else
	bad "no user.name or user.email — on the host run: git config --global user.name/user.email, then rebuild"
fi

say "Backing up launcher databases (once)"
# launcher-v2.sqlite holds the launcher's playsets. We work through Cold Steel
# and don't write it (decision 11), but keep a pristine copy anyway (decision 6);
# never overwritten on later rebuilds.
shopt -s nullglob
found=0
for db in "${PARADOX_DATA_DIR}"/*/launcher-v2.sqlite; do
	found=1
	bak="${db%.sqlite}.stellaris-patcher-orig.sqlite"
	if [ -e "$bak" ]; then
		ok "kept    ${bak#${PARADOX_DATA_DIR}/}"
	else
		cp -p "$db" "$bak" && ok "created ${bak#${PARADOX_DATA_DIR}/}"
	fi
done
[ "$found" = 1 ] || warn "no launcher-v2.sqlite under ${PARADOX_DATA_DIR}"

say "Backing up Cold Steel's data (once)"
# We write Cold Steel's playsets and conflict choices. Keep a copy from before
# this project ever touched them; never overwritten on later rebuilds.
cs_data="$HOME/.local/share/cold-steel"
cs_orig="$HOME/.local/share/stellaris-patcher/backups/cold-steel-orig.tar.gz"
if [ -e "$cs_orig" ]; then
	ok "kept    ${cs_orig#$HOME/}"
elif [ -e "$cs_data/playsets.json" ]; then
	mkdir -p "$(dirname "$cs_orig")"
	parts=(playsets.json)
	[ -d "$cs_data/resolutions" ] && parts+=(resolutions)
	tar -czf "$cs_orig" -C "$cs_data" "${parts[@]}" && ok "created ${cs_orig#$HOME/}"
else
	warn "no Cold Steel playsets yet at $cs_data — run Cold Steel once on the host"
fi

say "Verifying mounts"
vdf="${STEAM_DIR}/steamapps/libraryfolders.vdf"
if [ -r "$vdf" ]; then
	ok "steam library   ${STEAM_DIR}  ($(grep -c '"path"' "$vdf") library folder(s))"
else
	bad "steam library missing at ${STEAM_DIR}"
fi

if [ -w "${PARADOX_DATA_DIR}" ]; then
	games=$(find "${PARADOX_DATA_DIR}" -mindepth 1 -maxdepth 1 -type d ! -name 'launcher-v2' -printf '%f ' 2>/dev/null)
	ok "paradox data    writable  (games: ${games:-none})"
else
	bad "paradox data dir ${PARADOX_DATA_DIR} not writable"
fi

if [ -w "$cs_data" ]; then
	ok "cold steel data ${cs_data}  (writable)"
else
	bad "cold steel data not mounted writable at ${cs_data}"
fi

if [ -w "$HOME/.local/share/stellaris-patcher" ]; then
	ok "our data        $HOME/.local/share/stellaris-patcher  (persisted)"
else
	bad "our data folder not mounted at $HOME/.local/share/stellaris-patcher"
fi

if [ -d "${CLAUDE_CONFIG_DIR}" ]; then
	ok "claude state    ${CLAUDE_CONFIG_DIR}  (persisted)"
else
	bad "claude state dir missing at ${CLAUDE_CONFIG_DIR}"
fi

say "Verifying toolchain"
for tool in git gh python3 node sqlite3 rsvg-convert rg jq ruff mypy pytest; do
	if command -v "$tool" >/dev/null 2>&1; then
		ok "$(printf '%-8s' "$tool") $("$tool" --version 2>/dev/null | head -1)"
	else
		bad "$tool missing"
	fi
done
for mod in msgspec xxhash; do
	if ver=$(python3 -c "import $mod as m; print(getattr(m, '__version__', 'ok'))" 2>/dev/null); then
		ok "$(printf '%-16s' "$mod") $ver"
	else
		bad "python module $mod missing"
	fi
done

printf '\n\033[1;32mReady.\033[0m\n\n'
